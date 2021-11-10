output "api_gateway_references" {
  value = {
    "apigw_get_all_companies_lambda_function": {
      resource_path: aws_api_gateway_resource.companies.path,
      http_method: aws_api_gateway_method.get_all_companies_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_company_lambda_function": {
      resource_path: aws_api_gateway_resource.company.path,
      http_method: aws_api_gateway_method.get_company_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_metrics_lambda_function": {
      resource_path: aws_api_gateway_resource.metrics.path,
      http_method: aws_api_gateway_method.get_metrics_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_metric_by_company_id_lambda_function": {
      resource_path: aws_api_gateway_resource.metric.path,
      http_method: aws_api_gateway_method.get_metric_by_company_id_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }
  }
}

output "api_gateway_domain" {
  value = aws_api_gateway_domain_name.domain
}