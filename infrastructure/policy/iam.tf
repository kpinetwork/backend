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

resource "aws_iam_role" "company_lambda_exec_role" {
  name               = "${var.environment}_company_lambda_exec_role"
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

resource "aws_iam_role_policy_attachment" "company_lambda_logs" {
  role       = aws_iam_role.company_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_iam_role_policy_attachment" "companies_lambda_vpc" {
  role       = aws_iam_role.companies_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

resource "aws_iam_role_policy_attachment" "company_lambda_vpc" {
  role       = aws_iam_role.company_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

resource "aws_lambda_permission" "apigw_get_all_companies_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.get_all_companies_lambda_function}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_get_all_companies_lambda_function.api_id}/*/${var.api_gateway_references.apigw_get_all_companies_lambda_function.http_method}${var.api_gateway_references.apigw_get_all_companies_lambda_function.resource_path}"
}

resource "aws_lambda_permission" "apigw_get_company_lambda" {
  statement_id  = "AllowExecutionFromAPIGatewayCompanyId"
  action        = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.get_company_lambda_function}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_get_company_lambda_function.api_id}/*/${var.api_gateway_references.apigw_get_company_lambda_function.http_method}${var.api_gateway_references.apigw_get_company_lambda_function.resource_path}"
}

# ----------------------------------------------------------------------------------------------------------------------
# AWS IAM METRICS
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_iam_role" "get_metric_by_company_id_lambda_exec_role" {
  name               = "${var.environment}_get_metric_by_company_id_lambda_exec_role"
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

resource "aws_iam_role" "get_metrics_lambda_exec_role" {
  name               = "${var.environment}_get_metrics_lambda_exec_role"
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

resource "aws_iam_role_policy_attachment" "get_metric_by_company_id_lambda_logs" {
  role       = aws_iam_role.get_metric_by_company_id_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_iam_role_policy_attachment" "get_metrics_lambda_logs" {
  role       = aws_iam_role.get_metrics_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_iam_role_policy_attachment" "get_metrics_lambda_vpc" {
  role       = aws_iam_role.get_metrics_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

resource "aws_iam_role_policy_attachment" "get_metric_by_id_lambda_vpc" {
  role       = aws_iam_role.get_metric_by_company_id_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

resource "aws_lambda_permission" "apigw_get_metrics_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.get_metrics_lambda_function}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_get_metrics_lambda_function.api_id}/*/${var.api_gateway_references.apigw_get_metrics_lambda_function.http_method}${var.api_gateway_references.apigw_get_metrics_lambda_function.resource_path}"
}

resource "aws_lambda_permission" "apigw_get_metric_by_company_id_lambda" {
  statement_id  = "AllowExecutionFromAPIGatewayCompanyId"
  action        = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.get_metric_by_company_id_lambda_function}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_get_metric_by_company_id_lambda_function.api_id}/*/${var.api_gateway_references.apigw_get_metric_by_company_id_lambda_function.http_method}${var.api_gateway_references.apigw_get_metric_by_company_id_lambda_function.resource_path}"
}


# ----------------------------------------------------------------------------------------------------------------------
# AWS IAM REVENUE SUMMARY
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_iam_role" "get_revenue_sum_by_company_lambda_exec_role" {
  name               = "${var.environment}_get_revenue_sum_by_company_lambda_exec_role"
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

resource "aws_iam_role_policy_attachment" "get_revenue_sum_by_company_lambda_logs" {
  role       = aws_iam_role.get_revenue_sum_by_company_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_iam_role_policy_attachment" "get_revenue_sum_by_company_lambda_vpc" {
  role       = aws_iam_role.get_revenue_sum_by_company_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

resource "aws_lambda_permission" "apigw_get_revenue_sum_by_company_lambda" {
  statement_id  = "AllowExecutionFromAPIGatewayRevenueSum"
  action        = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.get_revenue_sum_by_company_lambda_function}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_get_revenue_sum_by_company_lambda_function.api_id}/*/${var.api_gateway_references.apigw_get_revenue_sum_by_company_lambda_function.http_method}${var.api_gateway_references.apigw_get_revenue_sum_by_company_lambda_function.resource_path}"
}

# ----------------------------------------------------------------------------------------------------------------------
# AWS IAM ROLE FINANCIAL SCENARIOS
# ----------------------------------------------------------------------------------------------------------------------
resource "aws_iam_role" "get_company_scenarios_lambda_exec_role" {
  name = "${var.environment}_get_company_scenarios_lambda_exec_role"
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

resource "aws_iam_role" "list_scenarios_lambda_exec_role" {
  name = "${var.environment}_list_scenarios_lambda_exec_role"
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

resource "aws_iam_role_policy_attachment" "company_scenarios_lambda_logs" {
  role = aws_iam_role.get_company_scenarios_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_iam_role_policy_attachment" "list_scenarios_lambda_logs" {
  role = aws_iam_role.list_scenarios_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_iam_role_policy_attachment" "company_scenarios_lambda_vpc" {
  role = aws_iam_role.get_company_scenarios_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

resource "aws_iam_role_policy_attachment" "list_scenarios_lambda_vpc" {
  role = aws_iam_role.list_scenarios_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

resource "aws_lambda_permission" "apigw_get_company_scenarios_lambda" {
  statement_id = "AllowExecutionFromAPIGatewayGetCompanyScenarios"
  action = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.get_company_scenarios_lambda_function}"
  principal = "apigateway.amazonaws.com"
  source_arn = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_get_company_scenarios_lambda_function.api_id}/*/${var.api_gateway_references.apigw_get_company_scenarios_lambda_function.http_method}${var.api_gateway_references.apigw_get_company_scenarios_lambda_function.resource_path}"
}

resource "aws_lambda_permission" "apigw_list_scenarios_lambda" {
  statement_id = "AllowExecutionFromAPIGatewayListScenarios"
  action = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.list_scenarios_lambda_function}"
  principal = "apigateway.amazonaws.com"
  source_arn = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_list_scenarios_lambda_function.api_id}/*/${var.api_gateway_references.apigw_list_scenarios_lambda_function.http_method}${var.api_gateway_references.apigw_list_scenarios_lambda_function.resource_path}"
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
# AWS IAM COHORTS
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_iam_role" "get_cohort_by_id_lambda_exec_role" {
  name               = "${var.environment}_get_cohort_by_id_lambda_exec_role"
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

resource "aws_iam_role" "get_cohorts_lambda_exec_role" {
  name               = "${var.environment}_get_cohorts_lambda_exec_role"
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

resource "aws_iam_role" "get_cohort_scenarios_lambda_exec_role" {
  name               = "${var.environment}_get_cohort_scenarios_lambda_exec_role"
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

resource "aws_iam_role_policy_attachment" "get_cohort_by_id_lambda_logs" {
  role       = aws_iam_role.get_cohort_by_id_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_iam_role_policy_attachment" "get_cohorts_lambda_logs" {
  role       = aws_iam_role.get_cohorts_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}


resource "aws_iam_role_policy_attachment" "get_cohort_scenarios_lambda_logs" {
  role       = aws_iam_role.get_cohort_scenarios_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_iam_role_policy_attachment" "get_cohort_scenarios_lambda_vpc" {
  role       = aws_iam_role.get_cohort_scenarios_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

resource "aws_iam_role_policy_attachment" "get_cohorts_lambda_vpc" {
  role       = aws_iam_role.get_cohorts_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}
resource "aws_iam_role_policy_attachment" "get_cohort_by_id_lambda_vpc" {
  role       = aws_iam_role.get_cohort_by_id_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

resource "aws_lambda_permission" "apigw_get_cohorts_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.get_cohorts_lambda_function}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_get_cohorts_lambda_function.api_id}/*/${var.api_gateway_references.apigw_get_cohorts_lambda_function.http_method}${var.api_gateway_references.apigw_get_cohorts_lambda_function.resource_path}"
}

resource "aws_lambda_permission" "apigw_get_cohort_by_id_lambda" {
  statement_id  = "AllowExecutionFromAPIGatewayCompanyId"
  action        = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.get_cohort_by_id_lambda_function}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_get_cohort_by_id_lambda_function.api_id}/*/${var.api_gateway_references.apigw_get_cohort_by_id_lambda_function.http_method}${var.api_gateway_references.apigw_get_cohort_by_id_lambda_function.resource_path}"
}

resource "aws_lambda_permission" "apigw_get_cohort_scenarios_lambda" {
  statement_id  = "AllowExecutionFromAPIGatewayCompanyId"
  action        = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.get_cohort_scenarios_lambda_function}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_get_cohort_scenarios_lambda_function.api_id}/*/${var.api_gateway_references.apigw_get_cohort_scenarios_lambda_function.http_method}${var.api_gateway_references.apigw_get_cohort_scenarios_lambda_function.resource_path}"
}
