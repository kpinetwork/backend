# ----------------------------------------------------------------------------------------------------------------------
# UPLOAD THE ZIP CODE TO S3
# @param bucket Bucket to upload code
# @param key Object name
# @param source Local directory to get zip code
# @param etag Triggers updates when the value changes
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_s3_bucket_object" "object" {
  bucket = var.bucket_name
  key = "helloWorldHandler.zip"
  source = "../${path.module}/dist/helloWorldHandler.zip"
  etag = filemd5("../${path.module}/dist/helloWorldHandler.zip")
}

# ----------------------------------------------------------------------------------------------------------------------
# CREATE REFERENCE FROM S3 FILE UPLOADED
# @param bucket Bucket reference
# @param key Object name
# @param depends_on Set of dependencies to execute the definition
# ----------------------------------------------------------------------------------------------------------------------

data "aws_s3_bucket_object" "lambda_zip" {
  bucket = "kpinetwork-backend"
  key = "helloWorldHandler.zip"
  depends_on = [
    aws_s3_bucket_object.object
  ]
}

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

resource "aws_lambda_function" "lambda_function" {
  role = aws_iam_role.lambda_exec_role.arn
  handler = "helloWorldHandler.handler"
  runtime = var.runtime
  s3_bucket = aws_s3_bucket_object.object.bucket
  s3_key = aws_s3_bucket_object.object.key
  function_name = var.function_name
  source_code_hash = base64sha256(data.aws_s3_bucket_object.lambda_zip.etag)
  depends_on = [
    aws_s3_bucket_object.object,
    aws_iam_role_policy_attachment.lambda_logs,
    aws_cloudwatch_log_group.example
  ]
}
