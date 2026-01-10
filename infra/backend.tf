terraform {
  backend "s3" {
    bucket         = "football-alerts-terraform-state"
    key            = "terraform.tfstate"
    region         = "eu-west-2"
    dynamodb_table = "terraform-lock"
    encrypt        = true
  }
}

