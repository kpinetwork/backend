terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "~> 3.0"
    }
  }

  backend "s3" {
    bucket = "kpinetwork-backend"
    key = "terraform.tfstate"
    region = "us-west-2"
    workspace_key_prefix = "env:"
  }
}