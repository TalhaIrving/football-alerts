import json
import handler

def test_lambda_handler_success(monkeypatch):
    # Mock SNS publish
    def mock_publish(self, **kwargs):
        return {"MessageId": "12345"}
    
    # Replace the module-level SNS client with a mock so no AWS calls are made
    mock_sns = type("MockSNS", (), {"publish": mock_publish})()
    monkeypatch.setattr(handler, "sns", mock_sns, raising=True)
    
    # Ensure required environment variable is present for the handler
    monkeypatch.setenv("TOPIC_ARN", "arn:aws:sns:eu-west-1:123456789012:dummy-topic")

    event = {"test": "football-alerts"}
    result = handler.lambda_handler(event, None)
    
    assert result["statusCode"] == 200
    assert "Published message ID:" in result["body"]
