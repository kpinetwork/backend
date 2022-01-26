
output "lambdas_exec_roles_arn" {
  value = {
      "companies_exec_role_arn": aws_iam_role.companies_lambda_exec_role.arn
      "company_exec_role_arn": aws_iam_role.company_lambda_exec_role.arn
      "metric_exec_role_arn": aws_iam_role.get_metric_by_company_id_lambda_exec_role.arn
      "metrics_exec_role_arn": aws_iam_role.get_metrics_lambda_exec_role.arn
      "get_average_metrics_exec_role_arn": aws_iam_role.get_average_metrics_lambda_exec_role.arn
      "get_average_metrics_by_cohort_exec_role_arn": aws_iam_role.get_average_metrics_by_cohort_lambda_exec_role.arn
      "get_metrics_by_cohort_id_exec_role_arn": aws_iam_role.get_metrics_by_cohort_id_lambda_exec_role.arn
      "glue_trigger_lambda_exec_role": aws_iam_role.glue_trigger_lambda_exec_role.arn
      "get_scenarios_exec_role_arn": aws_iam_role.get_scenarios_lambda_exec_role.arn
      "get_company_scenarios_exec_role_arn": aws_iam_role.get_company_scenarios_lambda_exec_role.arn
      "list_scenarios_exec_role_arn": aws_iam_role.list_scenarios_lambda_exec_role.arn
      "get_revenue_sum_by_company_exec_role_arn": aws_iam_role.get_revenue_sum_by_company_lambda_exec_role.arn
      "cohort_exec_role_arn": aws_iam_role.get_cohort_by_id_lambda_exec_role.arn
      "cohorts_exec_role_arn": aws_iam_role.get_cohorts_lambda_exec_role.arn
      "cohort_scenario_exec_role_arn": aws_iam_role.get_cohort_scenarios_lambda_exec_role.arn
      "get_revenue_sum_by_cohort_exec_role_arn": aws_iam_role.get_revenue_sum_by_cohort_lambda_exec_role.arn
      "get_universe_overview_exec_role_arn": aws_iam_role.get_universe_overview_lambda_exec_role.arn
      "get_company_report_vs_peers_exec_role_arn": aws_iam_role.get_company_report_vs_peers_lambda_exec_role.arn
      "get_comparison_vs_peers_exec_role_arn": aws_iam_role.get_comparison_vs_peers_lambda_exec_role.arn
      "add_user_to_customer_group_exec_role_arn": aws_iam_role.add_user_to_customer_group_lambda_exec_role.arn
      "authorize_exec_role_arn": aws_iam_role.authorize_lambda_exec_role.arn
      "verify_users_with_same_email_exec_role_arn": aws_iam_role.verify_users_with_same_email_lambda_exec_role.arn
  }
}


output "apigw_invokes_role_arn" {
  value = {
    "authorize_lambda_invoke_role_arn": aws_iam_role.authorize_lambda_invoke_role.arn
  }
}

output "aws_iam_roles_policy_attachment_logs" {
  value = {
      "companies_lambda_logs": aws_iam_role_policy_attachment.companies_lambda_logs
      "company_lambda_logs": aws_iam_role_policy_attachment.company_lambda_logs
  }
}

output "aws_iam_roles_policy_attachment_network" {
  value = {
      "companies_lambda_vpc": aws_iam_role_policy_attachment.companies_lambda_vpc
      "company_lambda_vpc": aws_iam_role_policy_attachment.company_lambda_vpc
  }
}
