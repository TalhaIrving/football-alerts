import json # for JSON data
import os # for environment variables
from datetime import datetime, timezone # for date and time
import boto3 # for SNS publishing
import requests # for external API calls


# --- Configuration ---
# Base URL confirmed from your request samples
API_BASE_URL = "https://v3.football.api-sports.io/fixtures"
API_HOST = "v3.football.api-sports.io" # <--- NEW: Host header value

# We use hardcoded IDs for Aston Villa (33) and Birmingham City (36)
TARGET_TEAM_IDS = [33, 36] 
TIMEZONE = "Europe/London"

# Clients
SNS_CLIENT = boto3.client("sns", region_name=os.getenv("AWS_REGION", "eu-west-2"))

def fetch_and_filter_fixtures(api_key):
    """Fetches fixtures for today and filters for relevant matches."""
    
    # Get today's date in YYYY-MM-DD format as required by the 'date' parameter
    today_date = datetime.now(timezone.utc).astimezone(timezone(TIMEZONE)).strftime("%Y-%m-%d")
    
    # API-Football V3 requires BOTH the key and the host in the headers
    headers = { 
        "x-rapidapi-key": API_KEY,      # <--- KEY
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

    for fixture_data in data.get("response", []):
        fixture = fixture_data.get("fixture", {})
        teams = fixture_data.get("teams", {})
        venue_info = fixture.get("venue", {})
        
        # Check if the fixture involves one of our target teams (by ID)
        home_id = teams.get("home", {}).get("id")
        away_id = teams.get("away", {}).get("id")

        if home_id in TARGET_TEAM_IDS or away_id in TARGET_TEAM_IDS:
            
            # --- Filtering Logic ---
            # NOTE: We alert on ANY match involving target teams today, 
            # assuming it's local traffic relevant for Birmingham.
            
            home_team_name = teams.get("home", {}).get("name", "Unknown Home Team")
            away_team_name = teams.get("away", {}).get("name", "Unknown Away Team")
            venue_name = venue_info.get("name", "Unknown Venue")
            
            # Extract time and format it
            match_datetime_str = fixture.get("date") # This is an ISO format string
            try:
                # Convert the ISO string to a datetime object, localize, and format
                # The .replace('Z', '+00:00') handles the API's ISO format reliably
                match_dt = datetime.fromisoformat(match_datetime_str.replace('Z', '+00:00'))
                kickoff_time = match_dt.astimezone(timezone(TIMEZONE)).strftime("%I:%M %p")
            except Exception:
                kickoff_time = "Time TBD"


            message = (
                f"MATCH DAY ALERT: {home_team_name} vs {away_team_name} at {venue_name}. "
                f"Kickoff: {kickoff_time} ({TIMEZONE}). Expect local traffic."
            )
            alerts.append(message)

    return alerts # <--- This is the last line of fetch_and_filter_fixtures


def lambda_handler(event, context):
    """Entry point: fetches fixtures and sends SNS alerts for home games."""
    
    # 1. Load configuration safely inside the handler function
    api_key = os.environ.get("API_KEY")
    topic_arn = os.environ.get("TOPIC_ARN") # Renamed to topic_arn (lowercase) for local use
    
    if not api_key or not topic_arn:
        print("ERROR: Missing API_KEY or TOPIC_ARN environment variable.")
        return {"statusCode": 500, "body": "Configuration error."}

    # 2. Call the fetch function, passing the securely loaded key
    alerts = fetch_and_filter_fixtures(api_key)
    
    if not alerts:
        print("SUCCESS: No relevant home matches scheduled today.")
        return {"statusCode": 200, "body": "No relevant home matches scheduled today."}

    # 3. Send SMS alerts
    published_ids = []
    for message in alerts:
        response = SNS_CLIENT.publish(
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