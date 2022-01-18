# ----------------------------------------------------------------------------------------------------------------------
# GENERAL CONFIGURATIONS
# ----------------------------------------------------------------------------------------------------------------------

variable "runtime" {
  default = "python3.6"
}
variable "environment" {}

variable "layer_name" {
  default = "db_lambda_layer"
}

variable "aws_account_id" {}
variable "region" {}

# ----------------------------------------------------------------------------------------------------------------------
# LAMBDA INPUTS
# ----------------------------------------------------------------------------------------------------------------------
variable "lambdas_exec_roles_arn" {}
variable "object_bucket_references" {}
variable "lambdas_names" {}
variable "bucket_files" {}

# ----------------------------------------------------------------------------------------------------------------------
# VPC INPUTS
# ----------------------------------------------------------------------------------------------------------------------

variable "public_subnet_a_id" {}
variable "security_group_id" {}

variable "db_host" {}
variable "db_name" {}
variable "db_username" {}
variable "db_password" {}
variable "aws_access_key_id" {}
variable "aws_secret_access_key" {}

# ----------------------------------------------------------------------------------------------------------------------
# AUTHORIZE
# ----------------------------------------------------------------------------------------------------------------------
variable "user_pool_id" {}
variable "app_client_id" {}
variable "api_gateway" {}
