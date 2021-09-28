variable "region" {}
variable "account_id" {}
variable "lambdas_names" {}
variable "api_gateway_minimal_lambda_function" {}

variable "codebuild_role_name" {
    default = "codebuild_exec_role"
}

variable "private_subnet_a" {}