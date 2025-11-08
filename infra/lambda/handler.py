import json # for JSON data
import os # for environment variables
from datetime import datetime
import pytz # for timezone
import boto3 # for SNS publishing
import requests # for external API calls


# --- Configuration ---
# Base URL confirmed from your request samples
API_BASE_URL = "https://v3.football.api-sports.io/fixtures"
API_HOST = "v3.football.api-sports.io" # <--- NEW: Host header value

# We use hardcoded IDs for Aston Villa (33) and Birmingham City (36)
TARGET_TEAM_IDS = [66, 54] 
TIMEZONE = "Europe/London"

def fetch_and_filter_fixtures(api_key):
    """Fetches fixtures for today and filters for relevant matches."""
    
    # Get today's date in YYYY-MM-DD format as required by the 'date' parameter
    local_tz = pytz.timezone(TIMEZONE)
    today_date = datetime.now(pytz.utc).astimezone(local_tz).strftime("%Y-%m-%d")
    
    # API-Football V3 requires BOTH the key and the host in the headers
    headers = { 
        "x-rapidapi-key": api_key,      # <--- KEY
        "x-rapidapi-host": API_HOST     # <--- NEW: HOST
    }
    
    # Use the 'date' and 'timezone' query parameters for the API call
    params = {
        "date": today_date,
        "timezone": TIMEZONE
    }
    
    try:
        # Perform the actual authenticated request to the API-Football fixtures endpoint
        response = requests.get(API_BASE_URL, headers=headers, params=params)
        
        # Check for HTTP errors (4xx or 5xx) and raise an exception if found
        response.raise_for_status() 
        
        # If successful, parse the JSON response
        data = response.json()
    
    except requests.RequestException as e:
        # Handle all network-related and HTTP status code errors
        print(f"ERROR: API request failed: {e}")
        # Return an empty list so the Lambda handler does not try to process bad data
        return []

    # Alerts list starts here if the API call was successful
    alerts = []
    total_fixtures = len(data.get("response", []))
    print(f"Processing {total_fixtures} fixtures for today")
    print(f"Target team IDs: {TARGET_TEAM_IDS}")

    for fixture_data in data.get("response", []):
        fixture = fixture_data.get("fixture", {})
        teams = fixture_data.get("teams", {})
        venue_info = fixture.get("venue", {})
        
        # Check if the fixture involves one of our target teams (by ID)
        # Convert to int to handle cases where API returns IDs as strings
        home_id = teams.get("home", {}).get("id")
        away_id = teams.get("away", {}).get("id")
        home_team_name = teams.get("home", {}).get("name", "Unknown Home Team")
        away_team_name = teams.get("away", {}).get("name", "Unknown Away Team")
        
        # Convert IDs to integers for proper comparison (handles string IDs from API)
        try:
            home_id = int(home_id) if home_id is not None else None
            away_id = int(away_id) if away_id is not None else None
        except (ValueError, TypeError):
            # Skip this fixture if IDs can't be converted
            print(f"WARNING: Could not parse team IDs - {home_team_name} (home: {home_id}), {away_team_name} (away: {away_id})")
            continue

        # Log ALL fixtures for debugging
        print(f"Checking: {home_team_name} (ID: {home_id}) vs {away_team_name} (ID: {away_id})")
        
        # Only alert if one of the teams is in our target list
        # This ensures we only get alerts for matches involving our target teams
        is_target_match = (home_id is not None and home_id in TARGET_TEAM_IDS) or (away_id is not None and away_id in TARGET_TEAM_IDS)
        
        if is_target_match:
            # Debug logging to verify filtering is working correctly
            print(f"MATCH FOUND: {home_team_name} (ID: {home_id}) vs {away_team_name} (ID: {away_id})")
            print(f"   home_id {home_id} in targets? {home_id in TARGET_TEAM_IDS if home_id else False}")
            print(f"   away_id {away_id} in targets? {away_id in TARGET_TEAM_IDS if away_id else False}")
            
            # --- Filtering Logic ---
            # NOTE: We alert on ANY match involving target teams today, 
            # assuming it's local traffic relevant for Birmingham.
            venue_name = venue_info.get("name", "Unknown Venue")
            
            # Extract time and format it
            match_datetime_str = fixture.get("date") # This is an ISO format string
            try:
                # Convert the ISO string to a datetime object, localize, and format
                # The .replace('Z', '+00:00') handles the API's ISO format reliably
                match_dt = datetime.fromisoformat(match_datetime_str.replace('Z', '+00:00'))
                kickoff_time = match_dt.astimezone(local_tz).strftime("%I:%M %p")
            except Exception:
                kickoff_time = "Time TBD"


            message = (
                f"MATCH DAY ALERT: {home_team_name} vs {away_team_name} at {venue_name}. "
                f"Kickoff: {kickoff_time} ({TIMEZONE}). Expect local traffic."
            )
            alerts.append(message)
        else:
            # Log fixtures that were filtered out
            print(f"FILTERED OUT: {home_team_name} (ID: {home_id}) vs {away_team_name} (ID: {away_id}) - neither team in target list")

    print(f"Summary: {len(alerts)} alert(s) created from {total_fixtures} total fixture(s)")
    return alerts # <--- This is the last line of fetch_and_filter_fixtures


def lambda_handler(event, context):
    """Entry point: fetches fixtures and sends SNS alerts for home games."""

    # Clients
    sns_client = boto3.client("sns", region_name=os.getenv("AWS_REGION", "eu-west-2"))

    # 1. Load configuration safely inside the handler function
    api_key = os.environ.get("api_key")
    topic_arn = os.environ.get("TOPIC_ARN") # Renamed to topic_arn (lowercase) for local use
    
    if not api_key or not topic_arn:
        print("ERROR: Missing api_key or TOPIC_ARN environment variable.")
        return {"statusCode": 500, "body": "Configuration error."}

    # 2. Call the fetch function, passing the securely loaded key
    alerts = fetch_and_filter_fixtures(api_key)
    
    if not alerts:
        print("SUCCESS: No relevant home matches scheduled today.")
        return {"statusCode": 200, "body": "No relevant home matches scheduled today."}

    # 3. Send SMS alerts
    published_ids = []
    for message in alerts:
        response = sns_client.publish(
            TopicArn=topic_arn, # Use the locally loaded variable
            Message=message,
            Subject="Football Traffic Alert",
            MessageAttributes={
                "AWS.SNS.SMS.SenderID": {"DataType": "String", "StringValue": "FOOTBALL"}
            }
        )
        published_ids.append(response.get('MessageId'))

    return {
        "statusCode": 200,
        "body": f"Published {len(alerts)} alert(s). IDs: {', '.join(published_ids)}"
    }