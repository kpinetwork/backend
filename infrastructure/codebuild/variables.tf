variable "codebuild_project_name" {
    default = "rds_migrations"
}

variable "environment" {}

variable "git_token" {}
variable "repository" {
    default = "https://github.com/kpinetwork/backend.git"
}

variable "codebuild_aws_iam_role" {}

variable "log_group_name" {}

variable "kpinetwork_vpc_id" {}
variable "private_subnet_a_id" {}
variable "codebuild_group_id" {}

variable "db_host" {}
variable "db_username" {}
variable "db_password" {}