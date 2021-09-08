# ----------------------------------------------------------------------------------------------------------------------
# CLOUDWATCH GROUPS
# @param name The name of the log group
# @param retention_in_days Specifies the number of days you want to retain log events in the specified log group
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_cloudwatch_log_group" "example" {
  name = "${var.prefix_lambda_cloudwatch_log_group}${var.function_name}"
  retention_in_days = var.retention_days
}
