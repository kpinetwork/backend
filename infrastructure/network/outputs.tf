output "api_gateway_references" {
  value = {
    "apigw_get_all_companies_lambda_function": {
      resource_path: aws_api_gateway_resource.companies.path,
      http_method: aws_api_gateway_method.get_all_companies_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_companies_kpi_average_lambda_function": {
      resource_path: aws_api_gateway_resource.companies_kpi_average.path,
      http_method: aws_api_gateway_method.get_companies_kpi_average_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_companies_count_by_size_lambda_function": {
      resource_path: aws_api_gateway_resource.companies_count_by_size.path,
      http_method: aws_api_gateway_method.get_companies_count_by_size_method.http_method,
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

    "apigw_get_average_metrics_lambda_function": {
      resource_path: aws_api_gateway_resource.average_metrics.path,
      http_method: aws_api_gateway_method.get_average_metrics_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_average_metrics_by_cohort_lambda_function": {
      resource_path: aws_api_gateway_resource.cohort_average_metric.path,
      http_method: aws_api_gateway_method.get_average_metrics_by_cohort_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_metrics_by_cohort_id_lambda_function": {
      resource_path: aws_api_gateway_resource.cohort_metrics.path,
      http_method: aws_api_gateway_method.get_metrics_by_cohort_id_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_scenarios_lambda_function": {
      resource_path: aws_api_gateway_resource.scenarios.path,
      http_method: aws_api_gateway_method.get_scenarios_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }
    
    "apigw_get_company_scenarios_lambda_function": {
      resource_path: aws_api_gateway_resource.scenarios_company_id.path,
      http_method: aws_api_gateway_method.get_company_scenarios_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_list_scenarios_lambda_function": {
      resource_path: aws_api_gateway_resource.scenarios_list.path,
      http_method: aws_api_gateway_method.list_scenarios_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_revenue_sum_by_company_lambda_function": {
      resource_path: aws_api_gateway_resource.company_revenue.path,
      http_method: aws_api_gateway_method.get_revenue_sum_by_company_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_cohorts_lambda_function": {
      resource_path: aws_api_gateway_resource.cohorts.path,
      http_method: aws_api_gateway_method.get_cohorts_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_cohort_by_id_lambda_function": {
      resource_path: aws_api_gateway_resource.cohort.path,
      http_method: aws_api_gateway_method.get_cohort_by_id_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_cohort_scenarios_lambda_function": {
      resource_path: aws_api_gateway_resource.cohort_scenarios.path,
      http_method: aws_api_gateway_method.get_cohort_scenarios_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_revenue_sum_by_cohort_lambda_function": {
      resource_path: aws_api_gateway_resource.cohort_revenue.path,
      http_method: aws_api_gateway_method.get_revenue_sum_by_cohort_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_growth_and_margin_lambda_function": {
      resource_path: aws_api_gateway_resource.growth_and_margin.path,
      http_method: aws_api_gateway_method.get_growth_and_margin_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_expected_growth_and_margin_lambda_function": {
      resource_path: aws_api_gateway_resource.expected_growth_and_margin.path,
      http_method: aws_api_gateway_method.get_expected_growth_and_margin_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_revenue_and_ebitda_lambda_function": {
      resource_path: aws_api_gateway_resource.revenue_and_ebitda.path,
      http_method: aws_api_gateway_method.get_revenue_and_ebitda_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }
  }
}

output "api_gateway_domain" {
  value = aws_api_gateway_domain_name.domain
}

output "api_gateway_rest_api_id" {
  value = aws_api_gateway_rest_api.api.id
}