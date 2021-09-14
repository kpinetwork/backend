output "lambda_exec_role_arn" {
  value = aws_iam_role.lambda_exec_role.arn
}

output "aws_iam_role_policy_attachment_logs" {
  value = aws_iam_role_policy_attachment.lambda_logs
}


