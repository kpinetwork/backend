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

resource "aws_iam_role_policy_attachment" "get_comparison_vs_peers_lambda_logs" {
  role       = aws_iam_role.get_comparison_vs_peers_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_iam_role_policy_attachment" "get_comparison_vs_peers_lambda_vpc" {
  role       = aws_iam_role.get_comparison_vs_peers_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

resource "aws_lambda_permission" "apigw_get_comparison_vs_peers_lambda" {
  statement_id  = "AllowExecutionFromAPIGatewayRuleOf40"
  action        = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.get_comparison_vs_peers_lambda_function}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_get_comparison_vs_peers_lambda_function.api_id}/*/${var.api_gateway_references.apigw_get_comparison_vs_peers_lambda_function.http_method}${var.api_gateway_references.apigw_get_comparison_vs_peers_lambda_function.resource_path}"
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

resource "aws_iam_role" "get_metrics_by_cohort_id_lambda_exec_role" {
  name               = "${var.environment}_get_metrics_by_cohort_id_lambda_exec_role"
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

resource "aws_iam_role_policy_attachment" "get_metrics_by_cohort_id_lambda_logs" {
  role       = aws_iam_role.get_metrics_by_cohort_id_lambda_exec_role.name
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

resource "aws_iam_role_policy_attachment" "get_metrics_by_cohort_id_lambda_vpc" {
  role       = aws_iam_role.get_metrics_by_cohort_id_lambda_exec_role.name
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

resource "aws_lambda_permission" "apigw_get_metrics_by_cohort_id_lambda" {
  statement_id  = "AllowExecutionFromAPIGatewayCohortId"
  action        = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.get_metric_by_company_id_lambda_function}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_get_metrics_by_cohort_id_lambda_function.api_id}/*/${var.api_gateway_references.apigw_get_metrics_by_cohort_id_lambda_function.http_method}${var.api_gateway_references.apigw_get_metrics_by_cohort_id_lambda_function.resource_path}"
}

# ----------------------------------------------------------------------------------------------------------------------
# AWS IAM AVERAGE METRICS
# ----------------------------------------------------------------------------------------------------------------------
resource "aws_iam_role" "get_average_metrics_lambda_exec_role" {
  name               = "${var.environment}_get_average_metrics_lambda_exec_role"
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

resource "aws_iam_role" "get_average_metrics_by_cohort_lambda_exec_role" {
  name               = "${var.environment}_get_average_metrics_by_cohort_lambda_exec_role"
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

resource "aws_iam_role_policy_attachment" "get_average_metrics_lambda_logs" {
  role       = aws_iam_role.get_average_metrics_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_iam_role_policy_attachment" "get_average_metrics_by_cohort_lambda_logs" {
  role       = aws_iam_role.get_average_metrics_by_cohort_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_iam_role_policy_attachment" "get_average_metrics_lambda_vpc" {
  role       = aws_iam_role.get_average_metrics_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

resource "aws_iam_role_policy_attachment" "get_average_metrics_by_cohort_lambda_vpc" {
  role       = aws_iam_role.get_average_metrics_by_cohort_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

resource "aws_lambda_permission" "apigw_get_average_metrics_lambda" {
  statement_id  = "AllowExecutionFromAPIGatewayAverage"
  action        = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.get_average_metrics_lambda_function}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_get_average_metrics_lambda_function.api_id}/*/${var.api_gateway_references.apigw_get_average_metrics_lambda_function.http_method}${var.api_gateway_references.apigw_get_average_metrics_lambda_function.resource_path}"
}

resource "aws_lambda_permission" "apigw_get_average_metrics_by_cohort_lambda" {
  statement_id  = "AllowExecutionFromAPIGatewayCohortAverage"
  action        = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.get_average_metrics_by_cohort_lambda_function}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_get_average_metrics_by_cohort_lambda_function.api_id}/*/${var.api_gateway_references.apigw_get_average_metrics_by_cohort_lambda_function.http_method}${var.api_gateway_references.apigw_get_average_metrics_by_cohort_lambda_function.resource_path}"
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

resource "aws_iam_role" "get_revenue_sum_by_cohort_lambda_exec_role" {
  name               = "${var.environment}_get_revenue_sum_by_cohort_lambda_exec_role"
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

resource "aws_iam_role_policy_attachment" "get_revenue_sum_by_cohort_lambda_logs" {
  role       = aws_iam_role.get_revenue_sum_by_cohort_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_iam_role_policy_attachment" "get_revenue_sum_by_company_lambda_vpc" {
  role       = aws_iam_role.get_revenue_sum_by_company_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

resource "aws_iam_role_policy_attachment" "get_revenue_sum_by_cohort_lambda_vpc" {
  role       = aws_iam_role.get_revenue_sum_by_cohort_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

resource "aws_lambda_permission" "apigw_get_revenue_sum_by_company_lambda" {
  statement_id  = "AllowExecutionFromAPIGatewayRevenueSum"
  action        = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.get_revenue_sum_by_company_lambda_function}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_get_revenue_sum_by_company_lambda_function.api_id}/*/${var.api_gateway_references.apigw_get_revenue_sum_by_company_lambda_function.http_method}${var.api_gateway_references.apigw_get_revenue_sum_by_company_lambda_function.resource_path}"
}

resource "aws_lambda_permission" "apigw_get_revenue_sum_by_cohort_lambda" {
  statement_id  = "AllowExecutionFromAPIGatewayRevenueSum"
  action        = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.get_revenue_sum_by_cohort_lambda_function}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_get_revenue_sum_by_cohort_lambda_function.api_id}/*/${var.api_gateway_references.apigw_get_revenue_sum_by_cohort_lambda_function.http_method}${var.api_gateway_references.apigw_get_revenue_sum_by_cohort_lambda_function.resource_path}"
}

# ----------------------------------------------------------------------------------------------------------------------
# AWS IAM ROLE FINANCIAL SCENARIOS
# ----------------------------------------------------------------------------------------------------------------------
resource "aws_iam_role" "get_scenarios_lambda_exec_role" {
  name = "${var.environment}_get_scenarios_lambda_exec_role"
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

resource "aws_iam_role_policy_attachment" "scenarios_lambda_logs" {
  role = aws_iam_role.get_scenarios_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_iam_role_policy_attachment" "company_scenarios_lambda_logs" {
  role = aws_iam_role.get_company_scenarios_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_iam_role_policy_attachment" "list_scenarios_lambda_logs" {
  role = aws_iam_role.list_scenarios_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_logs_arn
}

resource "aws_iam_role_policy_attachment" "scenarios_lambda_vpc" {
  role = aws_iam_role.get_scenarios_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

resource "aws_iam_role_policy_attachment" "company_scenarios_lambda_vpc" {
  role = aws_iam_role.get_company_scenarios_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

resource "aws_iam_role_policy_attachment" "list_scenarios_lambda_vpc" {
  role = aws_iam_role.list_scenarios_lambda_exec_role.name
  policy_arn = var.aws_iam_policy_network_arn
}

resource "aws_lambda_permission" "apigw_get_scenarios_lambda" {
  statement_id = "AllowExecutionFromAPIGatewayGetScenarios"
  action = "lambda:InvokeFunction"
  function_name = "${var.environment}_${var.lambdas_names.get_scenarios_lambda_function}"
  principal = "apigateway.amazonaws.com"
  source_arn = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_references.apigw_get_scenarios_lambda_function.api_id}/*/${var.api_gateway_references.apigw_get_scenarios_lambda_function.http_method}${var.api_gateway_references.apigw_get_scenarios_lambda_function.resource_path}"
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

resource "aws_iam_policy" "verify_users_with_same_email_policy" {
  name        = "${var.environment}_pre_signup_trigger_policy"
  description = "A policy to verify if it already exists email adress"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "VisualEditor0",
      "Effect": "Allow",
      "Action": [
        "cognito-idp:ListUsers"
      ],
      "Resource": "${var.cognito_user_pool_arn}"
      }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "verify_users_with_same_email_cognito_policy" {
  role       = aws_iam_role.verify_users_with_same_email_lambda_exec_role.name
  policy_arn = aws_iam_policy.verify_users_with_same_email_policy.arn
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