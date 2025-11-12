import handler
import requests # Required for mocking requests
import boto3 # Required for mocking boto3
import pytz # Required by handler logic
import json
from datetime import datetime
import pytest
from dotenv import load_dotenv # for loading environment variables from local .env file

load_dotenv()

# --- 1. Mock Data for API ---
# This simulates a successful API-Football response with one relevant match
MOCK_API_RESPONSE = {
    "response": [
        {
            "fixture": {
                "id": 12345, "timezone": "UTC", "date": "2025-11-05T19:00:00+00:00",
                "venue": {"id": 558, "name": "Villa Park", "city": "Birmingham"},
                "status": {"long": "Not Started", "short": "NS"}
            },
            "teams": {
                "home": {"id": 66, "name": "Aston Villa", "winner": None}, # Target team ID 66
                "away": {"id": 40, "name": "Liverpool", "winner": None}
            }
        }
    ]
}

# --- 2. Mock Class for Requests ---
# This class will intercept the requests.get() call
class MockRequests:
    @staticmethod
    def get(url, headers, params):
        class MockResponse:
            def json(self): return MOCK_API_RESPONSE
            def raise_for_status(self): return None
        return MockResponse()

# --- 3. Mock Class for SNS Client ---
# This class will intercept the boto3.client("sns", ...) call
class MockSNSClient:
    def __init__(self, *args, **kwargs):
        # We don't need the args, but we accept them
        print("MockSNSClient initialized")
    
    def publish(self, **kwargs):
        # Check that the TopicArn is being passed correctly (optional)
        assert "arn:aws:sns:eu-west-1:123456789012:dummy-topic" in kwargs.get("TopicArn")
        # Return the expected response
        return {"MessageId": "12345-mock-id"}

# --- 4. The Test Function ---
def test_lambda_handler_success(monkeypatch):
    
    # --- MOCKING SETUP ---
    
    # A) Mock the external API call (requests.get)
    monkeypatch.setattr(requests, "get", MockRequests.get)
    
    # B) Mock the boto3.client call
    #    When handler.py calls boto3.client("sns", ...), 
    #    it will get an instance of our MockSNSClient instead.
    monkeypatch.setattr(boto3, "client", MockSNSClient)
    
    # C) Set the environment variables the handler needs
    monkeypatch.setenv("TOPIC_ARN", "arn:aws:sns:eu-west-1:123456789012:dummy-topic")
    monkeypatch.setenv("api_key", "dummy-api-key") # Use lowercase 'api_key' to match handler

    # --- EXECUTION ---
    event = {"test": "football-alerts"}
    result = handler.lambda_handler(event, None)

    # --- ASSERTIONS ---
    
    # Check for the 200 OK status
    assert result["statusCode"] == 200
    
    # Check that the body confirms 1 alert was processed 
    assert "Published 1 alert(s)." in result["body"]