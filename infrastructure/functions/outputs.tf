
output "lambdas_invoke_arns" {
  value = {
    "minimal_lambda_function": aws_lambda_function.minimal_lambda_function.invoke_arn
    "db_sample_lambda_function": aws_lambda_function.db_sample_lambda_function.invoke_arn
    "glue_trigger_lambda_function": aws_lambda_function.db_sample_lambda_function.arn
  }
}