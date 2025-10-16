? Football Alerts – Match-Day Traffic Notifications

This project provisions an automated, serverless system to deliver SMS alerts for upcoming football matches involving specific teams (currently Birmingham City and Aston Villa). The goal is to provide timely notifications to help users plan around heavy match-day traffic in the Birmingham area.

The entire infrastructure is defined and deployed using Terraform and managed via a GitHub Actions CI/CD pipeline.

? Features

Automated Scheduling: Uses AWS EventBridge (CloudWatch Events) to trigger the Lambda function on a daily schedule.

API Integration: The Lambda function fetches fixtures, filters for relevant matches, and prepares alerts.

SMS Delivery: Utilizes Amazon Simple Notification Service (SNS) for reliable, low-latency text message delivery.

Infrastructure as Code (IaC): Full environment managed by Terraform with remote state management (S3 + DynamoDB).

Continuous Deployment: Automated linting, testing, and infrastructure deployment via GitHub Actions.

??? Architecture Overview

The system follows a simple, scheduled serverless workflow:

Key Components:

AWS EventBridge: Schedules the Lambda function to run at a specific time (e.g., every morning).

AWS Lambda (Python 3.12): Executes the Python code, calls the external fixtures API (to be integrated), and determines if an alert should be sent.

AWS SNS: Publishes the final alert message to all subscribed endpoints (your mobile number).

Terraform: Defines the Lambda function, SNS topic, IAM permissions, and deployment logic.

?? Technologies Used

Cloud Infrastructure: AWS Lambda, AWS SNS, AWS EventBridge, AWS IAM, AWS S3, AWS DynamoDB.

Infrastructure as Code (IaC): Terraform

Language: Python 3.12

Automation: GitHub Actions

Testing: pytest (local unit testing)

?? CI/CD Pipeline (GitHub Actions)

The CI/CD pipeline (.github/workflows/deploy.yml) ensures automated, tested, and standardized deployment of the infrastructure and code.

4.1. Pipeline Structure

The pipeline consists of a single job (build-test-deploy) that is automatically triggered on every push to the main branch or on any Pull Request. It authenticates to AWS using secure GitHub Repository Secrets (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY).

4.2. Deployment Process

The deployment uses a robust multi-step approach:

Setup & Tests: Checks out code, sets up Python, installs dependencies, and executes unit tests (pytest).

Terraform Initialization: Initializes the project, connecting to the remote state backend (S3/DynamoDB) and refreshing provider configurations.

Code Packaging: The terraform plan step forces the creation of the Lambda ZIP artifact (lambda.zip) and uploads it to an S3 bucket.

Note: This S3 deployment method (configured in main.tf) is essential to bypass the ~50 MB file size limit for direct AWS Lambda API uploads.

Format & Validation: Runs terraform fmt -recursive (to enforce HCL style) and terraform validate (to check configuration logic).

Deployment (Apply): The terraform apply command executes only on the main branch, provisioning or updating all AWS resources.

?? Setup & Manual Testing

This guide assumes you have the AWS CLI and Terraform installed locally.

1. Prerequisites

You must set the following environment variables (or Git-ignored terraform.tfvars file) for local execution:

Variable

Description

CI/CD Source

AWS_ACCESS_KEY_ID

Your AWS access key

GitHub Secret

AWS_SECRET_ACCESS_KEY

Your AWS secret key

GitHub Secret

TF_VAR_aws_profile

Local AWS profile name (used for local manual runs only)

.tfvars file (Git Ignored)

2. Manual Deployment (For Initial Setup/Debugging)

The CI/CD pipeline handles production deployment, but you can run these steps locally to manage the state and infrastructure:

# Navigate to the infrastructure directory
cd infra

# Initialize Terraform (fetches providers and sets up backend)
terraform init

# Review the changes Terraform will make
terraform plan -input=false

# Apply the changes and deploy the infrastructure (Lambda is deployed via S3 logic)
terraform apply -auto-approve


3. Local Lambda Testing

You can run the core Lambda handler locally to test its execution without deploying to AWS:

# Navigate to the Lambda directory
cd infra/lambda

# Activate the virtual environment
source .venv/bin/activate

# Mock the environment variable required by the Lambda handler
export TOPIC_ARN="arn:aws:sns:eu-west-2:XXXXXX:football-alerts-topic"

# Run the handler locally
python3 handler.py

# Deactivate the environment when done
deactivate


(Note: The SNS publishing will fail locally unless you use a mock library or the environment is configured with dummy AWS credentials.)

4. End-to-End Test (Via AWS CLI)

After deployment, invoke the Lambda function manually to test the full pipeline (Lambda fetch + SNS publish):

aws lambda invoke \
  --function-name football-alerts-lambda \
  --payload '{"test":"match-check"}' \
  --cli-binary-format raw-in-base64-out \
  --region eu-west-2 \
  response.json

# Expected output in response.json and an SMS delivered to your number:
# {
#   "statusCode": 200,
#   "body": "Published message ID: ..."
# }


?? Next Steps (Day 5 Onward)

Add EventBridge rule definition to schedule Lambda runs automatically.

Integrate the external football fixture API (e.g., API-Football) into the Python handler.

Implement CloudWatch monitoring and alarms (Day 5 task).

Implement DynamoDB logic for alert deduplication (Day 6 task).

?? Author

Talha Irving

?? License

This project is licensed under the MIT License.