terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
  }
  backend "s3" {
    bucket = "kpinetwork-infrastructure"
    key    = "backend/terraform.tfstate"
    region = "us-west-2"
    dynamodb_table = "terraform-state"
  }
}