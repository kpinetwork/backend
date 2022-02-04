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

    "apigw_get_universe_overview_lambda_function": {
      resource_path: aws_api_gateway_resource.universe_overview.path,
      http_method: aws_api_gateway_method.get_universe_overview_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_company_report_vs_peers_lambda_function": {
      resource_path: aws_api_gateway_resource.company_report_vs_peers_id.path,
      http_method: aws_api_gateway_method.get_company_report_vs_peers_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_comparison_vs_peers_lambda_function": {
      resource_path: aws_api_gateway_resource.comparison_vs_peers_id.path,
      http_method: aws_api_gateway_method.get_comparison_vs_peers_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_users_lambda_function": {
      resource_path: aws_api_gateway_resource.users.path,
      http_method: aws_api_gateway_method.get_users_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_roles_lambda_function": {
      resource_path: aws_api_gateway_resource.roles.path,
      http_method: aws_api_gateway_method.get_roles_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_user_details_lambda_function": {
      resource_path: aws_api_gateway_resource.user.path,
      http_method: aws_api_gateway_method.get_user_details_method.http_method,
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