# S3 bucket for Terraform state storage
resource "aws_s3_bucket" "terraform_state" {
  bucket = "football-alerts-terraform-state"
}

# Versioning
resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Block public access to the S3 bucket
resource "aws_s3_bucket_public_access_block" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# DynamoDB table for state locking
resource "aws_dynamodb_table" "terraform_locks" {
  name         = "terraform-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}

# Create an SNS topic for football alerts
resource "aws_sns_topic" "football_alerts" {
  name = var.topic_name
}

# Subscribe your phone number to the topic
resource "aws_sns_topic_subscription" "sms_subscription" {
  topic_arn = aws_sns_topic.football_alerts.arn
  protocol  = "sms"
  endpoint  = "+447761999587" # 👈 replace with your mobile number (E.164 format)
}

# Lambda function IAM role
resource "aws_iam_role" "lambda_exec" {
  name = "football-alerts-lambda-role"

  # IAM role for Lambda assume role policy
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

# IAM role policy attachment for Lambda logging
resource "aws_iam_role_policy_attachment" "lambda_logging" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Lambda function
resource "aws_lambda_function" "football_alerts" {
  function_name    = "football-alerts-lambda"
  role             = aws_iam_role.lambda_exec.arn
  handler          = "handler.lambda_handler"
  runtime          = "python3.12"
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256


  environment {
    variables = {
      TOPIC_ARN = aws_sns_topic.football_alerts.arn
    }
  }
}


# Archive the Lambda function
# This is used to zip the Lambda function and upload it to AWS
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda"
  output_path = "${path.module}/lambda.zip"
}

# IAM role policy for Lambda to publish to SNS
resource "aws_iam_role_policy" "lambda_sns_publish" {
  name = "lambda-sns-publish"
  role = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow"
        Action   = "sns:Publish"
        Resource = aws_sns_topic.football_alerts.arn
      }
    ]
  })
}

# EventBridge rule to schedule the Lambda function
resource "aws_cloudwatch_event_rule" "football_alerts_schedule" {
  name                = "football-alerts-schedule"
  description         = "Triggers the football-alerts Lambda every hour"
  schedule_expression = "cron(0 8 * * ? *)" # change this as needed
}

# EventBridge target to schedule the Lambda function
resource "aws_cloudwatch_event_target" "football_alerts_target" {
  rule      = aws_cloudwatch_event_rule.football_alerts_schedule.name
  target_id = "football-alerts-lambda"
  arn       = aws_lambda_function.football_alerts.arn
}

# Lambda permission to allow EventBridge to invoke the Lambda function
resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.football_alerts.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.football_alerts_schedule.arn
}

