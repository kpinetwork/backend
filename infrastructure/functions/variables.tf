# ----------------------------------------------------------------------------------------------------------------------
# GENERAL CONFIGURATIONS
# ----------------------------------------------------------------------------------------------------------------------

variable "runtime" {
  default = "python3.7"
}
variable "environment" {}

variable "layer_name" {
  default = "db_lambda_layer"
}

# ----------------------------------------------------------------------------------------------------------------------
# LAMBDA INPUTS
# ----------------------------------------------------------------------------------------------------------------------

variable "minimal_lambda_function_exec_role_arn" {}
#variable "minimal_lambda_function_bucket" {}
#variable "db_sample_lambda_function_bucket" {}
variable "s3_object_references" {}
variable "lambdas_names" {}
variable "object_buckets_information" {}
variable "lambda_exec_roles_arn" {}
variable "bucket_files" {}
# ----------------------------------------------------------------------------------------------------------------------
# LAMBDA LAYER INPUTS
# ----------------------------------------------------------------------------------------------------------------------

variable "lambda_layer_bucket" {}

# ----------------------------------------------------------------------------------------------------------------------
# VPC INPUTS
# ----------------------------------------------------------------------------------------------------------------------

variable "public_subnet_a_id" {}
variable "security_group_id" {}