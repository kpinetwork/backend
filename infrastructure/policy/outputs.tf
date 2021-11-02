output "lambdas_exec_roles_arn" {
  value = {
    "glue_trigger_lambda_exec_role": aws_iam_role.glue_trigger_lambda_exec_role.arn
  }
}