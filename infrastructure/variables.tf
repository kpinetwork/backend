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
    "get_company_details_lambda_function": "get_company_details_lambda_function"
    "get_all_companies_lambda_function": "get_all_companies_lambda_function"
    "get_all_public_companies_lambda_function": "get_all_public_companies_lambda_function"
    "glue_trigger_lambda_function": "glue_trigger_lambda_function"
    "get_universe_overview_lambda_function": "get_universe_overview_lambda_function"
    "get_company_report_vs_peers_lambda_function": "get_company_report_vs_peers_lambda_function"
    "get_comparison_vs_peers_lambda_function": "get_comparison_vs_peers_lambda_function"
    "download_comparison_vs_peers_lambda_function": "download_comparison_vs_peers_lambda_function"
    "get_investment_year_report_lambda_function": "get_investment_year_report_lambda_function"
    "get_investment_date_report_lambda_function": "get_investment_date_report_lambda_function"
    "get_investment_year_options_lambda_function": "get_investment_year_options_lambda_function"
    "get_by_metric_report_lambda_function": "get_by_metric_report_lambda_function"
    "get_dynamic_report_lambda_function": "get_dynamic_report_lambda_function"
    "add_user_to_customer_group_lambda_function": "add_user_to_customer_group_lambda_function"
    "authorize_lambda_function": "authorize_lambda_function"
    "verify_users_with_same_email_lambda_function" : "verify_users_with_same_email_lambda_function"
    "get_users_lambda_function": "get_users_lambda_function"
    "get_roles_lambda_function" : "get_roles_lambda_function"
    "get_user_details_lambda_function" : "get_user_details_lambda_function"
    "change_user_role_lambda_function" : "change_user_role_lambda_function"
    "assign_company_permissions_lambda_function" : "assign_company_permissions_lambda_function"
    "get_company_permissions_lambda_function" : "get_company_permissions_lambda_function"
    "change_company_publicly_lambda_function" : "change_company_publicly_lambda_function"
    "upload_file_s3_lambda_function" : "upload_file_s3_lambda_function"
    "connect_lambda_function" : "connect_lambda_function"
    "disconnect_lambda_function" : "disconnect_lambda_function"
    "message_lambda_function" : "message_lambda_function"
    "register_lambda_function" : "register_lambda_function"
    "validate_data_lambda_function": "validate_data_lambda_function"
    "get_company_investments_lambda_function": "get_company_investments_lambda_function"
    "add_investment_lambda_function": "add_investment_lambda_function"
    "update_data_lambda_function": "update_data_lambda_function"
    "delete_scenarios_lambda_function": "delete_scenarios_lambda_function"
    "add_scenario_lambda_function": "add_scenario_lambda_function"
    "edit_modify_data_lambda_function": "edit_modify_data_lambda_function"
    "get_edit_modify_data_lambda_function": "get_edit_modify_data_lambda_function"
    "delete_company_lambda_function": "delete_company_lambda_function"
    "get_metric_types_lambda_function": "get_metric_types_lambda_function"
    "get_all_tags_lambda_function": "get_all_tags_lambda_function"
    "get_tags_by_company_lambda_function": "get_tags_by_company_lambda_function"
    "add_tag_lambda_function": "add_tag_lambda_function"
    "update_tags_lambda_function": "update_tags_lambda_function"
    "delete_tags_lambda_function": "delete_tags_lambda_function"
    "get_all_ranges_lambda_function": "get_all_ranges_lambda_function"
    "get_ranges_by_metric_lambda_function": "get_ranges_by_metric_lambda_function"
    "modify_ranges_lambda_function": "modify_ranges_lambda_function"
    "get_full_year_total_lambda_function": "get_full_year_total_lambda_function"
    "get_quarters_report_lambda_function": "get_quarters_report_lambda_function"
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

variable "comparison_file_path" {
  sensitive = true
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

  prod_callback_urls = [
    "https://app.${var.root_domain_name}"
    ]
  
  demo_callback_urls = [
    "http://localhost:3000/",
    "https://app.demo.${var.root_domain_name}"
  ]

  prod_logout_urls = [
    "https://app.${var.root_domain_name}"
    ]
  
  demo_logout_urls = [
    "http://localhost:3000/",
    "https://app.demo.${var.root_domain_name}"
  ]

  callback_urls = local.is_production ? local.prod_callback_urls : local.demo_callback_urls
  
  logout_urls = local.is_production ? local.prod_logout_urls : local.demo_logout_urls

  remote_state_config = {
      bucket      = "kpinetwork-infrastructure"
      key         = "key/terraform.tfstate"
      region      = "us-west-2"
      access_key = var.aws_access_key_id
      secret_key = var.aws_secret_access_key
  }
}