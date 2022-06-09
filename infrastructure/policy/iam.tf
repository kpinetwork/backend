# ----------------------------------------------------------------------------------------------------------------------
# AWS IAM ROLE
# Provides an IAM role.
# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role#description (General configurations)
# http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-control-access-using-iam-policies-to-invoke-api.html (aws_lambda_permission)
# ----------------------------------------------------------------------------------------------------------------------
resource "aws_iam_role" "companies_lambda_exec_role" {
  name               = "${var.environment}_companies_lambda_exec_role"
  path               = "/"
  description        = "Allows Lambda Function to call AWS services on your behalf."
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

resource "aws_iam_role" "get_all_public_companies_lambda_exec_role" {
  name               = "${var.environment}_get_all_public_companies_lambda_exec_role"
  path               = "/"
  description        = "Allows Lambda Function to call AWS services on your behalf."
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

resource "aws_iam_role_policy" "get_all_public_companies_cognito_policy" {
  name        = "${var.environment}_get_all_public_companies_cognito_policy"
  role        = aws_iam_role.get_all_public_companies_lambda_exec_role.id
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "cognito-idp:AdminListGroupsForUser",
        "cognito-idp:AdminGetUser"
      ],
      "Effect": "Allow",
      "Resource": "arn:aws:cognito-idp:${var.region}:${var.account_id}:userpool/${var.user_pool_id}"
    }
  ]
}
EOF
}

resource "aws_iam_role" "get_company_details_lambda_exec_role" {
  name               = "${var.environment}_get_company_details_lambda_exec_role"
  path               = "/"
  description        = "Allows Lambda Function to call AWS services on your behalf."
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

resource "aws_iam_role_policy_attachment" "companies_lambda_logs" {
  role       = aws_iam_role.companies_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_iam_role_policy_attachment" "get_all_public_companies_lambda_logs" {
  role       = aws_iam_role.get_all_public_companies_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_iam_role_policy_attachment" "get_company_details_lambda_logs" {
  role       = aws_iam_role.get_company_details_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_iam_role_policy_attachment" "companies_lambda_vpc" {
  role       = aws_iam_role.companies_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

resource "aws_iam_role_policy_attachment" "get_all_public_companies_lambda_vpc" {
  role       = aws_iam_role.get_all_public_companies_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

resource "aws_iam_role_policy_attachment" "get_company_details_lambda_vpc" {
  role       = aws_iam_role.get_company_details_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

resource "aws_lambda_permission" "apigw_get_all_companies_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.get_all_companies_lambda_function}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_get_all_companies_lambda_function.api_id}/*/${var.api_gateway_references.apigw_get_all_companies_lambda_function.http_method}${var.api_gateway_references.apigw_get_all_companies_lambda_function.resource_path}"
}

resource "aws_lambda_permission" "apigw_get_all_public_companies_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.get_all_public_companies_lambda_function}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_get_all_public_companies_lambda_function.api_id}/*/${var.api_gateway_references.apigw_get_all_public_companies_lambda_function.http_method}${var.api_gateway_references.apigw_get_all_public_companies_lambda_function.resource_path}"
}

resource "aws_lambda_permission" "apigw_get_company_details_lambda" {
  statement_id  = "AllowExecutionFromAPIGatewayCompanyId"
  action        = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.get_company_details_lambda_function}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_get_company_details_lambda_function.api_id}/*/${var.api_gateway_references.apigw_get_company_details_lambda_function.http_method}${var.api_gateway_references.apigw_get_company_details_lambda_function.resource_path}"
}

# ----------------------------------------------------------------------------------------------------------------------
# AWS IAM ROLE OVERVIEW
# ----------------------------------------------------------------------------------------------------------------------
resource "aws_iam_role" "get_universe_overview_lambda_exec_role" {
  name               = "${var.environment}_get_universe_overview_lambda_exec_role"
  path               = "/"
  description        = "Allows Lambda Function to call AWS services on your behalf."
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

resource "aws_iam_role_policy" "get_universe_overview_cognito_policy" {
  name        = "${var.environment}_get_universe_overview_cognito_policy"
  role        = aws_iam_role.get_universe_overview_lambda_exec_role.id
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "cognito-idp:AdminListGroupsForUser",
        "cognito-idp:AdminGetUser"
      ],
      "Effect": "Allow",
      "Resource": "arn:aws:cognito-idp:${var.region}:${var.account_id}:userpool/${var.user_pool_id}"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "get_universe_overview_lambda_logs" {
  role       = aws_iam_role.get_universe_overview_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_iam_role_policy_attachment" "get_universe_overview_lambda_vpc" {
  role       = aws_iam_role.get_universe_overview_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

resource "aws_lambda_permission" "apigw_get_universe_overview_lambda" {
  statement_id  = "AllowExecutionFromAPIGatewayRuleOf40"
  action        = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.get_universe_overview_lambda_function}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_get_universe_overview_lambda_function.api_id}/*/${var.api_gateway_references.apigw_get_universe_overview_lambda_function.http_method}${var.api_gateway_references.apigw_get_universe_overview_lambda_function.resource_path}"
}

# ----------------------------------------------------------------------------------------------------------------------
# AWS IAM COMPANY REPORT VS PEERS
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_iam_role" "get_company_report_vs_peers_lambda_exec_role" {
  name               = "${var.environment}_get_company_report_vs_peers_lambda_exec_role"
  path               = "/"
  description        = "Allows Lambda Function to call AWS services on your behalf."
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

resource "aws_iam_role_policy" "get_company_report_vs_peers_cognito_policy" {
  name        = "${var.environment}_get_company_report_vs_peers_cognito_policy"
  role        = aws_iam_role.get_company_report_vs_peers_lambda_exec_role.id
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "cognito-idp:AdminListGroupsForUser",
        "cognito-idp:AdminGetUser"
      ],
      "Effect": "Allow",
      "Resource": "arn:aws:cognito-idp:${var.region}:${var.account_id}:userpool/${var.user_pool_id}"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "get_company_report_vs_peers_lambda_logs" {
  role       = aws_iam_role.get_company_report_vs_peers_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_iam_role_policy_attachment" "get_company_report_vs_peers_lambda_vpc" {
  role       = aws_iam_role.get_company_report_vs_peers_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

resource "aws_lambda_permission" "apigw_get_company_report_vs_peers_lambda" {
  statement_id  = "AllowExecutionFromAPIGatewayRuleOf40"
  action        = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.get_company_report_vs_peers_lambda_function}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_get_company_report_vs_peers_lambda_function.api_id}/*/${var.api_gateway_references.apigw_get_company_report_vs_peers_lambda_function.http_method}${var.api_gateway_references.apigw_get_company_report_vs_peers_lambda_function.resource_path}"
}

# ----------------------------------------------------------------------------------------------------------------------
# AWS IAM COMPARISON VS PEERS
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_iam_role" "get_comparison_vs_peers_lambda_exec_role" {
  name               = "${var.environment}_get_comparison_vs_peers_lambda_exec_role"
  path               = "/"
  description        = "Allows Lambda Function to call AWS services on your behalf."
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

resource "aws_iam_role" "download_comparison_vs_peers_lambda_exec_role" {
  name               = "${var.environment}_download_comparison_vs_peers_lambda_exec_role"
  path               = "/"
  description        = "Allows Lambda Function to call AWS services on your behalf."
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

resource "aws_iam_role_policy" "get_comparison_vs_peers_cognito_policy" {
  name        = "${var.environment}_get_comparison_vs_peers_cognito_policy"
  role        = aws_iam_role.get_comparison_vs_peers_lambda_exec_role.id
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "cognito-idp:AdminListGroupsForUser",
        "cognito-idp:AdminGetUser"
      ],
      "Effect": "Allow",
      "Resource": "arn:aws:cognito-idp:${var.region}:${var.account_id}:userpool/${var.user_pool_id}"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "download_comparison_vs_peers_cognito_policy" {
  name        = "${var.environment}_download_comparison_vs_peers_cognito_policy"
  role        = aws_iam_role.download_comparison_vs_peers_lambda_exec_role.id
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "cognito-idp:AdminListGroupsForUser",
        "cognito-idp:AdminGetUser"
      ],
      "Effect": "Allow",
      "Resource": "arn:aws:cognito-idp:${var.region}:${var.account_id}:userpool/${var.user_pool_id}"
    }
  ]
}
EOF
}


resource "aws_iam_role_policy_attachment" "get_comparison_vs_peers_lambda_logs" {
  role       = aws_iam_role.get_comparison_vs_peers_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}
resource "aws_iam_role_policy_attachment" "download_comparison_vs_peers_lambda_logs" {
  role       = aws_iam_role.download_comparison_vs_peers_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_iam_role_policy_attachment" "get_comparison_vs_peers_lambda_vpc" {
  role       = aws_iam_role.get_comparison_vs_peers_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}
resource "aws_iam_role_policy_attachment" "download_comparison_vs_peers_lambda_vpc" {
  role       = aws_iam_role.download_comparison_vs_peers_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

resource "aws_lambda_permission" "apigw_get_comparison_vs_peers_lambda" {
  statement_id  = "AllowExecutionFromAPIGatewayRuleOf40"
  action        = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.get_comparison_vs_peers_lambda_function}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_get_comparison_vs_peers_lambda_function.api_id}/*/${var.api_gateway_references.apigw_get_comparison_vs_peers_lambda_function.http_method}${var.api_gateway_references.apigw_get_comparison_vs_peers_lambda_function.resource_path}"
}
resource "aws_lambda_permission" "apigw_download_comparison_vs_peers_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.download_comparison_vs_peers_lambda_function}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_download_comparison_vs_peers_lambda_function.api_id}/*/${var.api_gateway_references.apigw_download_comparison_vs_peers_lambda_function.http_method}${var.api_gateway_references.apigw_download_comparison_vs_peers_lambda_function.resource_path}"
}


# ----------------------------------------------------------------------------------------------------------------------
# INVESTMENT REPORT
# ----------------------------------------------------------------------------------------------------------------------
resource "aws_iam_role" "get_investment_year_report_lambda_exec_role" {
  name               = "${var.environment}_get_investment_year_report_lambda_exec_role"
  path               = "/"
  description        = "Allows Lambda Function to call AWS services on your behalf."
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

resource "aws_iam_role" "get_investment_year_options_lambda_exec_role" {
  name               = "${var.environment}_get_investment_year_options_lambda_exec_role"
  path               = "/"
  description        = "Allows Lambda Function to call AWS services on your behalf."
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


resource "aws_iam_role_policy" "get_investment_year_report_cognito_policy" {
  name        = "${var.environment}_get_investment_year_report_cognito_policy"
  role        = aws_iam_role.get_investment_year_report_lambda_exec_role.id
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "cognito-idp:AdminListGroupsForUser",
        "cognito-idp:AdminGetUser"
      ],
      "Effect": "Allow",
      "Resource": "arn:aws:cognito-idp:${var.region}:${var.account_id}:userpool/${var.user_pool_id}"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "get_investment_year_report_lambda_logs" {
  role       = aws_iam_role.get_investment_year_report_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}
resource "aws_iam_role_policy_attachment" "get_investment_year_options_lambda_logs" {
  role       = aws_iam_role.get_investment_year_options_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_iam_role_policy_attachment" "get_investment_year_report_lambda_vpc" {
  role       = aws_iam_role.get_investment_year_report_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}
resource "aws_iam_role_policy_attachment" "get_investment_year_options_lambda_vpc" {
  role       = aws_iam_role.get_investment_year_options_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

resource "aws_lambda_permission" "apigw_get_investment_year_report_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.get_investment_year_report_lambda_function}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_get_investment_year_report_lambda_function.api_id}/*/${var.api_gateway_references.apigw_get_investment_year_report_lambda_function.http_method}${var.api_gateway_references.apigw_get_investment_year_report_lambda_function.resource_path}"
}
resource "aws_lambda_permission" "apigw_get_investment_year_options_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.get_investment_year_options_lambda_function}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_get_investment_year_options_lambda_function.api_id}/*/${var.api_gateway_references.apigw_get_investment_year_options_lambda_function.http_method}${var.api_gateway_references.apigw_get_investment_year_options_lambda_function.resource_path}"
}

# ----------------------------------------------------------------------------------------------------------------------
# BY METRIC REPORT
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_iam_role" "get_by_metric_report_lambda_exec_role" {
  name               = "${var.environment}_get_by_metric_report_lambda_exec_role"
  path               = "/"
  description        = "Allows Lambda Function to call AWS services on your behalf."
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


resource "aws_iam_role_policy" "get_by_metric_report_cognito_policy" {
  name        = "${var.environment}_get_by_metric_report_cognito_policy"
  role        = aws_iam_role.get_by_metric_report_lambda_exec_role.id
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "cognito-idp:AdminListGroupsForUser",
        "cognito-idp:AdminGetUser"
      ],
      "Effect": "Allow",
      "Resource": "arn:aws:cognito-idp:${var.region}:${var.account_id}:userpool/${var.user_pool_id}"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "get_by_metric_report_lambda_logs" {
  role       = aws_iam_role.get_by_metric_report_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_iam_role_policy_attachment" "get_by_metric_report_lambda_vpc" {
  role       = aws_iam_role.get_by_metric_report_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

resource "aws_lambda_permission" "apigw_get_by_metric_report_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.get_by_metric_report_lambda_function}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_get_by_metric_report_lambda_function.api_id}/*/${var.api_gateway_references.apigw_get_by_metric_report_lambda_function.http_method}${var.api_gateway_references.apigw_get_by_metric_report_lambda_function.resource_path}"
}

# ----------------------------------------------------------------------------------------------------------------------
# AWS IAM ROLE GLUE
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_iam_role" "glue_trigger_lambda_exec_role" {
  name = "${var.environment}_glue_trigger_lambda_exec_role"
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
  name = "${var.environment}_iam_policy_lambda_logging_function_back"
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
  name = "${var.environment}_iam_policy_lambda_glue_access"
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

# ----------------------------------------------------------------------------------------------------------------------
# AWS IAM COGNITO TRIGGER POST CONFIRMATION
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_iam_role" "add_user_to_customer_group_lambda_exec_role" {
  name               = "${var.environment}_add_user_to_customer_group_lambda_exec_role"
  path               = "/"
  description        = "Allows Lambda Function to call AWS services on your behalf."
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

resource "aws_iam_policy" "add_user_to_customer_group_policy" {
  name        = "${var.environment}_post_configuration_trigger_policy"
  description = "A policy to add user to customer group"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "VisualEditor0",
      "Effect": "Allow",
      "Action": [
        "cognito-idp:AdminAddUserToGroup",
        "cognito-idp:AdminGetUser"
      ],
      "Resource": "${var.cognito_user_pool_arn}"
      }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "add_user_to_customer_group_lambda_cognito_policy" {
  role       = aws_iam_role.add_user_to_customer_group_lambda_exec_role.name
  policy_arn = aws_iam_policy.add_user_to_customer_group_policy.arn
}

resource "aws_iam_role_policy_attachment" "add_user_to_customer_group_lambda_logs" {
  role       = aws_iam_role.add_user_to_customer_group_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

# ----------------------------------------------------------------------------------------------------------------------
# AWS IAM ROLE USERS AND ROLES
# ----------------------------------------------------------------------------------------------------------------------
resource "aws_iam_role" "get_roles_lambda_exec_role" {
  name               = "${var.environment}_get_roles_lambda_exec_role"
  path               = "/"
  description        = "Allows Lambda Function to call AWS services on your behalf."
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

resource "aws_iam_role_policy_attachment" "get_roles_lambda_logs" {
  role       = aws_iam_role.get_roles_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_iam_role_policy" "get_roles_cognito_policy" {
  name        = "${var.environment}_get_roles_cognito_policy"
  role        = aws_iam_role.get_roles_lambda_exec_role.id
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action":[
        "cognito-idp:ListGroups",
        "cognito-idp:AdminListGroupsForUser"
      ],
      "Effect": "Allow",
      "Resource": "arn:aws:cognito-idp:${var.region}:${var.account_id}:userpool/${var.user_pool_id}"
    }
  ]
}
EOF
}

resource "aws_lambda_permission" "apigw_get_roles_lambda" {
  statement_id  = "AllowExecutionFromAPIGatewayGetRoles"
  action        = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.get_roles_lambda_function}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_get_roles_lambda_function.api_id}/*/${var.api_gateway_references.apigw_get_roles_lambda_function.http_method}${var.api_gateway_references.apigw_get_roles_lambda_function.resource_path}"
}

# ----------------------------------------------------------------------------------------------------------------------
# AWS API GATEWAY AUTHORIZATION
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_iam_role" "authorize_lambda_exec_role" {
  name = "${var.environment}_authorize_lambda_exec_role"
  description        = "Allows Lambda Function to call AWS services on your behalf."
  
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "authorize_lambda_logs" {
  role       = aws_iam_role.authorize_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_lambda_permission" "apigw_authorize_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.authorize_lambda_function}"
  principal     = "apigateway.amazonaws.com"
}

resource "aws_iam_role" "authorize_lambda_invoke_role" {
  name               = "${var.environment}_authorize_lambda_invoke_role"
  path               = "/"
  description        = "Allows API Gateway to call AWS services on your behalf."
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "apigateway.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "authorize_lambda_invoke_policy" {
  name        = "${var.environment}_authorize_lambda_invoke_policy"
  role        = aws_iam_role.authorize_lambda_invoke_role.id
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "lambda:InvokeFunction",
      "Effect": "Allow",
      "Resource": "arn:aws:lambda:${var.region}:${var.account_id}:function:${var.environment}_${var.lambdas_names.authorize_lambda_function}"
    }
  ]
}
EOF
}

# ----------------------------------------------------------------------------------------------------------------------
# AWS IAM COGNITO TRIGGER PRE SIGN UP
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_iam_role" "verify_users_with_same_email_lambda_exec_role" {
  name               = "${var.environment}_verify_users_with_same_email_exec_role"
  path               = "/"
  description        = "Allows Lambda Function to call AWS services on your behalf."
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

resource "aws_iam_role_policy" "verify_users_with_same_email_lambda_list_users_policy" {
  name        = "${var.environment}_verify_users_with_same_email_lambda_list_users_policy"
  role        = aws_iam_role.verify_users_with_same_email_lambda_exec_role.id
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "cognito-idp:ListUsers",
      "Effect": "Allow",
      "Resource": "${var.cognito_user_pool_arn}"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "verify_users_with_same_email_lambda_logs" {
  role       = aws_iam_role.verify_users_with_same_email_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_lambda_permission" "allow_pre_signup_from_user_pool" {
  statement_id = "AllowPreSignUpFromUserPool"
  action = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.verify_users_with_same_email_lambda_function}"
  principal = "cognito-idp.amazonaws.com"
  source_arn = "${var.cognito_user_pool_arn}"
}

# ----------------------------------------------------------------------------------------------------------------------
# AWS IAM ROLE USERS
# ----------------------------------------------------------------------------------------------------------------------
resource "aws_iam_role" "get_users_lambda_exec_role" {
  name               = "${var.environment}_get_users_lambda_exec_role"
  path               = "/"
  description        = "Allows Lambda Function to call AWS services on your behalf."
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

resource "aws_iam_role_policy" "authorize_lambda_get_users_and_groups" {
  name        = "${var.environment}_authorize_lambda_get_users_and_groups"
  role        = aws_iam_role.get_users_lambda_exec_role.id
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cognito-idp:AdminListGroupsForUser",
        "cognito-idp:ListUsers"
      ],
      "Resource": "${var.cognito_user_pool_arn}"
      }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "get_users_lambda_logs" {
  role       = aws_iam_role.get_users_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_iam_role_policy_attachment" "get_users_lambda_vpc" {
  role       = aws_iam_role.get_universe_overview_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

resource "aws_lambda_permission" "apigw_get_users_lambda" {
  statement_id  = "AllowExecutionFromAPIGatewayGetUsers"
  action        = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.get_users_lambda_function}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_get_users_lambda_function.api_id}/*/${var.api_gateway_references.apigw_get_users_lambda_function.http_method}${var.api_gateway_references.apigw_get_users_lambda_function.resource_path}"
}

# ----------------------------------------------------------------------------------------------------------------------
# AWS IAM ROLE USER DETAILS
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_iam_role" "get_user_details_lambda_exec_role" {
  name               = "${var.environment}_get_user_details_lambda_exec_role"
  path               = "/"
  description        = "Allows Lambda Function to call AWS services on your behalf."
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

resource "aws_iam_role" "change_user_role_lambda_exec_role" {
  name               = "${var.environment}_change_user_role_lambda_exec_role"
  path               = "/"
  description        = "Allows Lambda Function to call AWS services on your behalf."
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

resource "aws_iam_role" "assign_company_permissions_lambda_exec_role" {
  name               = "${var.environment}_assign_company_permissions_lambda_exec_role"
  path               = "/"
  description        = "Allows Lambda Function to call AWS services on your behalf."
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

resource "aws_iam_role_policy" "assign_company_permissions_cognito_policy" {
  name        = "${var.environment}_assign_company_permissions_cognito_policy"
  role        = aws_iam_role.assign_company_permissions_lambda_exec_role.id
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "cognito-idp:AdminListGroupsForUser"
      ],
      "Effect": "Allow",
      "Resource": "arn:aws:cognito-idp:${var.region}:${var.account_id}:userpool/${var.user_pool_id}"
    }
  ]
}
EOF
}

resource "aws_iam_role" "get_company_permissions_lambda_exec_role" {
  name               = "${var.environment}_get_company_permissions_lambda_exec_role"
  path               = "/"
  description        = "Allows Lambda Function to call AWS services on your behalf."
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

resource "aws_iam_role_policy" "get_company_permissions_cognito_policy" {
  name        = "${var.environment}_get_company_permissions_cognito_policy"
  role        = aws_iam_role.get_company_permissions_lambda_exec_role.id
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "cognito-idp:AdminListGroupsForUser"
      ],
      "Effect": "Allow",
      "Resource": "arn:aws:cognito-idp:${var.region}:${var.account_id}:userpool/${var.user_pool_id}"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "get_user_details_lambda_logs" {
  role       = aws_iam_role.get_user_details_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_iam_role_policy_attachment" "change_user_role_lambda_logs" {
  role       = aws_iam_role.change_user_role_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_iam_role_policy_attachment" "assign_company_permissions_lambda_logs" {
  role       = aws_iam_role.assign_company_permissions_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_iam_role_policy_attachment" "get_company_permissions_lambda_logs" {
  role       = aws_iam_role.get_company_permissions_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_iam_role_policy_attachment" "get_user_details_lambda_vpc" {
  role       = aws_iam_role.get_user_details_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

resource "aws_iam_role_policy_attachment" "change_user_role_lambda_vpc" {
  role       = aws_iam_role.change_user_role_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

resource "aws_iam_role_policy_attachment" "assign_company_permissions_lambda_vpc" {
  role       = aws_iam_role.assign_company_permissions_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

resource "aws_iam_role_policy_attachment" "get_company_permissions_lambda_vpc" {
  role       = aws_iam_role.get_company_permissions_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

resource "aws_iam_role_policy" "get_user_details_cognito_policy" {
  name        = "${var.environment}_get_user_details_cognito_policy"
  role        = aws_iam_role.get_user_details_lambda_exec_role.id
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "cognito-idp:AdminListGroupsForUser",
        "cognito-idp:AdminGetUser",
        "cognito-idp:ListUsers"
      ],
      "Effect": "Allow",
      "Resource": "arn:aws:cognito-idp:${var.region}:${var.account_id}:userpool/${var.user_pool_id}"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "change_user_role_cognito_policy" {
  name        = "${var.environment}_change_user_role_cognito_policy"
  role        = aws_iam_role.change_user_role_lambda_exec_role.id
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "cognito-idp:AdminListGroupsForUser",
        "cognito-idp:AdminAddUserToGroup",
        "cognito-idp:AdminRemoveUserFromGroup",
        "cognito-idp:AdminGetUser",
        "cognito-idp:ListUsers"
      ],
      "Effect": "Allow",
      "Resource": "arn:aws:cognito-idp:${var.region}:${var.account_id}:userpool/${var.user_pool_id}"
    }
  ]
}
EOF
}

resource "aws_lambda_permission" "apigw_get_user_details_lambda" {
  statement_id  = "AllowExecutionFromAPIGatewayGetUserDetails"
  action        = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.get_user_details_lambda_function}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_get_user_details_lambda_function.api_id}/*/${var.api_gateway_references.apigw_get_user_details_lambda_function.http_method}${var.api_gateway_references.apigw_get_user_details_lambda_function.resource_path}"
}

resource "aws_lambda_permission" "apigw_change_user_role_lambda" {
  statement_id  = "AllowExecutionFromAPIGatewayChangeUserRole"
  action        = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.change_user_role_lambda_function}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_change_user_role_lambda_function.api_id}/*/${var.api_gateway_references.apigw_change_user_role_lambda_function.http_method}${var.api_gateway_references.apigw_change_user_role_lambda_function.resource_path}"
}

resource "aws_lambda_permission" "apigw_assign_company_permissions_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.assign_company_permissions_lambda_function}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_assign_company_permissions_lambda_function.api_id}/*/${var.api_gateway_references.apigw_assign_company_permissions_lambda_function.http_method}${var.api_gateway_references.apigw_assign_company_permissions_lambda_function.resource_path}"
}

resource "aws_lambda_permission" "apigw_get_company_permissions_lambda" {
  statement_id  = "AllowExecutionFromAPIGatewayGetCompanyPermissions"
  action        = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.get_company_permissions_lambda_function}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_get_company_permissions_lambda_function.api_id}/*/${var.api_gateway_references.apigw_get_company_permissions_lambda_function.http_method}${var.api_gateway_references.apigw_get_company_permissions_lambda_function.resource_path}"
}

# ----------------------------------------------------------------------------------------------------------------------
# AWS IAM CHANGE COMPANY PUBLICLY
# ----------------------------------------------------------------------------------------------------------------------
resource "aws_iam_role" "change_company_publicly_lambda_exec_role" {
  name = "${var.environment}_change_company_publicly_lambda_exec_role"
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

resource "aws_iam_role_policy" "change_company_publicly_cognito_policy" {
  name        = "${var.environment}_change_company_publicly_cognito_policy"
  role        = aws_iam_role.change_company_publicly_lambda_exec_role.id
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "cognito-idp:AdminListGroupsForUser"
      ],
      "Effect": "Allow",
      "Resource": "arn:aws:cognito-idp:${var.region}:${var.account_id}:userpool/${var.user_pool_id}"
    }
  ]
}
EOF
}


resource "aws_iam_role_policy_attachment" "change_company_publicly_lambda_logs" {
  role = aws_iam_role.change_company_publicly_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_iam_role_policy_attachment" "change_company_publicly_lambda_vpc" {
  role = aws_iam_role.change_company_publicly_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

resource "aws_lambda_permission" "apigw_change_company_publicly_lambda" {
  statement_id = "AllowExecutionFromAPIGatewayChangeCompanyPublicly"
  action = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.change_company_publicly_lambda_function}"
  principal = "apigateway.amazonaws.com"
  source_arn = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_change_company_publicly_lambda_function.api_id}/*/${var.api_gateway_references.apigw_change_company_publicly_lambda_function.http_method}${var.api_gateway_references.apigw_change_company_publicly_lambda_function.resource_path}"
}

# ----------------------------------------------------------------------------------------------------------------------
# AWS IAM UPLOAD FILE S3 AND VALIDATION
# ----------------------------------------------------------------------------------------------------------------------
resource "aws_iam_role" "upload_file_s3_lambda_exec_role" {
  name = "${var.environment}_upload_file_s3_lambda_exec_role"
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

resource "aws_iam_role_policy" "upload_file_s3_policy" {
  name        = "${var.environment}_upload_file_s3_policy"
  role        = aws_iam_role.upload_file_s3_lambda_exec_role.id
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "s3:PutObject"
      ],
      "Effect": "Allow",
      "Resource":"*"
    }
  ]
}
EOF
}


resource "aws_iam_role_policy_attachment" "upload_file_s3_lambda_logs" {
  role = aws_iam_role.upload_file_s3_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_lambda_permission" "apigw_upload_file_s3_lambda" {
  statement_id = "AllowExecutionFromAPIGatewayUploadFileS3"
  action = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.upload_file_s3_lambda_function}"
  principal = "apigateway.amazonaws.com"
  source_arn = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_upload_file_s3_lambda_function.api_id}/*/${var.api_gateway_references.apigw_upload_file_s3_lambda_function.http_method}${var.api_gateway_references.apigw_upload_file_s3_lambda_function.resource_path}"
}

resource "aws_iam_role" "validate_data_lambda_exec_role" {
  name = "${var.environment}_validate_data_lambda_exec_role"
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

resource "aws_iam_role_policy_attachment" "validate_data_lambda_logs" {
  role = aws_iam_role.validate_data_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_iam_role_policy_attachment" "validate_data_lambda_vpc" {
  role = aws_iam_role.validate_data_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}
resource "aws_lambda_permission" "apigw_validate_data_lambda" {
  statement_id = "AllowExecutionFromAPIGatewayValidateData"
  action = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.validate_data_lambda_function}"
  principal = "apigateway.amazonaws.com"
  source_arn = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_validate_data_lambda_function.api_id}/*/${var.api_gateway_references.apigw_validate_data_lambda_function.http_method}${var.api_gateway_references.apigw_validate_data_lambda_function.resource_path}"
}
# ----------------------------------------------------------------------------------------------------------------------
# AWS WEBSOCKET
# ----------------------------------------------------------------------------------------------------------------------
resource "aws_iam_role" "connect_lambda_exec_role" {
  name = "${var.environment}_connect_lambda_exec_role"
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

resource "aws_iam_role_policy_attachment" "connect_lambda_logs" {
  role = aws_iam_role.connect_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_lambda_permission" "websocket_connect" {
  statement_id = "AllowExecutionFromApiGateway"
  action = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.connect_lambda_function}"
  principal = "apigateway.amazonaws.com"
  source_arn = "${var.websocket_api_references.api.arn}/*/$connect"
}

resource "aws_iam_role" "disconnect_lambda_exec_role" {
  name = "${var.environment}_disconnect_lambda_exec_role"
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

resource "aws_iam_role_policy_attachment" "disconnect_lambda_logs" {
  role = aws_iam_role.disconnect_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_iam_role_policy_attachment" "disconnect_lambda_vpc" {
  role = aws_iam_role.disconnect_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

resource "aws_lambda_permission" "websocket_disconnect" {
  statement_id = "AllowExecutionFromApiGateway"
  action = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.disconnect_lambda_function}"
  principal = "apigateway.amazonaws.com"
  source_arn = "${var.websocket_api_references.api.arn}/*/$disconnect"
}

resource "aws_iam_role" "message_lambda_exec_role" {
  name = "${var.environment}_message_lambda_exec_role"
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

resource "aws_iam_role_policy_attachment" "message_lambda_logs" {
  role = aws_iam_role.message_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_iam_role_policy_attachment" "message_lambda_vpc" {
  role = aws_iam_role.message_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

resource "aws_lambda_permission" "websocket_message" {
  statement_id = "AllowExecutionFromApiGateway"
  action = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.message_lambda_function}"
  principal = "apigateway.amazonaws.com"
  source_arn = "${var.websocket_api_references.api.arn}/*/message"
}

resource "aws_iam_role_policy" "allow_execute_api_message_connection" {
  name        = "${var.environment}_allow_execute_api_message_connection_policy"
  role        = aws_iam_role.message_lambda_exec_role.id
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "execute-api:ManageConnections"
      ],
      "Effect": "Allow",
      "Resource": "${var.websocket_api_references.api.arn}/*"
    }
  ]
}
EOF
}

resource "aws_iam_role" "register_lambda_exec_role" {
  name = "${var.environment}_register_lambda_exec_role"
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

resource "aws_iam_role_policy_attachment" "register_lambda_logs" {
  role = aws_iam_role.register_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_iam_role_policy_attachment" "register_lambda_vpc" {
  role = aws_iam_role.register_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

resource "aws_lambda_permission" "websocket_register" {
  statement_id = "AllowExecutionFromApiGateway"
  action = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.register_lambda_function}"
  principal = "apigateway.amazonaws.com"
  source_arn = "${var.websocket_api_references.api.arn}/*/register"
}

resource "aws_iam_role_policy" "allow_execute_api_register_connection" {
  name        = "${var.environment}_allow_execute_api_register_connection_policy"
  role        = aws_iam_role.register_lambda_exec_role.id
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "execute-api:ManageConnections"
      ],
      "Effect": "Allow",
      "Resource": "${var.websocket_api_references.api.arn}/*"
    }
  ]
}
EOF
}

# ----------------------------------------------------------------------------------------------------------------------
# AWS IAM INVESTMENTS
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_iam_role" "company_investments_lambda_exec_role" {
  name               = "${var.environment}_get_company_investments_lambda_exec_role"
  path               = "/"
  description        = "Allows Lambda Function to call AWS services on your behalf."
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

resource "aws_iam_role" "add_investment_lambda_exec_role" {
  name               = "${var.environment}_add_investment_lambda_exec_role"
  path               = "/"
  description        = "Allows Lambda Function to call AWS services on your behalf."
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


resource "aws_iam_role_policy_attachment" "company_investments_lambda_logs" {
  role       = aws_iam_role.company_investments_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_iam_role_policy_attachment" "add_investment_lambda_logs" {
  role       = aws_iam_role.add_investment_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}


resource "aws_iam_role_policy_attachment" "company_investments_lambda_vpc" {
  role       = aws_iam_role.company_investments_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

resource "aws_iam_role_policy_attachment" "add_investment_lambda_vpc" {
  role       = aws_iam_role.add_investment_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

resource "aws_lambda_permission" "apigw_company_investments_lambda" {
  statement_id  = "AllowExecutionFromAPIGatewayGetCompanyInvestmentsId"
  action        = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.get_company_investments_lambda_function}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_get_company_investments_lambda_function.api_id}/*/${var.api_gateway_references.apigw_get_company_investments_lambda_function.http_method}${var.api_gateway_references.apigw_get_company_investments_lambda_function.resource_path}"
}

resource "aws_lambda_permission" "apigw_add_investment_lambda" {
  statement_id  = "AllowExecutionFromAPIGatewayAddInvestmentId"
  action        = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.add_investment_lambda_function}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_add_investment_lambda_function.api_id}/*/${var.api_gateway_references.apigw_add_investment_lambda_function.http_method}${var.api_gateway_references.apigw_add_investment_lambda_function.resource_path}"
}

# ----------------------------------------------------------------------------------------------------------------------
# AWS UPDATE DATA LAMBDA FOR GLUE SCRIPT
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_iam_role" "update_data_lambda_exec_role" {
  name               = "${var.environment}_update_data_lambda_exec_role"
  path               = "/"
  description        = "Allows Lambda Function to call AWS services on your behalf."
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

resource "aws_iam_role_policy_attachment" "update_data_lambda_logs" {
  role       = aws_iam_role.update_data_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_iam_role_policy_attachment" "update_data_lambda_vpc" {
  role       = aws_iam_role.update_data_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

