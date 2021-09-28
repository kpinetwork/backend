# ----------------------------------------------------------------------------------------------------------------------
# GENERAL CONFIGURATIONS
# ----------------------------------------------------------------------------------------------------------------------

variable "stage_name" {
  default = "prod"
  type = string
}

variable "lambdas_functions_arn" {}

variable "tag_name" {
  default = "kpinetworks"
}

variable "kpinetworks_vpc_id" {}

variable "kpinetworks_public_subnet_a_id" {}

variable "kpinetworks_private_subnet_a_id" {}
