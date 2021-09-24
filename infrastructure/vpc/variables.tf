variable "region" {}

variable "vpc_name" {
    default = "kpinetworks_vpc"
}

variable "security_group_name" {
    default = "kpinetwokrs_rds_group"
}

variable "security_group_name_lambda" {
    default = "kpinetwokrs_lambda_group"
}