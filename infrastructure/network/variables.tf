# ----------------------------------------------------------------------------------------------------------------------
# GENERAL CONFIGURATIONS
# ----------------------------------------------------------------------------------------------------------------------

variable "stage_name" {
  default = "prod"
  type = string
}

variable "api_name" {
  default = "kpinetwork_api"
  type = string
}

variable "lambdas_functions_arn" {}

variable "domain_name" {}
variable "certificate_arn" {}

variable "environment" {}
variable "is_production" {}