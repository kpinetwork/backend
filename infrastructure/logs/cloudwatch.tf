# ----------------------------------------------------------------------------------------------------------------------
# CLOUDWATCH GROUPS
# @param name The name of the log group
# @param retention_in_days Specifies the number of days you want to retain log events in the specified log group
# ----------------------------------------------------------------------------------------------------------------------
resource "aws_cloudwatch_log_group" "get_company_details_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_company_details_lambda_function}"
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

resource "aws_cloudwatch_log_group" "get_by_metric_report_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_by_metric_report_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "get_dynamic_report_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_dynamic_report_lambda_function}"
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

resource "aws_cloudwatch_log_group" "connect_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.connect_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "disconnect_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.disconnect_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "message_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.message_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "register_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.register_lambda_function}"
  retention_in_days = var.retention_days
}
resource "aws_cloudwatch_log_group" "validate_data_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.validate_data_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "get_company_investments_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_company_investments_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "add_investment_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.add_investment_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "update_data_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.update_data_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "delete_scenarios_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.delete_scenarios_lambda_function}"
  retention_in_days = var.retention_days
}
resource "aws_cloudwatch_log_group" "add_scenario_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.add_scenario_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "edit_modify_data_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.edit_modify_data_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "get_edit_modify_data_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_edit_modify_data_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "delete_company_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.delete_company_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "get_metric_types_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_metric_types_lambda_function}"
  retention_in_days = var.retention_days
}
resource "aws_cloudwatch_log_group" "get_investment_date_report_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_investment_date_report_lambda_function}"
  retention_in_days = var.retention_days
}
resource "aws_cloudwatch_log_group" "get_all_tags_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_all_tags_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "get_tags_by_company_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_tags_by_company_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "add_tag_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.add_tag_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "update_tags_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.update_tags_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "delete_tags_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.delete_tags_lambda_function}"
  retention_in_days = var.retention_days
}
resource "aws_cloudwatch_log_group" "get_all_ranges_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_all_ranges_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "get_ranges_by_metric_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_ranges_by_metric_lambda_function}"
  retention_in_days = var.retention_days
}
resource "aws_cloudwatch_log_group" "modify_ranges_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.modify_ranges_lambda_function}"
  retention_in_days = var.retention_days
}
resource "aws_cloudwatch_log_group" "get_full_year_total_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_full_year_total_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "get_quarters_report_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.environment}_${var.lambdas_names.get_quarters_report_lambda_function}"
  retention_in_days = var.retention_days
}

