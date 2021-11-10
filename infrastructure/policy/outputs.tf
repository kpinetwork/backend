
output "lambdas_exec_roles_arn" {
  value = {
      "companies_exec_role_arn": aws_iam_role.companies_lambda_exec_role.arn
      "company_exec_role_arn": aws_iam_role.company_lambda_exec_role.arn
      "metric_exec_role_arn": aws_iam_role.get_metric_by_company_id_lambda_exec_role.arn
      "metrics_exec_role_arn": aws_iam_role.get_metrics_lambda_exec_role.arn
      "glue_trigger_lambda_exec_role": aws_iam_role.glue_trigger_lambda_exec_role.arn
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
