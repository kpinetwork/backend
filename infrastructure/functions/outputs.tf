output "lambdas_invoke_arns" {
  value = {
    "get_company_lambda_function": aws_lambda_function.get_company_lambda_function.invoke_arn
    "get_all_companies_lambda_function": aws_lambda_function.get_all_companies_lambda_function.invoke_arn
    "get_metrics_lambda_function": aws_lambda_function.get_metrics_function.invoke_arn
    "get_metric_by_company_id_lambda_function": aws_lambda_function.get_metric_by_company_id_function.invoke_arn
    "get_average_metrics_lambda_function": aws_lambda_function.get_average_metrics_function.invoke_arn
    "get_average_metrics_by_cohort_lambda_function": aws_lambda_function.get_average_metrics_by_cohort_function.invoke_arn
    "get_metrics_by_cohort_id_lambda_function": aws_lambda_function.get_metrics_by_cohort_id_function.invoke_arn
    "get_scenarios_lambda_function" : aws_lambda_function.get_scenarios_lambda_function.invoke_arn
    "get_company_scenarios_lambda_function" : aws_lambda_function.get_company_scenarios_lambda_function.invoke_arn
    "list_scenarios_lambda_function" : aws_lambda_function.list_scenarios_lambda_function.invoke_arn
    "get_revenue_sum_by_company_lambda_function" : aws_lambda_function.get_revenue_sum_by_company_lambda_function.invoke_arn
    "get_cohorts_lambda_function": aws_lambda_function.get_cohorts_function.invoke_arn
    "get_cohort_by_id_lambda_function": aws_lambda_function.get_cohort_by_id_function.invoke_arn
    "get_cohort_scenarios_lambda_function": aws_lambda_function.get_cohorts_scenarios_function.invoke_arn
    "get_revenue_sum_by_cohort_lambda_function" : aws_lambda_function.get_revenue_sum_by_cohort_lambda_function.invoke_arn
    "get_universe_overview_lambda_function": aws_lambda_function.get_universe_overview_lambda_function.invoke_arn
    "get_company_report_vs_peers_lambda_function": aws_lambda_function.get_company_report_vs_peers_lambda_function.invoke_arn
    "get_comparison_vs_peers_lambda_function": aws_lambda_function.get_comparison_vs_peers_lambda_function.invoke_arn
    "add_user_to_customer_group_lambda_function": aws_lambda_function.add_user_to_customer_group_lambda_function.invoke_arn
    "authorize_lambda_function": aws_lambda_function.authorize_lambda_function.invoke_arn
    "verify_users_with_same_email_lambda_function": aws_lambda_function.verify_users_with_same_email_lambda_function.invoke_arn
    "get_users_lambda_function": aws_lambda_function.get_users_lambda_function.invoke_arn
    "get_roles_lambda_function": aws_lambda_function.get_roles_lambda_function.invoke_arn
    "get_user_details_lambda_function": aws_lambda_function.get_user_details_lambda_function.invoke_arn
    "assign_company_permissions_lambda_function": aws_lambda_function.assign_company_permissions_lambda_function.invoke_arn
    "make_data_public_lambda_function": aws_lambda_function.make_data_public_lambda_function.invoke_arn
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