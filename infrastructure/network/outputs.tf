output "api_gateway_minimal_lambda_function" {
  value = {
    resource_path: aws_api_gateway_resource.resource.path,
    http_method: aws_api_gateway_method.method.http_method,
    api_id: aws_api_gateway_rest_api.api.id,
  }
}

output "api_gateway_domain" {
  value = aws_api_gateway_domain_name.domain
}