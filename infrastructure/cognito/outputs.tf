output "id" {
  value  = aws_cognito_user_pool.pool.id
}

output "amplify_client_id" {
  value  = aws_cognito_user_pool_client.amplify.id
}

output "cognito_arn" {
  value = aws_cognito_user_pool.pool.arn
}
