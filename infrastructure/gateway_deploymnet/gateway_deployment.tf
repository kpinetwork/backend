# ----------------------------------------------------------------------------------------------------------------------
# API GATEWAY DEPLOYMENT
# Manages an API Gateway REST Deployment.
# @param depends_on Set of dependencies to execute the definition
# @param rest_api_id  REST API identifier.
# @param stage_name Name of the stage to create with this deployment, with this isn't necessary add aws_api_gateway_stage resource
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_api_gateway_deployment" "gateway_deployment" {
  rest_api_id       = var.api_gateway_rest_api_id
  stage_name        = var.is_production? var.stage_name : var.environment
  stage_description = "Deployed at ${timestamp()}"

  lifecycle {
    create_before_destroy = true
  }
}