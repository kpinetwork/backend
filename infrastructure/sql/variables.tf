variable "region" {}

variable "db_name" {
  default     = "kpinetworksdb"
}

variable "db_username" {}

variable "db_password" {}

variable "db_subnet_group_name" {
  default     = "kpinetworks"
}

variable "db_security_group" {}
