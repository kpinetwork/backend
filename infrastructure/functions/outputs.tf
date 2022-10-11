output "lambdas_invoke_arns" {
  value = {
    "get_company_details_lambda_function": aws_lambda_function.get_company_details_lambda_function.invoke_arn
    "get_all_companies_lambda_function": aws_lambda_function.get_all_companies_lambda_function.invoke_arn
    "get_all_public_companies_lambda_function": aws_lambda_function.get_all_public_companies_lambda_function.invoke_arn
    "get_universe_overview_lambda_function": aws_lambda_function.get_universe_overview_lambda_function.invoke_arn
    "get_company_report_vs_peers_lambda_function": aws_lambda_function.get_company_report_vs_peers_lambda_function.invoke_arn
    "get_comparison_vs_peers_lambda_function": aws_lambda_function.get_comparison_vs_peers_lambda_function.invoke_arn
    "download_comparison_vs_peers_lambda_function": aws_lambda_function.download_comparison_vs_peers_lambda_function.invoke_arn
    "get_by_metric_report_lambda_function": aws_lambda_function.get_by_metric_report_lambda_function.invoke_arn
    "get_dynamic_report_lambda_function": aws_lambda_function.get_dynamic_report_lambda_function.invoke_arn
    "add_user_to_customer_group_lambda_function": aws_lambda_function.add_user_to_customer_group_lambda_function.invoke_arn
    "authorize_lambda_function": aws_lambda_function.authorize_lambda_function.invoke_arn
    "verify_users_with_same_email_lambda_function": aws_lambda_function.verify_users_with_same_email_lambda_function.invoke_arn
    "get_users_lambda_function": aws_lambda_function.get_users_lambda_function.invoke_arn
    "get_roles_lambda_function": aws_lambda_function.get_roles_lambda_function.invoke_arn
    "get_user_details_lambda_function": aws_lambda_function.get_user_details_lambda_function.invoke_arn
    "change_user_role_lambda_function": aws_lambda_function.change_user_role_lambda_function.invoke_arn
    "assign_company_permissions_lambda_function": aws_lambda_function.assign_company_permissions_lambda_function.invoke_arn
    "get_company_permissions_lambda_function": aws_lambda_function.get_company_permissions_lambda_function.invoke_arn
    "change_company_publicly_lambda_function": aws_lambda_function.change_company_publicly_lambda_function.invoke_arn
    "upload_file_s3_lambda_function": aws_lambda_function.upload_file_s3_lambda_function.invoke_arn
    "connect_lambda_function": aws_lambda_function.connect_lambda_function.invoke_arn
    "disconnect_lambda_function": aws_lambda_function.disconnect_lambda_function.invoke_arn
    "message_lambda_function": aws_lambda_function.message_lambda_function.invoke_arn
    "register_lambda_function": aws_lambda_function.register_lambda_function.invoke_arn
    "validate_data_lambda_function": aws_lambda_function.validate_data_lambda_function.invoke_arn
    "get_company_investments_lambda_function": aws_lambda_function.get_company_investments_lambda_function.invoke_arn
    "add_investment_lambda_function": aws_lambda_function.add_investment_lambda_function.invoke_arn
    "update_data_lambda_function": aws_lambda_function.update_data_lambda_function.invoke_arn
    "add_scenario_lambda_function": aws_lambda_function.add_scenario_lambda_function.invoke_arn
    "edit_modify_data_lambda_function": aws_lambda_function.edit_modify_data_lambda_function.invoke_arn
    "get_edit_modify_data_lambda_function": aws_lambda_function.get_edit_modify_data_lambda_function.invoke_arn
    "delete_scenarios_lambda_function": aws_lambda_function.delete_scenarios_lambda_function.invoke_arn
    "delete_company_lambda_function": aws_lambda_function.delete_company_lambda_function.invoke_arn
    "get_metric_types_lambda_function": aws_lambda_function.get_metric_types_lambda_function.invoke_arn
    "get_investment_date_report_lambda_function": aws_lambda_function.get_investment_date_report_lambda_function.invoke_arn
    "get_all_tags_lambda_function": aws_lambda_function.get_all_tags_lambda_function.invoke_arn
  }
}

output "lambda_trigger_arns"{
  value = {
    "add_user_to_customer_group_lambda_function": aws_lambda_function.add_user_to_customer_group_lambda_function.arn
    "verify_users_with_same_email_lambda_function": aws_lambda_function.verify_users_with_same_email_lambda_function.arn
  }
}

output "lambdas_arns" {
  value = {
    "glue_trigger_lambda_function" : aws_lambda_function.glue_trigger_lambda_function.arn
  }
}