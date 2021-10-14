variable "region" {}

variable "environment" {}
variable "is_production" {}

variable "db_username" {}
variable "db_password" {}

variable "subnet_ids" {}
variable "db_security_group" {}

locals {
  db_name = var.is_production? "kpinetworkdb" : "${var.environment}-kpinetworkdb"
  db_subnet_group_name = var.is_production ? "kpinetwork" : "${var.environment}-kpinetwork"
}
