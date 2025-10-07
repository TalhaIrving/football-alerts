output "sns_topic_arn" {
  description = "ARN of the Football Alerts SNS topic"
  value       = aws_sns_topic.football_alerts.arn
}

output "sns_subscription_id" {
  description = "ID of the Football Alerts SNS subscription"
  value       = aws_sns_topic_subscription.sms_subscription.id
}


output "aws_region" {
  description = "AWS region where resources were deployed"
  value       = var.aws_region
}

output "lambda_arn" {
  description = "ARN of the Football Alerts Lambda"
  value       = aws_lambda_function.football_alerts.arn
}

output "lambda_invoke_arn" {
  description = "Invoke ARN of the Football Alerts Lambda"
  value       = aws_lambda_function.football_alerts.invoke_arn
}
