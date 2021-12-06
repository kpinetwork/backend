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

resource "aws_cloudwatch_log_group" "get_companies_kpi_average_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_companies_kpi_average_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "get_companies_count_by_size_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_companies_count_by_size_lambda_function}"
  retention_in_days = var.retention_days
}
resource "aws_cloudwatch_log_group" "get_revenue_sum_by_company_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_revenue_sum_by_company_lambda_function}"
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

resource "aws_cloudwatch_log_group" "get_metric_by_id_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_metric_by_company_id_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "get_metrics_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_metrics_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "get_average_metrics_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_average_metrics_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "get_average_metrics_by_cohort_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_average_metrics_by_cohort_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "get_metrics_by_cohort_id_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_metrics_by_cohort_id_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "get_scenarios_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_scenarios_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "get_company_scenarios_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_company_scenarios_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "list_scenarios_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.list_scenarios_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "get_cohort_by_id_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_cohort_by_id_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "get_cohort_scenarios_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_cohort_scenarios_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "get_cohorts_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_cohorts_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "get_revenue_sum_by_cohort_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_revenue_sum_by_cohort_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "get_growth_and_margin_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_growth_and_margin_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "get_expected_growth_and_margin_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_expected_growth_and_margin_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "get_revenue_and_ebitda_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_revenue_and_ebitda_lambda_function}"
  retention_in_days = var.retention_days
}
