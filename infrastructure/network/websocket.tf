resource "aws_apigatewayv2_api" "websocket_api" {
  name                       = var.is_production? "websocket_${var.api_name}" : "websocket_${var.environment}_${var.api_name}"
  protocol_type              = "WEBSOCKET"
  route_selection_expression = "$request.body.action"
}

resource "aws_apigatewayv2_integration" "connect_integration" {
  api_id           = aws_apigatewayv2_api.websocket_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = var.lambdas_functions_arn.connect_lambda_function
  integration_method = "POST"
}

resource "aws_apigatewayv2_integration" "disconnect_integration" {
  api_id           = aws_apigatewayv2_api.websocket_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = var.lambdas_functions_arn.disconnect_lambda_function
  integration_method = "POST"
}

resource "aws_apigatewayv2_integration" "message_integration" {
  api_id           = aws_apigatewayv2_api.websocket_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = var.lambdas_functions_arn.message_lambda_function
  integration_method = "POST"
}

resource "aws_apigatewayv2_integration" "register_integration" {
  api_id           = aws_apigatewayv2_api.websocket_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = var.lambdas_functions_arn.register_lambda_function
  integration_method = "POST"
}

resource "aws_apigatewayv2_route" "connect_route" {
  api_id    = aws_apigatewayv2_api.websocket_api.id
  route_key = "$connect"
  target = "integrations/${aws_apigatewayv2_integration.connect_integration.id}"
}

resource "aws_apigatewayv2_route" "disconnect_route" {
  api_id    = aws_apigatewayv2_api.websocket_api.id
  route_key = "$disconnect"
  target = "integrations/${aws_apigatewayv2_integration.disconnect_integration.id}"
}

resource "aws_apigatewayv2_route" "message_route" {
  api_id    = aws_apigatewayv2_api.websocket_api.id
  route_key = "message"
  target = "integrations/${aws_apigatewayv2_integration.message_integration.id}"
}

resource "aws_apigatewayv2_route" "register_route" {
  api_id    = aws_apigatewayv2_api.websocket_api.id
  route_key = "register"
  target = "integrations/${aws_apigatewayv2_integration.register_integration.id}"
}

resource "aws_apigatewayv2_stage" "stage" {
  api_id = aws_apigatewayv2_api.websocket_api.id
  name   = var.environment

  default_route_settings {
    logging_level = "OFF"
    data_trace_enabled = false
    throttling_rate_limit = 100
    throttling_burst_limit = 50
  }
}

resource "aws_apigatewayv2_deployment" "deploy" {
  api_id      = aws_apigatewayv2_api.websocket_api.id
  description = "Deployed at ${timestamp()}"

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [
    aws_apigatewayv2_integration.disconnect_integration,
    aws_apigatewayv2_integration.connect_integration,
    aws_apigatewayv2_integration.message_integration,
    aws_apigatewayv2_route.disconnect_route,
    aws_apigatewayv2_route.connect_route,
    aws_apigatewayv2_route.message_route
  ]
}
      