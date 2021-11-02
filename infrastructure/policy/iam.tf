# ----------------------------------------------------------------------------------------------------------------------
# AWS IAM ROLE
# Provides an IAM role.
# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role#description (General configurations)
# http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-control-access-using-iam-policies-to-invoke-api.html (aws_lambda_permission)
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_lambda_permission" "apigw_lambda" {
  statement_id = "AllowExecutionFromAPIGateway"
  action = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.minimal_lambda_function}"
  principal = "apigateway.amazonaws.com"
  source_arn = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_minimal_lambda_function.api_id}/*/${var.api_gateway_minimal_lambda_function.http_method}${var.api_gateway_minimal_lambda_function.resource_path}"
}

# ----------------------------------------------------------------------------------------------------------------------
# AWS IAM ROLE
# Provides an IAM role.
# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role#description (General configurations)
# http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-control-access-using-iam-policies-to-invoke-api.html (aws_lambda_permission)
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_iam_role" "glue_trigger_lambda_exec_role" {
  name = "glue_trigger_lambda_exec_role"
  path = "/"
  description = "Allows Lambda Function to call AWS services on your behalf."
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

# IAM policy for logging from a lambda
resource "aws_iam_policy" "lambda_logging" {
  name = "iam_policy_lambda_logging_function_back"
  path = "/"
  description = "IAM policy for logging from a lambda"
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*",
      "Effect": "Allow"
    }
  ]
}
EOF
}

# IAM policy to call glue from a lambda
resource "aws_iam_policy" "lambda_glue_access" {
  name = "iam_policy_lambda_glue_access"
  path = "/"
  description = "IAM policy to call glue from a lambda"
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "glue:StartJobRun"
      ],
      "Resource": "*",
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "glue_trigger_lambda_logs" {
  role = aws_iam_role.glue_trigger_lambda_exec_role.name
  policy_arn = aws_iam_policy.lambda_logging.arn
}

resource "aws_iam_role_policy_attachment" "glue_trigger_lambda_glue_access" {
  role = aws_iam_role.glue_trigger_lambda_exec_role.name
  policy_arn = aws_iam_policy.lambda_glue_access.arn
}
