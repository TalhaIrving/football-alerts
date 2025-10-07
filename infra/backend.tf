terraform {
  backend "s3" {
    bucket         = "football-alerts-terraform-state"
    key            = "terraform.tfstate"
    region         = "eu-west-2"
    dynamodb_table = "terraform-locks"
    encrypt        = true
    profile        = "talhairving@gmail.com"
  }
}

