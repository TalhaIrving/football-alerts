Football Alerts – Match-Day Traffic Notifications
This project provisions an automated, serverless system to deliver SMS alerts for upcoming football matches involving specific teams (currently Birmingham City and Aston Villa). The goal is to provide timely notifications to help users plan around heavy match-day traffic in the Birmingham area.
The entire infrastructure is defined and deployed using Terraform and managed via a GitHub Actions CI/CD pipeline.

--------------------------------------------------------------------------------
Features (The "Why")
This system incorporates industry best practices to ensure reliability, security, and maintainability:
• Automated Scheduling: AWS EventBridge (CloudWatch Events) triggers the Lambda function on a daily schedule.
• API Integration: The Python Lambda function fetches fixtures, filters for relevant matches, and prepares alerts.
• Idempotency and Deduplication: The system utilizes a DynamoDB table specifically designed to track and manage match notifications already sent, which effectively avoids sending duplicate alerts to the subscribed endpoints.
• SMS Delivery: Amazon Simple Notification Service (SNS) publishes the final alert message to all subscribed endpoints, ensuring reliable, low-latency text message delivery.
• Infrastructure as Code (IaC): Terraform manages the full environment, including remote state management using S3 and DynamoDB for robust version control and collaboration.
• Least Privilege IAM: The project defines strict IAM roles that grant only the necessary permissions (e.g., CloudWatch logging and SNS publishing) to the Lambda function, adhering to the principle of least privilege.
• Continuous Deployment (CI/CD): A GitHub Actions workflow automates linting, testing, and infrastructure deployment.
• Monitoring and Alerting: The Lambda enables CloudWatch logs, and a CloudWatch alarm is configured to send an SNS alert if an error count exceeds a predefined threshold (e.g., error count > 1).

--------------------------------------------------------------------------------
Architecture Overview
<img width="1024" height="1024" alt="image" src="https://github.com/user-attachments/assets/6c340c80-8f3b-40a2-9d56-02c5bb669c52" />


The system follows a simple, scheduled serverless workflow:
The AWS EventBridge schedules the Lambda function to run at a specific time (e.g., every morning). The AWS Lambda function executes the Python code, calls the external fixtures API, and determines if an alert should be sent. If an alert is required and has not been previously sent (checked against DynamoDB), the Lambda function then publishes the final alert message to all subscribed endpoints via AWS SNS.
Key Components:
• AWS EventBridge: Schedules the Lambda function for daily execution.
• AWS Lambda (Python 3.12): Executes the application logic, API fetching, filtering, and alert preparation.
• AWS SNS: Publishes the final alert message to subscribed mobile numbers.
• AWS DynamoDB: Stores records of sent alerts to ensure deduplication.
• Terraform: Defines the Lambda function, SNS topic, IAM permissions, EventBridge rules, and deployment logic.

--------------------------------------------------------------------------------
Key Implementation Details (How the System Functions)
This section describes how core features operate in the production environment:
1. Remote State Management: Terraform utilizes S3 and DynamoDB to configure the backend for remote state management. This practice ensures state locking and collaboration when managing infrastructure.
2. Lambda Deployment and Logic: The Python Lambda code calls the sports fixtures API and specifically filters for Birmingham City (Blues) and Aston Villa home games. The deployment process uses Terraform definitions to package and deploy the Lambda (either as a zip file or container image).
3. Scheduled Execution: Terraform defines an EventBridge rule that triggers the Lambda on a consistent schedule, such as daily.
4. Permission Management: An IAM role is defined using the principle of least privilege. This role grants the Lambda function permissions only for writing logs to CloudWatch and publishing messages to the specified SNS topic.
5. Security and Deduplication: Before sending an alert, the Lambda checks the DynamoDB table to see if a notification for that specific match has already been sent. This check prevents duplicate SMS messages. Additionally, IAM roles are tightened for maximum security.
6. Variable Management: Terraform employs variable management using mechanisms like workspaces or .tfvars files to handle environment-specific configurations.

--------------------------------------------------------------------------------
Technologies Used
• Cloud Infrastructure: AWS Lambda, AWS SNS, AWS EventBridge, AWS IAM, AWS S3, AWS DynamoDB, AWS CloudWatch.
• Infrastructure as Code (IaC): Terraform.
• Language: Python 3.12.
• Automation: GitHub Actions.
• Testing: pytest (for local unit testing).

--------------------------------------------------------------------------------
Project Development Timeline
The project development followed a structured approach, focusing first on core infrastructure and later incorporating advanced features like security, monitoring, and CI/CD:

1. Repository Foundation and Infrastructure Skeleton: The initial step involved creating the GitHub repository with a clean structure, including dedicated directories for infrastructure (infra/), application code (lambda/), and documentation (docs/). The Terraform boilerplate was written to configure the AWS provider and establish remote state management utilizing S3 and DynamoDB, demonstrating best practice. An Amazon SNS topic was defined, and the subscription endpoint (the mobile phone number) was successfully added.
2. Core Lambda Application Logic (API Fetching): The Python Lambda function was developed. This code calls the external sports fixtures API and specifically filters for home games involving the targeted teams (Birmingham City and Aston Villa). The function was tested locally with a mock event, and unit tests were implemented using pytest.
3. Infrastructure as Code Deployment: Terraform definitions were written to manage the deployment of the system. This included resources for the Lambda deployment (handling packaging whether as a zip or container image) and the EventBridge rule necessary to schedule the daily run. A least privilege IAM role was defined, granting the function only the required permissions (CloudWatch logging and SNS publishing). Successful deployment enabled a conclusive end-to-end test (API call resulting in an SMS).
4. CI/CD Pipeline Implementation: A robust GitHub Actions workflow was created to automate the deployment process. This workflow ensures consistency by first linting and testing the Lambda code, then packaging the Lambda, and finally executing terraform plan followed by terraform apply. AWS credentials were securely managed using GitHub Secrets, and the full pipeline process was documented.
5. Monitoring and Logging: Operational visibility was established by enabling CloudWatch logs for the Lambda function. A critical CloudWatch alarm was configured to monitor system health; this alarm sends an SNS alert if the error count exceeds a threshold (e.g., error count > 1). Furthermore, a basic metrics dashboard was added in the AWS console for quick operational oversight.
6. Security Refinement and Deduplication: To enhance resilience, a DynamoDB table was introduced solely for tracking match notifications that have already been sent, which effectively avoids sending duplicate alerts to users. Security was finalized by tightening the IAM roles to strictly enforce the principle of least privilege. Lastly, Terraform variable management (using workspaces or .tfvars) was implemented for handling environment-specific configurations.

--------------------------------------------------------------------------------

## Project Setup & Installation

Follow these steps sequentially to set up the project environment on your local machine:

1.  **Clone the Repository**
    Start by copying the entire project to your local machine:
    ```bash
    git clone [https://github.com/TalhaIrving/football-alerts.git](https://github.com/TalhaIrving/football-alerts.git)
    cd football-alerts/infra/lambda
    ```

2.  **Install System Dependencies**
    Ensure you have the required infrastructure tools installed globally:
    ```bash
    # Install Terraform CLI and AWS CLI
    sudo apt-get install terraform awscli
    ```

3.  **Set Up Python Environment**
    Navigate to the Lambda directory and create/activate the isolated environment:
    ```bash
    # (Assuming you are in infra/lambda directory from step 1)
    python3 -m venv .venv
    source .venv/bin/activate
    ```

4.  **Install Python Libraries**
    Install the core dependencies and the essential local testing tools:
    ```bash
    # Install core libraries (requests, pytz) and testing tools (pytest, boto3, moto)
    pip install -r requirements.txt pytest boto3 moto
    
    # Install dotenv for local secret management (loading the .env file)
    pip install python-dotenv
    ```

5.  **Configure Local Secrets**
    Create the necessary file to hold your API key for local testing. **Crucially, ensure this file is listed in your .gitignore.**
    * Create a file named **`.env`** in the `infra/lambda` directory.
    * Add your actual credentials inside the file:
        ```
        api_key="YOUR_ACTUAL_API_FOOTBALL_KEY_HERE"
        TOPIC_ARN="arn:aws:sns:eu-west-2:XXXXXX:football-alerts-topic"
        ```


The entire system functions like a digital newspaper delivery service: EventBridge is the delivery truck that arrives every morning, Lambda is the reporter who checks the news (the API) to see if there is a relevant story (a match), DynamoDB is the ledger checking if the customer has already received that day's paper, and SNS is the paperboy who throws the relevant alert onto your front porch (your phone).


Author

Talha Irving

License

This project is licensed under the MIT License
