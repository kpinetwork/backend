output "lambdas_invoke_arns" {
  value = {
    "get_company_lambda_function" : aws_lambda_function.get_company_lambda_function.invoke_arn
    "get_all_companies_lambda_function" : aws_lambda_function.get_all_companies_lambda_function.invoke_arn
  }
}

output "lambdas_arns" {
  value = {
    "glue_trigger_lambda_function" : aws_lambda_function.glue_trigger_lambda_function.arn
  }
}