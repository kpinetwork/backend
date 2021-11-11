# ----------------------------------------------------------------------------------------------------------------------
# AWS CREDENTIALS
# ----------------------------------------------------------------------------------------------------------------------

variable "aws_access_key_id" {
  description = "AWS access key credential"
  sensitive = true
}

variable "aws_secret_access_key" {
  description = "AWS secret access key credential"
  sensitive = true
}

variable "region" {
  default = "us-west-2"
}

variable "aws_account_id" {
  description = "AWS account id"
  sensitive = true
}

variable "root_domain_name" {
  default = "kpinetwork.com"
}

# ----------------------------------------------------------------------------------------------------------------------
# LAMBDAS NAMES
# ----------------------------------------------------------------------------------------------------------------------

variable "lambdas_names" {
  default = {
    "get_company_lambda_function": "get_company_lambda_function"
    "get_all_companies_lambda_function": "get_all_companies_lambda_function"
    "get_metric_by_company_id_lambda_function": "get_metric_by_company_id_lambda_function"
    "get_metrics_lambda_function": "get_metrics_lambda_function"
    "glue_trigger_lambda_function": "glue_trigger_lambda_function"
    "get_company_scenarios_lambda_function": "get_company_scenarios_lambda_function"
<<<<<<< HEAD
    "list_scenarios_lambda_function": "list_scenarios_lambda_function",
    "get_revenue_sum_by_company_lambda_function": "get_revenue_sum_by_company_lambda_function"
    "get_cohort_by_id_lambda_function": "get_cohort_by_id_lambda_function"
    "get_cohorts_lambda_function": "get_cohorts_lambda_function"
    "get_cohort_scenarios_lambda_function": "get_cohort_scenarios_lambda_function"
=======
    "list_scenarios_lambda_function": "list_scenarios_lambda_function"
>>>>>>> 7317739 (feat: KPI-52-financial-scenarios (#34))
  }
}

# ----------------------------------------------------------------------------------------------------------------------
# DATABASE VARIABLES
# ----------------------------------------------------------------------------------------------------------------------

variable "db_username" {
  description = "KPI Network database root username"
  type = string
  sensitive = true
}

variable "db_prod_password" {
  description = "KPI Network prod database root user password"
  type = string
  sensitive = true
}

variable "db_demo_password" {
  description = "KPI Network demo database root user password"
  type = string
  sensitive = true
}

# ----------------------------------------------------------------------------------------------------------------------
# CODEBUILD VARIABLES
# ----------------------------------------------------------------------------------------------------------------------

variable "git_token" {
  description = "Git token to access codebuild"
  type = string
  sensitive = true
}

# ----------------------------------------------------------------------------------------------------------------------
# REMOTE DATA SOURCE VARIABLES
# ----------------------------------------------------------------------------------------------------------------------


variable "backend" {
  default     = "s3"
}

# ----------------------------------------------------------------------------------------------------------------------
# LOCAL VARIABLES
# ----------------------------------------------------------------------------------------------------------------------

variable "bucket_files" {
  default = "kpinetwork-files"
}

locals {
  environment = terraform.workspace
  is_production = local.environment == "prod"

  db_password = {
    "prod" = var.db_prod_password
    "demo" = var.db_demo_password
  }
  
  domains = {
    "root" = var.root_domain_name
    "prod" = "api.${var.root_domain_name}"
    "demo" = "api.demo.${var.root_domain_name}"
  }

  prod_certs = [
    local.domains.prod
  ]
  demo_certs = [
    local.domains.demo
  ]
  cert_sans = local.is_production ? local.prod_certs : local.demo_certs

  remote_state_config = {
      bucket      = "kpinetwork-infrastructure"
      key         = "key/terraform.tfstate"
      region      = "us-west-2"
      access_key = var.aws_access_key_id
      secret_key = var.aws_secret_access_key
  }
}