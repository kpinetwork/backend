# ----------------------------------------------------------------------------------------------------------------------
# GENERAL CONFIGURATIONS
# ----------------------------------------------------------------------------------------------------------------------

variable "retention_days" {
  default = 14
}

# ----------------------------------------------------------------------------------------------------------------------
# CLOUDWATCH LOG GROUPS
# ----------------------------------------------------------------------------------------------------------------------

variable "prefix_lambda_cloudwatch_log_group" {
  default = "/aws/lambda/"
}

variable "lambdas_names" {}


variable "prefix_codebuild_cloudwatch_log_group" {
  default = "/aws/codebuild/"
}


variable "codebuild_project_name" {
    default = "rds_migrations"
}