
output "lambdas_invoke_arns" {
  value = {
    "minimal_lambda_function": aws_lambda_function.minimal_lambda_function.invoke_arn
  }
}