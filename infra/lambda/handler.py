import json

import boto3
import os


# SNS function 
sns = boto3.client("sns", region_name=os.getenv("AWS_REGION", "eu-west-2"))

# SNS function
def lambda_handler(event, context):
    topic_arn = os.environ["TOPIC_ARN"]

    message = "Football alert: Blues/Aston Villa home game scheduled."
    
    response = sns.publish(
        TopicArn=topic_arn,
        Message=message,
        Subject="Football Traffic Alert",
        MessageAttributes={
            "AWS.SNS.SMS.SenderID": {
                "DataType": "String",
                "StringValue": "FOOTBALL"
            }
        }
        
    )

    return {
        "statusCode": 200,
        "body": f"Published message ID: {response['MessageId']}"
    }

