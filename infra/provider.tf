provider "aws" {
  region = var.aws_region

  # Only use the profile when running locally (not in CI)
  profile = var.aws_profile != "" ? var.aws_profile : null
}
