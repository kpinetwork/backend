# ----------------------------------------------------------------------------------------------------------------------
# CLOUDWATCH GROUPS
# @param name The name of the log group
# @param retention_in_days Specifies the number of days you want to retain log events in the specified log group
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_cloudwatch_log_group" "get_company_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}/${var.lambdas_names.get_company_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "get_all_companyies_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}/${var.lambdas_names.get_all_companies_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "codebuild_rds_migrations" {
  name = "${var.prefix_codebuild_cloudwatch_log_group}${var.environment}/${var.codebuild_project_name}"
  retention_in_days = var.retention_days
  tags = {
      Name = "${var.prefix_codebuild_cloudwatch_log_group}${var.environment}/${var.codebuild_project_name}"
      Environment   =  var.environment
  }
}