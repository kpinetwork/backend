# ----------------------------------------------------------------------------------------------------------------------
# API GATEWAY REST API
# @param name Name of the REST API
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_api_gateway_rest_api" "api" {
  name =  var.is_production? var.api_name : "${var.environment}_${var.api_name}"
}

# ----------------------------------------------------------------------------------------------------------------------
# API GATEWAY RESOURCE
# Provides an API Gateway Resource
# @param path_part The last path segment of this API resource.
# @param parent_id  The ID of the parent API resource
# @param rest_api_id  The ID of the associated REST API
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_api_gateway_resource" "companies" {
  path_part   = "companies"
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_resource" "company" {
  path_part   = "{id}"
  parent_id   = aws_api_gateway_resource.companies.id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_resource" "scenarios" {
  path_part   = "scenarios"
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_resource" "scenario_company" {
  path_part   = "company"
  parent_id   = aws_api_gateway_resource.scenarios.id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_resource" "scenarios_company_id" {
  path_part   = "{company_id}"
  parent_id   = aws_api_gateway_resource.scenario_company.id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_resource" "scenarios_list" {
  path_part   = "list"
  parent_id   = aws_api_gateway_resource.scenarios.id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_resource" "metrics" {
  path_part   = "metrics"
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_resource" "company_metric" {
  path_part   = "company"
  parent_id   = aws_api_gateway_resource.metrics.id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_resource" "metric" {
  path_part   = "{company_id}"
  parent_id   = aws_api_gateway_resource.company_metric.id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_resource" "average_metrics" {
  path_part   = "avg"
  parent_id   = aws_api_gateway_resource.metric.id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_resource" "metric_cohort" {
  path_part   = "cohort"
  parent_id   = aws_api_gateway_resource.metrics.id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_resource" "metric_cohort_id" {
  path_part   = "{cohort_id}"
  parent_id   = aws_api_gateway_resource.metric_cohort.id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_resource" "cohort_average_metric" {
  path_part   = "avg"
  parent_id   = aws_api_gateway_resource.metric_cohort_id.id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_resource" "cohort_metrics" {
  path_part   = "serie"
  parent_id   = aws_api_gateway_resource.metric_cohort_id.id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_resource" "company_revenue" {
  path_part   = "company-revenue"
  parent_id   = aws_api_gateway_resource.companies.id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_resource" "cohorts" {
  path_part   = "cohorts"
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_resource" "cohort" {
  path_part   = "{id}"
  parent_id   = aws_api_gateway_resource.cohorts.id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_resource" "cohort_scenarios" {
  path_part   = "scenarios"
  parent_id   = aws_api_gateway_resource.cohort.id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_resource" "cohort_revenue" {
  path_part   = "cohort-revenue"
  parent_id   = aws_api_gateway_resource.cohorts.id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_resource" "universe_overview" {
  path_part   = "universe_overview"
  parent_id   = aws_api_gateway_resource.companies.id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

# ----------------------------------------------------------------------------------------------------------------------
# API GATEWAY METHOD
# Provides a HTTP Method for an API Gateway Resource.
# @param rest_api_id The ID of the associated REST API
# @param resource_id  The API resource ID
# @param http_method  The HTTP Method
# @param authorization  The type of authorization used for the method
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_api_gateway_method" "get_all_companies_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.companies.id
  http_method   = "GET"
  authorization = "NONE"
  
  request_parameters = {
    "method.request.querystring.offset" = false
    "method.request.querystring.limit" = false
  }
}

resource "aws_api_gateway_method" "get_company_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.company.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "get_scenarios_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.scenarios.id
  http_method   = "GET"
  authorization = "NONE"
  request_parameters = {
    "method.request.querystring.offset" = false
    "method.request.querystring.limit" = false
  }
}

resource "aws_api_gateway_method" "get_company_scenarios_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.scenarios_company_id.id
  http_method   = "GET"
  authorization = "NONE"
  request_parameters = {
    "method.request.querystring.scenario_type" = false
    "method.request.querystring.offset" = false
    "method.request.querystring.limit" = false
  }
}

resource "aws_api_gateway_method" "list_scenarios_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.scenarios_list.id
  http_method   = "GET"
  authorization = "NONE"

  request_parameters = {
    "method.request.querystring.company_id" = false
    "method.request.querystring.offset" = false
    "method.request.querystring.limit" = false
  }
}

resource "aws_api_gateway_method" "get_metrics_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.metrics.id
  http_method   = "GET"
  authorization = "NONE"

  request_parameters = {
    "method.request.querystring.offset" = false
    "method.request.querystring.limit" = false
  }
}

resource "aws_api_gateway_method" "get_metric_by_company_id_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.metric.id
  http_method   = "GET"
  authorization = "NONE"

  request_parameters = {
    "method.request.querystring.name" = false
    "method.request.querystring.scenario_type" = false
  }
}

resource "aws_api_gateway_method" "get_average_metrics_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.average_metrics.id
  http_method   = "GET"
  authorization = "NONE"

  request_parameters = {
    "method.request.querystring.name" = true
  }
}

resource "aws_api_gateway_method" "get_metrics_by_cohort_id_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.cohort_metrics.id
  http_method   = "GET"
  authorization = "NONE"

  request_parameters = {
    "method.request.querystring.name" = false
    "method.request.querystring.scenario_type" = false
  }
}

resource "aws_api_gateway_method" "get_average_metrics_by_cohort_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.cohort_average_metric.id
  http_method   = "GET"
  authorization = "NONE"

  request_parameters = {
    "method.request.querystring.name" = true
  }
}

resource "aws_api_gateway_method" "get_revenue_sum_by_company_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.company_revenue.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "get_cohorts_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.cohorts.id
  http_method   = "GET"
  authorization = "NONE"

  request_parameters = {
    "method.request.querystring.offset" = false
    "method.request.querystring.limit" = false
  }
}

resource "aws_api_gateway_method" "get_cohort_by_id_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.cohort.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "get_cohort_scenarios_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.cohort_scenarios.id
  http_method   = "GET"
  authorization = "NONE"

  request_parameters = {
    "method.request.querystring.offset" = false
    "method.request.querystring.limit" = false
    "method.request.querystring.scenario_type" = false
    "method.request.querystring.year" = false
  }
}

resource "aws_api_gateway_method" "get_revenue_sum_by_cohort_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.cohort_revenue.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "get_universe_overview_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.universe_overview.id
  http_method   = "GET"
  authorization = "NONE"

  request_parameters = {
    "method.request.querystring.vertical" = false
    "method.request.querystring.sector" = false
    "method.request.querystring.year" = false
  }
}

# ----------------------------------------------------------------------------------------------------------------------
# API GATEWAY INTEGRATION
# Provides an HTTP Method Integration for an API Gateway Integration.
# @param rest_api_id The ID of the associated REST API
# @param resource_id  The API resource ID
# @param http_method The HTTP method (GET, POST, PUT, DELETE, HEAD, OPTION, ANY) when calling the associated resource.
# @param integration_http_method  The integration HTTP method, Lambda function can only be invoked via POST
# @param type   The integration input's type.
# @param uri  The input's URI
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_api_gateway_integration" "companies_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.companies.id
  http_method             = aws_api_gateway_method.get_all_companies_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambdas_functions_arn.get_all_companies_lambda_function
}

resource "aws_api_gateway_integration" "company_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.company.id
  http_method             = aws_api_gateway_method.get_company_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambdas_functions_arn.get_company_lambda_function
}

resource "aws_api_gateway_integration" "metrics_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.metrics.id
  http_method             = aws_api_gateway_method.get_metrics_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambdas_functions_arn.get_metrics_lambda_function
}

resource "aws_api_gateway_integration" "metric_by_company_id_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.metric.id
  http_method             = aws_api_gateway_method.get_metric_by_company_id_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambdas_functions_arn.get_metric_by_company_id_lambda_function
}

resource "aws_api_gateway_integration" "average_metrics_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.average_metrics.id
  http_method             = aws_api_gateway_method.get_average_metrics_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambdas_functions_arn.get_average_metrics_lambda_function
}

resource "aws_api_gateway_integration" "cohort_average_metrics_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.cohort_average_metric.id
  http_method             = aws_api_gateway_method.get_average_metrics_by_cohort_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambdas_functions_arn.get_average_metrics_by_cohort_lambda_function
}

resource "aws_api_gateway_integration" "metrics_by_cohort_id_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.cohort_metrics.id
  http_method             = aws_api_gateway_method.get_metrics_by_cohort_id_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambdas_functions_arn.get_metrics_by_cohort_id_lambda_function
}

resource "aws_api_gateway_integration" "scenarios_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.scenarios.id
  http_method             = aws_api_gateway_method.get_scenarios_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambdas_functions_arn.get_scenarios_lambda_function
}

resource "aws_api_gateway_integration" "company_scenarios_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.scenarios_company_id.id
  http_method             = aws_api_gateway_method.get_company_scenarios_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambdas_functions_arn.get_company_scenarios_lambda_function
}

resource "aws_api_gateway_integration" "scenarios_list_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.scenarios_list.id
  http_method             = aws_api_gateway_method.list_scenarios_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambdas_functions_arn.list_scenarios_lambda_function
}

resource "aws_api_gateway_integration" "revenue_sum_by_company_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.company_revenue.id
  http_method             = aws_api_gateway_method.get_revenue_sum_by_company_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambdas_functions_arn.get_revenue_sum_by_company_lambda_function
}

resource "aws_api_gateway_integration" "cohorts_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.cohorts.id
  http_method             = aws_api_gateway_method.get_cohorts_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambdas_functions_arn.get_cohorts_lambda_function
}

resource "aws_api_gateway_integration" "cohort_by_id_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.cohort.id
  http_method             = aws_api_gateway_method.get_cohort_by_id_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambdas_functions_arn.get_cohort_by_id_lambda_function
}

resource "aws_api_gateway_integration" "cohort_scenarios_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.cohort_scenarios.id
  http_method             = aws_api_gateway_method.get_cohort_scenarios_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambdas_functions_arn.get_cohort_scenarios_lambda_function
}

resource "aws_api_gateway_integration" "revenue_sum_by_cohort_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.cohort_revenue.id
  http_method             = aws_api_gateway_method.get_revenue_sum_by_cohort_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambdas_functions_arn.get_revenue_sum_by_cohort_lambda_function
}

resource "aws_api_gateway_integration" "universe_overview_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.universe_overview.id
  http_method             = aws_api_gateway_method.get_universe_overview_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambdas_functions_arn.get_universe_overview_lambda_function
}

# ----------------------------------------------------------------------------------------------------------------------
# API GATEWAY DOMAIN
# Manages domain SSL certificate
# @param domain_name Domain name
# @param certificate_arn  SSL certificate arn
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_api_gateway_domain_name" "domain" {
  domain_name     = var.domain_name
  certificate_arn = var.certificate_arn
}

# ----------------------------------------------------------------------------------------------------------------------
# API GATEWAY BASE MAPPING
# Manages an API Gateway domain association.
# @param api_id Api identifier
# @param stage_name  Association between stage and custom domain name
# @param domain_name  Domain name
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_api_gateway_base_path_mapping" "domain_mapping" {
  api_id      = aws_api_gateway_rest_api.api.id
  stage_name  = var.gateway_deployment.stage_name
  domain_name = aws_api_gateway_domain_name.domain.domain_name
  depends_on  = [var.gateway_deployment]
}