output "id" {
  value  = aws_cognito_user_pool.pool.id
}

output "client_ids" {
  value  = aws_cognito_user_pool_client.client.id
}
