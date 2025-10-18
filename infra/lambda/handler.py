import json # for JSON data
import os # for environment variables
from datetime import datetime, timezone # for date and time
import boto3 # for SNS publishing
import requests # for external API calls


# Configuration
API_ENDPOINT = "https://api-football-fixtures.com/v1/fixtures" # Example endpoint, replace if needed
API_KEY = os.environ.get("API_KEY")
TOPIC_ARN = os.environ.get("TOPIC_ARN")
TEAMS = ["Aston Villa", "Birmingham City"]
HOME_STADIUMS = ["Villa Park", "St Andrew's Trillion Trophy Stadium"]

# Clients
SNS_CLIENT = boto3.client("sns", region_name=os.getenv("AWS_REGION", "eu-west-2"))

def fetch_and_filter_fixtures():
    """Fetches fixtures for today and filters for relevant home games."""
    today_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    headers = {"Authorization": API_KEY, "Date": today_date}
    
    try:
        # ⚠️ NOTE: This URL/API key must match the service you use.
        response = requests.get(f"{API_ENDPOINT}?date={today_date}", headers=headers)
        response.raise_for_status() # Raise exception for 4xx or 5xx status codes
        data = response.json()
    except requests.RequestException as e:
        print(f"ERROR: API request failed: {e}")
        return []

    alerts = []
    
    # Assuming 'data' contains a list of fixtures
    for fixture in data.get("fixtures", []):
        home_team = fixture.get("home_team", {}).get("name")
        away_team = fixture.get("away_team", {}).get("name")
        venue = fixture.get("venue", {}).get("name")
        match_time = fixture.get("time") # Format this based on your API

        # Filter 1: Must be a game involving one of your teams
        if home_team in TEAMS or away_team in TEAMS:
            
            # Filter 2: Must be played at a local stadium (Home game)
            if venue in HOME_STADIUMS:
                
                # Format the alert message
                message = (
                    f"MATCH DAY ALERT: {home_team} vs {away_team} at {venue} today. "
                    f"Kickoff: {match_time} UTC. Expect heavy traffic."
                )
                alerts.append(message)

    return alerts


def lambda_handler(event, context):
    """Entry point: fetches fixtures and sends SNS alerts for home games."""
    if not API_KEY or not TOPIC_ARN:
        print("ERROR: Missing API_KEY or TOPIC_ARN environment variable.")
        return {"statusCode": 500, "body": "Configuration error."}

    alerts = fetch_and_filter_fixtures()
    
    if not alerts:
        return {"statusCode": 200, "body": "No relevant home matches scheduled today."}

    # Send an SMS for each match found
    published_ids = []
    for message in alerts:
        response = SNS_CLIENT.publish(
            TopicArn=TOPIC_ARN,
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



# this was the test function
# # SNS function
# def lambda_handler(event, context):
#     topic_arn = os.environ["TOPIC_ARN"]

#     message = "Football alert: Blues/Aston Villa home game scheduled."
    
#     response = SNS_CLIENT.publish(
#         TopicArn=topic_arn,
#         Message=message,
#         Subject="Football Traffic Alert",
#         MessageAttributes={
#             "AWS.SNS.SMS.SenderID": {
#                 "DataType": "String",
#                 "StringValue": "FOOTBALL"
#             }
#         }
        
#     )

#     return {
#         "statusCode": 200,
#         "body": f"Published message ID: {response['MessageId']}"
#     }

