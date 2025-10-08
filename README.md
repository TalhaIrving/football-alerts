# ⚽ Football Alerts – Automated Match-Day Traffic Notifications

This project automates **SMS alerts** for upcoming football matches involving specific teams (currently **Birmingham City** and **Aston Villa**) to help plan around heavy matchday traffic.  

It uses **AWS Lambda** for the backend logic, **Amazon SNS** for SMS delivery, and **Terraform** for full infrastructure automation.

---

## 🚀 Features
- Automated Lambda function fetches fixtures and sends SMS alerts for relevant matches.
- Fully serverless — no servers or manual management required.
- Terraform-managed infrastructure for easy deployment.
- Tested with an end-to-end SNS + Lambda integration.

---

## 🧩 Architecture Overview
User → AWS EventBridge (Scheduled Trigger)
→ AWS Lambda (Python)
→ AWS SNS Topic (SMS Notifications)


**Key Components:**
- **Lambda:** Executes Python code to call the fixtures API and publish alerts.  
- **SNS:** Sends SMS notifications to subscribed numbers.  
- **Terraform:** Manages Lambda, SNS, IAM roles, and environment configuration.

---

## 🛠️ Technologies Used
- **AWS Lambda** – Serverless compute
- **AWS SNS (Simple Notification Service)** – SMS publishing
- **AWS IAM** – Permissions and execution roles
- **Terraform** – Infrastructure as Code
- **Python 3.12** – Lambda runtime
- **GitHub** – Version control

---

⚙️ Setup Instructions

1. Clone the repo
```bash
git clone https://github.com/TalhaIrving/football-alerts.git
cd football-alerts/infra

2. Initialise Terraform
terraform init 
terraform apply

This creates:
SNS topic and subscription
Lambda execution role and policy
Lambda function with environment variables

3. Zip and Deploy the Lambda
cd lambda
zip -j ../lambda.zip handler.py
cd ..
terraform apply

4. Test the Lambda Manually
aws lambda invoke \
  --function-name football-alerts-lambda \
  --payload '{"test":"football-alerts"}' \
  --cli-binary-format raw-in-base64-out \
  --region eu-west-2 \
  response.json

Expected output:
{
  "statusCode": 200,
  "body": "Published message ID: ..."
}

An SMS will be delivered to your configured phone number.

---

🧪 Local Testing

If you want to test locally before deployment:

Mock the environment variable:

export TOPIC_ARN=arn:aws:sns:eu-west-2:XXXXXX:football-alerts-topic


Run the handler locally:

python3 lambda/handler.py


Verify it executes without AWS errors (SNS call will fail locally unless mocked).

---

🧭 Next Steps

Add EventBridge rule to schedule Lambda runs automatically.

Integrate football fixture API (e.g., API-Football).

Extend alert logic to handle multiple teams or custom alert preferences.

👤 Author

Talha Irving
https://github.com/TalhaIrving

🪪 License

This project is licensed under the MIT License.
