# ----------------------------------------------------------------------------------------------------------------------
# API GATEWAY REST API
# @param name Name of the REST API
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_api_gateway_rest_api" "api" {
  name = "myapi"
}

# ----------------------------------------------------------------------------------------------------------------------
# API GATEWAY RESOURCE
# Provides an API Gateway Resource
# @param path_part The last path segment of this API resource.
# @param parent_id  The ID of the parent API resource
# @param rest_api_id  The ID of the associated REST API
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_api_gateway_resource" "resource" {
  path_part = "resource"
  parent_id = aws_api_gateway_rest_api.api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_resource" "test" {
  path_part = "test"
  parent_id = aws_api_gateway_rest_api.api.root_resource_id
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

resource "aws_api_gateway_method" "method" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.resource.id
  http_method = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "method_sample" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.test.id
  http_method = "GET"
  authorization = "NONE"
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

resource "aws_api_gateway_integration" "integration" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.resource.id
  http_method = aws_api_gateway_method.method.http_method
  integration_http_method = "POST"
  type = "AWS_PROXY"
  uri = var.lambdas_functions_arn.minimal_lambda_function
}

resource "aws_api_gateway_integration" "integration_sample" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.test.id
  http_method = aws_api_gateway_method.method_sample.http_method
  integration_http_method = "POST"
  type = "AWS_PROXY"
  uri = var.lambdas_functions_arn.sample_lambda_function
}

# ----------------------------------------------------------------------------------------------------------------------
# API GATEWAY DEPLOYMENT
# Manages an API Gateway REST Deployment.
# @param depends_on Set of dependencies to execute the definition
# @param rest_api_id  REST API identifier.
# @param stage_name Name of the stage to create with this deployment
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_api_gateway_deployment" "example" {
  depends_on = [
    aws_api_gateway_integration.integration
  ]

  rest_api_id = aws_api_gateway_rest_api.api.id
  stage_name = ""
}

# ----------------------------------------------------------------------------------------------------------------------
# API GATEWAY STAGE
# Manages an API Gateway Stage.
# @param deployment_id The ID of the deployment that the stage points to
# @param rest_api_id  REST API identifier.
# @param stage_name The name of the stage
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_api_gateway_stage" "example" {
  deployment_id = aws_api_gateway_deployment.example.id
  rest_api_id = aws_api_gateway_rest_api.api.id
  stage_name = var.stage_name
}