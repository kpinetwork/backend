
output "lambdas_exec_roles_arn" {
  value = {
      "companies_exec_role_arn": aws_iam_role.companies_lambda_exec_role.arn
      "get_all_public_companies_exec_role_arn": aws_iam_role.get_all_public_companies_lambda_exec_role.arn
      "company_exec_role_arn": aws_iam_role.company_lambda_exec_role.arn
      "glue_trigger_lambda_exec_role": aws_iam_role.glue_trigger_lambda_exec_role.arn
      "get_universe_overview_exec_role_arn": aws_iam_role.get_universe_overview_lambda_exec_role.arn
      "get_company_report_vs_peers_exec_role_arn": aws_iam_role.get_company_report_vs_peers_lambda_exec_role.arn
      "get_comparison_vs_peers_exec_role_arn": aws_iam_role.get_comparison_vs_peers_lambda_exec_role.arn
      "download_comparison_vs_peers_exec_role_arn": aws_iam_role.download_comparison_vs_peers_lambda_exec_role.arn
      "add_user_to_customer_group_exec_role_arn": aws_iam_role.add_user_to_customer_group_lambda_exec_role.arn
      "authorize_exec_role_arn": aws_iam_role.authorize_lambda_exec_role.arn
      "verify_users_with_same_email_exec_role_arn": aws_iam_role.verify_users_with_same_email_lambda_exec_role.arn
      "get_users_exec_role_arn": aws_iam_role.get_users_lambda_exec_role.arn
      "get_roles_exec_role_arn": aws_iam_role.get_roles_lambda_exec_role.arn
      "get_user_details_exec_role_arn": aws_iam_role.get_user_details_lambda_exec_role.arn
      "change_user_role_exec_role_arn": aws_iam_role.change_user_role_lambda_exec_role.arn
      "assign_company_permissions_exec_role_arn": aws_iam_role.assign_company_permissions_lambda_exec_role.arn
      "get_company_permissions_exec_role_arn": aws_iam_role.get_company_permissions_lambda_exec_role.arn
      "change_company_publicly_exec_role_arn": aws_iam_role.change_company_publicly_lambda_exec_role.arn
      "upload_file_s3_exec_role_arn": aws_iam_role.upload_file_s3_lambda_exec_role.arn
  }
}


output "apigw_invokes_role_arn" {
  value = {
    "authorize_lambda_invoke_role_arn": aws_iam_role.authorize_lambda_invoke_role.arn
  }
}

