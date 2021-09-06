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
# AWS GENERAL CONFIGURATIONS
# ----------------------------------------------------------------------------------------------------------------------

variable "runtime" {
  default = "python3.8"
}

variable "bucket_name" {
  default = "kpinetwork-backend"
}

variable "stage_name" {
  default = "prod"
  type    = string
}

variable "retention_days" {
  default = 14
}

# ----------------------------------------------------------------------------------------------------------------------
# LAMBDA NAMES
# ----------------------------------------------------------------------------------------------------------------------

variable "function_name" {
  default = "minimal_lambda_function"
}

# ----------------------------------------------------------------------------------------------------------------------
# CLOUDWATCH LOG GROUPS
# ----------------------------------------------------------------------------------------------------------------------

variable "prefix_lambda_cloudwatch_log_group" {
  default = "/aws/lambda/"
}
