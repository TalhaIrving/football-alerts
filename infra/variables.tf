variable "aws_region" {
  description = "AWS region to deploy resources"
  default     = "eu-west-2"
}

variable "topic_name" {
  description = "SNS topic name"
  default     = "football-alerts-topic"
}
variable "aws_profile" {
  description = "AWS CLI profile to use (leave empty in CI/CD)"
  type        = string
  default     = "talhairving@gmail.com"
}
