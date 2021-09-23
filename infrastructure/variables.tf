# ----------------------------------------------------------------------------------------------------------------------
# AWS CREDENTIALS
# ----------------------------------------------------------------------------------------------------------------------

variable "aws_access_key_id" {
  description = "AWS access key credential"
}

variable "aws_secret_access_key" {
  description = "AWS secret access key credential"
}

variable "region" {
  default = "us-west-2"
}

variable "aws_account_id" {
  description = "AWS account id"
}

# ----------------------------------------------------------------------------------------------------------------------
# LAMBDAS NAMES
# ----------------------------------------------------------------------------------------------------------------------

variable "lambdas_names" {
  default = {
    "minimal_lambda_function": "minimal_lambda_function"
  }
}

# ----------------------------------------------------------------------------------------------------------------------
# DATABASE VARIABLES
# ----------------------------------------------------------------------------------------------------------------------

variable "db_username" {
  description = "KPI Networks database root username"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "KPI Networks database root user password"
  type        = string
  sensitive   = true
}