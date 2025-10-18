import json
import handler

def test_lambda_handler_success(monkeypatch):
    # Mock SNS publish
    def mock_publish(self, **kwargs):
        return {"MessageId": "12345"}
    
    # Replace the module-level SNS client with a mock so no AWS calls are made
    mock_SNS_CLIENT = type("MockSNSClient", (), {"publish": mock_publish})()
    monkeypatch.setattr(handler, "SNS_CLIENT", mock_SNS_CLIENT, raising=True)
    
# ADD THIS LINE: Mocks the API key for the handler to pass its initial check
    monkeypatch.setenv("API_KEY", "dummy-api-key")

    event = {"test": "football-alerts"}
    result = handler.lambda_handler(event, None)
    
    assert result["statusCode"] == 200
    assert "Published message ID:" in result["body"]
