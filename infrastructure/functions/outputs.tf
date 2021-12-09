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
  }
}

output "lambdas_arns" {
  value = {
    "glue_trigger_lambda_function" : aws_lambda_function.glue_trigger_lambda_function.arn
  }
}