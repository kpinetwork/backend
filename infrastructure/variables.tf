# ----------------------------------------------------------------------------------------------------------------------
# AWS CREDENTIALS
# ----------------------------------------------------------------------------------------------------------------------

variable "aws_access_key_id" {
  description = "AWS access key credential"
  sensitive = true
}

variable "aws_secret_access_key" {
  description = "AWS secret access key credential"
  sensitive = true
}

variable "region" {
  default = "us-west-2"
}

variable "aws_account_id" {
  description = "AWS account id"
  sensitive = true
}

variable "root_domain_name" {
  default = "kpinetwork.com"
}


# ----------------------------------------------------------------------------------------------------------------------
# LAMBDAS NAMES
# ----------------------------------------------------------------------------------------------------------------------

variable "lambdas_names" {
  default = {
    "minimal_lambda_function": "minimal_lambda_function"
    "db_sample_lambda_function": "db_sample_lambda_function"
  }
}

# ----------------------------------------------------------------------------------------------------------------------
# DATABASE VARIABLES
# ----------------------------------------------------------------------------------------------------------------------

variable "db_username" {
  description = "KPI Networks database root username"
  type = string
  sensitive = true
}

variable "db_password" {
  description = "KPI Networks database root user password"
  type = string
  sensitive = true
}

# ----------------------------------------------------------------------------------------------------------------------
# CODEBUILD VARIABLES
# ----------------------------------------------------------------------------------------------------------------------

variable "git_token" {
  description = "Git token to access codebuild"
  type = string
  sensitive = true
}

