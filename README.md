⚽ Football Alerts – Match-Day Traffic Notifications

This project provisions an automated, serverless system to deliver SMS alerts for upcoming home football matches involving specific teams (currently Birmingham City and Aston Villa). The goal is to provide timely notifications to help users plan around heavy match-day traffic in the Birmingham area.

The entire infrastructure is defined and deployed using Terraform and managed via a GitHub Actions CI/CD pipeline.

✨ Features

Automated Scheduling: Uses AWS EventBridge (CloudWatch Events) to trigger the Lambda function on a daily schedule.

API Integration: The Lambda function fetches fixtures, filters for relevant home matches, and prepares alerts.

SMS Delivery: Utilizes Amazon Simple Notification Service (SNS) for reliable, low-latency text message delivery.

Infrastructure as Code (IaC): Full environment managed by Terraform with remote state management (S3 + DynamoDB).

Continuous Deployment: Automated linting, testing, and infrastructure deployment via GitHub Actions.

Monitoring & Observability: A comprehensive CloudWatch Dashboard provides real-time, end-to-end visibility into the system's health (Lambda Invocations, Errors, and SNS Messages Sent), all defined in Terraform.

🏗️ Architecture Overview

The system follows a simple, scheduled serverless workflow:

Key Components:

AWS EventBridge: Schedules the Lambda function to run at a specific time (e.g., every morning).

AWS Lambda (Python 3.12): Executes the Python code, calls the external fixtures API (API-Football V3), and determines if an alert should be sent.

AWS SNS: Publishes the final alert message to all subscribed endpoints (your mobile number).

AWS CloudWatch: Provides logging, metrics, and a dashboard for end-to-end observability.

Terraform: Defines all resources, including the Lambda function, SNS topic, IAM permissions, and the CloudWatch Dashboard.

AWS S3 & DynamoDB: Used for Terraform's remote state backend and state locking.

📦 Technologies Used

Cloud Infrastructure: AWS Lambda, AWS SNS, AWS EventBridge, AWS IAM, AWS S3, AWS DynamoDB, AWS CloudWatch

Infrastructure as Code (IaC): Terraform

Language: Python 3.12

Automation: GitHub Actions

Testing: pytest (local unit testing)

⚙️ CI/CD Pipeline (GitHub Actions)

The CI/CD pipeline (.github/workflows/deploy.yml) ensures automated, tested, and standardized deployment of the infrastructure and code.

Pipeline Structure

The pipeline consists of a single job (build-test-deploy) that is automatically triggered on every push to the main branch or on any Pull Request. It authenticates to AWS using secure GitHub Repository Secrets (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY).

Deployment Process

The deployment uses a robust multi-step approach:

Setup & Tests: Checks out code, sets up Python, installs dependencies, and executes unit tests (pytest).

Terraform Initialization: Initializes the project, connecting to the remote state backend (S3/DynamoDB).

Code Packaging & Validation: The terraform plan step forces the creation of the Lambda ZIP artifact (lambda.zip) and runs local size checks. It also runs terraform fmt and terraform validate.

Deployment (Apply): The terraform apply command executes only on the main branch, provisioning or updating all AWS resources.

🚀 Setup & Manual Testing

This guide assumes you have the AWS CLI and Terraform installed locally.

Prerequisites

You must set the following environment variables for local execution, or ensure they are set as GitHub Secrets for the pipeline.

Variable

Description

CI/CD Source

AWS_ACCESS_KEY_ID

Your AWS access key

GitHub Secret

AWS_SECRET_ACCESS_KEY

Your AWS secret key

GitHub Secret

TF_VAR_api_key

API-Football API Key

GitHub Secret

Manual Deployment (For Initial Setup/Debugging)

(Steps for local terraform init, plan, and apply...)

Local Lambda Testing

(Steps for local python3 handler.py...)

End-to-End Test (Via AWS CLI)

After deployment, invoke the Lambda function manually to test the full pipeline:

aws lambda invoke \
--function-name football-alerts-lambda \
--payload '{"test":"match-check"}' \
--cli-binary-format raw-in-base64-out \
--region eu-west-2 \
response.json


Expected output (if a home game is scheduled):

{
  "statusCode": 200,
  "body": "Published 1 alert(s). IDs: ..."
}


Expected output (if no home game is scheduled):

{
  "statusCode": 200,
  "body": "No relevant home matches scheduled today."
}


🛠️ Key Implementation Details

This section details how the project's core features were implemented.

1. Automated Scheduling (EventBridge)

The Lambda function is triggered automatically every morning at 8:00 AM UTC. This is defined in infra/main.tf using two Terraform resources:

aws_cloudwatch_event_rule "every_morning": This resource defines the schedule using a cron(0 8 * * ? *) expression.

aws_cloudwatch_event_target "trigger_lambda": This resource links the event rule to the Lambda function, giving it permission to invoke the function when the schedule is met.

2. API Integration & Filtering (Lambda)

The core application logic resides in infra/lambda/handler.py.

API Call: The function uses the Python requests library to call the API-Football V3 /fixtures endpoint. It authenticates by passing the api_key (sourced from GitHub Secrets and passed to Terraform as a variable) in the request headers.

Filtering Logic: The function requests all fixtures for the current date. It then loops through the results and filters them based on two criteria:

Home Game: The match's home_id must be in the target list.

Target Team: The home_id must match one of the verified IDs for our teams: 66 (Aston Villa) or 54 (Birmingham City).

Outcome: If no matches are found, the function exits gracefully. If a match is found, it proceeds to publish an alert.

3. Monitoring & Observability (CloudWatch)

End-to-end system health is monitored using a custom dashboard defined in infra/main.tf via the aws_cloudwatch_dashboard resource. This dashboard provides immediate, at-a-glance proof that the system is working and includes three critical widgets:

Lambda Invocations (Sum): Proves that the EventBridge scheduler successfully triggered the Lambda function.

Lambda Errors (Sum): Proves that the Python code executed without crashing (e.g., no API timeouts or code exceptions).

SNS Messages Published (Sum): Proves that the function's logic was met (a home game was found) and that the final alert was successfully sent to SNS.

✍️ Author

Talha Irving

📄 License

This project is licensed under the MIT License
