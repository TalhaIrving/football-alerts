⚽ Football Alerts – Match-Day Traffic Notifications

This project provisions an automated, serverless system to deliver SMS alerts for upcoming home football matches involving specific local teams (Aston Villa and Birmingham City). The goal is to provide timely notifications to help users plan around heavy match-day traffic in the Birmingham area.

The entire infrastructure is defined and deployed using Terraform and managed via a GitHub Actions CI/CD pipeline.

✨ Completed Professional Features

Idempotency & Deduplication: Implemented a DynamoDB table to track sent match IDs, ensuring the system never sends duplicate SMS alerts even during AWS retries or manual testing failures.

Least Privilege IAM: Replaced the overly broad default logging policy with a custom one, granting the Lambda function only the specific permissions needed for logging and operations.

Home Game Filtering: The Python handler is configured to discriminate, only triggering alerts for home games where the home_id matches the target teams (Aston Villa: 66, Birmingham City: 54).

Monitoring & Observability: Created a custom CloudWatch Dashboard to monitor end-to-end health (Invocations, Errors, SNS Publishes).

Infrastructure as Code (IaC): Full environment managed by Terraform with remote state management (S3 + DynamoDB).

🏗️ Architecture Overview

The system follows a simple, scheduled serverless workflow:

AWS EventBridge: Schedules the Lambda function to run daily.

AWS Lambda (Python 3.12): Executes the Python code, calls the external fixtures API (API-Football V3), and determines if an alert should be sent.

Amazon DynamoDB: Stores match IDs to prevent duplicate alerts (Deduplication).

AWS SNS: Publishes the final alert message via SMS.

🛠️ Key Implementation Details

This section details how the project's core features were implemented in code.

1. Scheduler and API Integration

Scheduler: The aws_cloudwatch_event_rule resource is configured with the expression cron(0 8 * * ? *), ensuring the Lambda executes daily at 8:00 AM UTC.

API Logic: The Python handler uses the requests library and authenticates via an api_key environment variable. The code calculates the current date and sends a targeted query to the API-Football V3 /fixtures endpoint for all games on that specific day.

Filtering: The function executes the core filtering logic by checking if the fixture's home_id is present within the hardcoded TARGET_TEAM_IDS list ([66, 54]), bypassing all away games.

2. Security and Deduplication

Idempotency: A DynamoDB table (football-alerts-deduplication) is created with a TTL (Time To Live) attribute. The Python handler executes a conditional PutItem operation: the SMS is only sent if the database confirms the match ID does not already exist, preventing duplicate alerts from being sent during retries.

Least Privilege Logging: The Lambda's logging policy no longer uses the * wildcard. Instead, it grants permission only to the specific log group created by the aws_cloudwatch_log_group resource (/aws/lambda/football-alerts-lambda).

3. Monitoring

The system's operational health is tracked via a custom aws_cloudwatch_dashboard resource that explicitly monitors three key metrics:

AWS/Lambda:Invocations (Sum)

AWS/Lambda:Errors (Sum)

AWS/SNS:NumberOfMessagesPublished (Sum)

🚀 Setup & Local Testing

Local Secrets Management

To run the function locally, you must provide the environment variables:

Create .env: Create a file named .env inside the infra/lambda directory (ensure it is listed in your .gitignore).

Populate .env: Add your actual API key and Topic ARN to the file:

api_key="YOUR_ACTUAL_API_FOOTBALL_KEY_HERE"
TOPIC_ARN="arn:aws:sns:eu-west-2:XXXXXX:football-alerts-topic"


Local Lambda Execution

You must activate the virtual environment and load the environment file before testing:

# 1. Navigate to the Lambda directory
cd infra/lambda

# 2. Activate the virtual environment
source .venv/bin/activate

# 3. Test the handler logic (it loads secrets from .env automatically)
python3 handler.py

# 4. Deactivate the environment when done
deactivate
