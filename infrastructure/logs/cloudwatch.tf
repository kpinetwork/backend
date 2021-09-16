# ----------------------------------------------------------------------------------------------------------------------
# CLOUDWATCH GROUPS
# @param name The name of the log group
# @param retention_in_days Specifies the number of days you want to retain log events in the specified log group
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_cloudwatch_log_group" "minimal_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.lambdas_names.minimal_lambda_function}"
  retention_in_days = var.retention_days
}

resource "aws_cloudwatch_log_group" "sample_lambda_function" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.lambdas_names.sample_lambda_function}"
  retention_in_days = var.retention_days
}
