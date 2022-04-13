# ----------------------------------------------------------------------------------------------------------------------
# API GATEWAY REST API
# @param name Name of the REST API
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_api_gateway_rest_api" "api" {
  name =  var.is_production? var.api_name : "${var.environment}_${var.api_name}"
  binary_media_types = ["application/octet-stream"]
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

resource "aws_api_gateway_resource" "public_companies" {
  path_part   = "public"
  parent_id   = aws_api_gateway_resource.companies.id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_resource" "company" {
  path_part   = "{id}"
  parent_id   = aws_api_gateway_resource.companies.id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_resource" "universe_overview" {
  path_part   = "universe_overview"
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_resource" "company_report_vs_peers" {
  path_part   = "company_report"
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_resource" "company_report_vs_peers_id" {
  path_part   = "{company_id}"
  parent_id   = aws_api_gateway_resource.company_report_vs_peers.id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_resource" "comparison_vs_peers" {
  path_part   = "comparison"
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_resource" "comparison_vs_peers_id" {
  path_part   = "{company_id}"
  parent_id   = aws_api_gateway_resource.comparison_vs_peers.id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_resource" "download_comparison_vs_peers" {
  path_part   = "download"
  parent_id   = aws_api_gateway_resource.comparison_vs_peers_id.id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_resource" "users" {
  path_part   = "users"
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_resource" "user" {
  path_part   = "{username}"
  parent_id   = aws_api_gateway_resource.users.id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_resource" "user_roles" {
  path_part   = "roles"
  parent_id   = aws_api_gateway_resource.user.id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_resource" "company_permissions" {
  path_part   = "company_permissions"
  parent_id   = aws_api_gateway_resource.user.id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_resource" "roles" {
  path_part   = "roles"
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_resource" "change_company_publicly" {
  path_part   = "change_company_publicly"
  parent_id   = aws_api_gateway_resource.companies.id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_resource" "upload_file_s3" {
  path_part   = "upload_file"
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
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
  authorization = "CUSTOM"
  authorizer_id = aws_api_gateway_authorizer.kpi_authorizer.id
  
  request_parameters = {
    "method.request.querystring.offset" = false
    "method.request.querystring.limit" = false
  }
}

resource "aws_api_gateway_method" "get_all_public_companies_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.public_companies.id
  http_method   = "GET"
  authorization = "CUSTOM"
  authorizer_id = aws_api_gateway_authorizer.kpi_authorizer.id
  
  request_parameters = {
    "method.request.querystring.offset" = false
    "method.request.querystring.limit" = false
  }
}

resource "aws_api_gateway_method" "get_company_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.company.id
  http_method   = "GET"
  authorization = "CUSTOM"
  authorizer_id = aws_api_gateway_authorizer.kpi_authorizer.id
}

resource "aws_api_gateway_method" "get_universe_overview_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.universe_overview.id
  http_method   = "GET"
  authorization = "CUSTOM"
  authorizer_id = aws_api_gateway_authorizer.kpi_authorizer.id

  request_parameters = {
    "method.request.querystring.vertical" = false
    "method.request.querystring.sector" = false
    "method.request.querystring.investor_profile" = false
    "method.request.querystring.growth_profile" = false
    "method.request.querystring.size" = false
    "method.request.querystring.year" = false
  }
}

resource "aws_api_gateway_method" "get_company_report_vs_peers_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.company_report_vs_peers_id.id
  http_method   = "GET"
  authorization = "CUSTOM"
  authorizer_id = aws_api_gateway_authorizer.kpi_authorizer.id

  request_parameters = {
    "method.request.querystring.vertical" = false
    "method.request.querystring.sector" = false
    "method.request.querystring.investor_profile" = false
    "method.request.querystring.growth_profile" = false
    "method.request.querystring.size" = false
    "method.request.querystring.year" = false
  }
}

resource "aws_api_gateway_method" "get_comparison_vs_peers_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.comparison_vs_peers_id.id
  http_method   = "GET"
  authorization = "CUSTOM"
  authorizer_id = aws_api_gateway_authorizer.kpi_authorizer.id

  request_parameters = {
    "method.request.querystring.vertical" = false
    "method.request.querystring.sector" = false
    "method.request.querystring.investor_profile" = false
    "method.request.querystring.growth_profile" = false
    "method.request.querystring.size" = false
    "method.request.querystring.year" = false
    "method.request.querystring.from_main" = false
  }
}

resource "aws_api_gateway_method" "download_comparison_vs_peers_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.download_comparison_vs_peers.id
  http_method   = "GET"
  authorization = "CUSTOM"
  authorizer_id = aws_api_gateway_authorizer.kpi_authorizer.id

  request_parameters = {
    "method.request.querystring.vertical" = false
    "method.request.querystring.sector" = false
    "method.request.querystring.investor_profile" = false
    "method.request.querystring.growth_profile" = false
    "method.request.querystring.size" = false
    "method.request.querystring.year" = false
    "method.request.querystring.from_main" = false
  }
}

resource "aws_api_gateway_method" "get_users_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.users.id
  http_method   = "GET"
  authorization = "CUSTOM"
  authorizer_id = aws_api_gateway_authorizer.kpi_authorizer.id

    request_parameters = {
    "method.request.querystring.token" = false
    "method.request.querystring.limit" = false
  }
}

resource "aws_api_gateway_method" "get_user_details_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.user.id
  http_method   = "GET"
  authorization = "CUSTOM"
  authorizer_id = aws_api_gateway_authorizer.kpi_authorizer.id
}

resource "aws_api_gateway_method" "change_user_role_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.user_roles.id
  http_method   = "PUT"
  authorization = "CUSTOM"
  authorizer_id = aws_api_gateway_authorizer.kpi_authorizer.id
}

resource "aws_api_gateway_method" "assign_company_permissions_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.company_permissions.id
  http_method   = "PUT"
  authorization = "CUSTOM"
  authorizer_id = aws_api_gateway_authorizer.kpi_authorizer.id
}

resource "aws_api_gateway_method" "get_company_permissions_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.company_permissions.id
  http_method   = "GET"
  authorization = "CUSTOM"
  authorizer_id = aws_api_gateway_authorizer.kpi_authorizer.id
}

resource "aws_api_gateway_method" "get_roles_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.roles.id
  http_method   = "GET"
  authorization = "CUSTOM"
  authorizer_id = aws_api_gateway_authorizer.kpi_authorizer.id
}

resource "aws_api_gateway_method" "change_company_publicly_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.change_company_publicly.id
  http_method   = "PUT"
  authorization = "CUSTOM"
  authorizer_id = aws_api_gateway_authorizer.kpi_authorizer.id
}

resource "aws_api_gateway_method" "upload_file_s3_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.upload_file_s3.id
  http_method   = "POST"
  authorization = "CUSTOM"
  authorizer_id = aws_api_gateway_authorizer.kpi_authorizer.id
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

resource "aws_api_gateway_integration" "public_companies_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.public_companies.id
  http_method             = aws_api_gateway_method.get_all_public_companies_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambdas_functions_arn.get_all_public_companies_lambda_function
}

resource "aws_api_gateway_integration" "company_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.company.id
  http_method             = aws_api_gateway_method.get_company_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambdas_functions_arn.get_company_lambda_function
}

resource "aws_api_gateway_integration" "universe_overview_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.universe_overview.id
  http_method             = aws_api_gateway_method.get_universe_overview_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambdas_functions_arn.get_universe_overview_lambda_function
}

resource "aws_api_gateway_integration" "company_report_vs_peers_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.company_report_vs_peers_id.id
  http_method             = aws_api_gateway_method.get_company_report_vs_peers_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambdas_functions_arn.get_company_report_vs_peers_lambda_function
}

resource "aws_api_gateway_integration" "comparison_vs_peers_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.comparison_vs_peers_id.id
  http_method             = aws_api_gateway_method.get_comparison_vs_peers_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambdas_functions_arn.get_comparison_vs_peers_lambda_function
}

resource "aws_api_gateway_integration" "download_comparison_vs_peers_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.download_comparison_vs_peers.id
  http_method             = aws_api_gateway_method.download_comparison_vs_peers_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambdas_functions_arn.download_comparison_vs_peers_lambda_function
}

resource "aws_api_gateway_integration" "users_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.users.id
  http_method             = aws_api_gateway_method.get_users_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambdas_functions_arn.get_users_lambda_function
}

resource "aws_api_gateway_integration" "user_details_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.user.id
  http_method             = aws_api_gateway_method.get_user_details_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambdas_functions_arn.get_user_details_lambda_function
}

resource "aws_api_gateway_integration" "change_user_role_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.user_roles.id
  http_method             = aws_api_gateway_method.change_user_role_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambdas_functions_arn.change_user_role_lambda_function
}

resource "aws_api_gateway_integration" "assign_company_permissions_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.company_permissions.id
  http_method             = aws_api_gateway_method.assign_company_permissions_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambdas_functions_arn.assign_company_permissions_lambda_function
}

resource "aws_api_gateway_integration" "get_company_permissions_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.company_permissions.id
  http_method             = aws_api_gateway_method.get_company_permissions_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambdas_functions_arn.get_company_permissions_lambda_function
}

resource "aws_api_gateway_integration" "get_roles_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.roles.id
  http_method             = aws_api_gateway_method.get_roles_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambdas_functions_arn.get_roles_lambda_function
}

resource "aws_api_gateway_integration" "change_company_publicly_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.change_company_publicly.id
  http_method             = aws_api_gateway_method.change_company_publicly_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambdas_functions_arn.change_company_publicly_lambda_function
}

resource "aws_api_gateway_integration" "upload_file_s3_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.upload_file_s3.id
  http_method             = aws_api_gateway_method.upload_file_s3_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambdas_functions_arn.upload_file_s3_lambda_function
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

# ----------------------------------------------------------------------------------------------------------------------
# API GATEWAY AUTHORIZER
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_api_gateway_authorizer" "kpi_authorizer" {
  name                   = "${var.environment}_kpi_authorizer"
  rest_api_id            = aws_api_gateway_rest_api.api.id
  authorizer_uri         = var.lambdas_functions_arn.authorize_lambda_function
  authorizer_credentials = var.apigw_invokes_role_arn.authorize_lambda_invoke_role_arn
}