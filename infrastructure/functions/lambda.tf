# ----------------------------------------------------------------------------------------------------------------------
# CREATE THE LAMBDA FUNCTION
# @param role Amazon Resource Name (ARN) of the function's execution role
# @param handler Function entrypoint
# @param runtime Identifier of the function's runtime
# @param s3_bucket Bucket reference to get code
# @param s3_key Source code name in s3 bucket
# @param function_name Function name
# @param source_code_hash Used to trigger updates
# @param depends_on Set of dependencies to execute the definition
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_lambda_function" "minimal_lambda_function" {
  role             = var.minimal_lambda_function_exec_role_arn
  handler          = "helloWorldHandler.handler"
  runtime          = var.runtime
  s3_bucket        = var.s3_object_references.minimal_function_object.bucket
  s3_key           = var.s3_object_references.minimal_function_object.key
  function_name    = "${var.environment}_${var.lambdas_names.minimal_lambda_function}"
  source_code_hash = base64sha256(var.s3_object_references.minimal_function_object.etag)
}

resource "aws_lambda_function" "db_sample_lambda_function" {
  role             = var.minimal_lambda_function_exec_role_arn
  handler          = "dbSampleHandler.handler"
  runtime          = var.runtime
  s3_bucket        = var.s3_object_references.db_sample_function_object.bucket
  s3_key           = var.s3_object_references.db_sample_function_object.key
  function_name    = "${var.environment}_${var.lambdas_names.db_sample_lambda_function}"
  source_code_hash = base64sha256(var.s3_object_references.db_sample_function_object.etag)

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [var.public_subnet_a_id]
    security_group_ids = [var.security_group_id]
  }

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]
}

resource "aws_lambda_function" "glue_trigger_lambda_function" {
  role             = var.lambda_exec_roles_arn.glue_trigger_lambda_exec_role
  handler          = "glueTriggerHandler.handler"
  runtime          = var.runtime
  s3_bucket        = var.s3_object_references.glue_trigger_function_object.bucket
  s3_key           = var.s3_object_references.glue_trigger_function_object.key
  function_name    = "${var.environment}_${var.lambdas_names.glue_trigger_lambda_function}"
  source_code_hash = base64sha256(var.s3_object_references.glue_trigger_function_object.etag)
  environment {
    variables = {
      ENV          = var.environment
      BUCKET_FILES = var.bucket_files
    }
  }
}

resource "aws_lambda_permission" "glue_trigger_event_permission" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.glue_trigger_lambda_function.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = "arn:aws:s3:::${var.bucket_files}"
}

resource "aws_s3_bucket_notification" "files_bucket_notification" {
  bucket     = var.bucket_files
  lambda_function {
    id                  = "aws_s3_bucket_notification_${aws_lambda_function.glue_trigger_lambda_function.function_name}"
    lambda_function_arn = aws_lambda_function.glue_trigger_lambda_function.arn
    events              = ["s3:ObjectCreated:Put"]
    filter_prefix       = "${var.environment}/"
  }
  depends_on = [
    aws_lambda_function.glue_trigger_lambda_function,
    aws_lambda_permission.glue_trigger_event_permission
  ]
}