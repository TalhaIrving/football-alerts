import requests # NEW: Required for mocking
from datetime import datetime
import pytz # NEW: May be needed by the handler logic running in the test

# Mock data simulating a successful API-Football response
MOCK_API_RESPONSE = {
    "response": [
        {
            "fixture": {
                "id": 12345,
                "timezone": "UTC",
                "date": "2025-11-05T19:00:00+00:00", 
                "venue": {"id": 558, "name": "Villa Park", "city": "Birmingham"},
                "status": {"long": "Not Started", "short": "NS"}
            },
            "league": {"id": 39, "name": "Premier League", "country": "England"},
            "teams": {
                "home": {"id": 33, "name": "Aston Villa", "winner": None}, # Target team ID 33
                "away": {"id": 40, "name": "Liverpool", "winner": None}
            },
            "goals": {"home": None, "away": None},
            "score": {"halftime": None, "fulltime": None}
        }
    ]
}

# NEW: Mock class to replace requests.get()
class MockRequests:
    @staticmethod
    def get(url, headers, params):
        class MockResponse:
            def json(self):
                return MOCK_API_RESPONSE
            def raise_for_status(self):
                return None # Simulates a successful 200 HTTP response
        return MockResponse()

def test_lambda_handler_success(monkeypatch):
    
    # 1. NEW: Mock the external API call to return fake data
    monkeypatch.setattr("requests.get", MockRequests.get)
    
    # Mock SNS publish: This ensures no real AWS calls are made.
    # Note: We mock the actual publish method on the client object itself.
    def mock_publish(**kwargs):
        # We need to return a dict that contains a MessageId
        return {"MessageId": "12345"}

    # Replace the actual 'publish' method on the existing handler's SNS_CLIENT
    monkeypatch.setattr(handler.SNS_CLIENT, "publish", mock_publish)
    
    # Ensure required environment variables are set for the handler function's os.environ.get() checks
    # This also helps stabilize the environment variables read by the handler.
    monkeypatch.setenv("TOPIC_ARN", "arn:aws:sns:eu-west-1:123456789012:dummy-topic")
    monkeypatch.setenv("API_KEY", "dummy-api-key")

    event = {"test": "football-alerts"}
    
    # Call the actual Lambda handler
    result = handler.lambda_handler(event, None)

    # --- ASSERTIONS ---
    
    # Your handler returns 200 upon success
    assert result["statusCode"] == 200
    # FIX: Assert the content we expect from a successful run with our mocked data.
    # It should confirm the number of alerts published.
    assert "Published 1 alert(s)." in result["body"]