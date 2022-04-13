# ----------------------------------------------------------------------------------------------------------------------
# CLOUDWATCH GROUPS
# @param name The name of the log group
# @param retention_in_days Specifies the number of days you want to retain log events in the specified log group
# ----------------------------------------------------------------------------------------------------------------------
resource "aws_cloudwatch_log_group" "get_company_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_company_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "get_all_companies_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_all_companies_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "get_all_public_companies_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_all_public_companies_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "codebuild_rds_migrations" {
  name = "${var.prefix_codebuild_cloudwatch_log_group}${var.environment}_${var.codebuild_project_name}"
  retention_in_days = var.retention_days
  tags = {
      Name = "${var.prefix_codebuild_cloudwatch_log_group}${var.environment}_${var.codebuild_project_name}"
      Environment   =  var.environment
  }
}

resource "aws_cloudwatch_log_group" "glue_trigger_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.glue_trigger_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "get_universe_overview_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_universe_overview_lambda_function}"
  retention_in_days = var.retention_days

}

resource "aws_cloudwatch_log_group" "get_company_report_vs_peers_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_company_report_vs_peers_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "get_comparison_vs_peers_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_comparison_vs_peers_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "download_comparison_vs_peers_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.download_comparison_vs_peers_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "add_user_to_customer_group_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.add_user_to_customer_group_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "authorize_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.authorize_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "verify_users_with_same_email_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.verify_users_with_same_email_lambda_function}"
  retention_in_days = var.retention_days
}
resource "aws_cloudwatch_log_group" "get_users_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_users_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "get_roles_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_roles_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "get_user_details_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_user_details_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "change_user_role_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.change_user_role_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "assign_company_permissions_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.assign_company_permissions_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "get_company_permissions_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_company_permissions_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "change_company_publicly_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.change_company_publicly_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "upload_file_s3_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.upload_file_s3_lambda_function}"
  retention_in_days = var.retention_days
}