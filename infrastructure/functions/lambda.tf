
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
  role = var.minimal_lambda_function_exec_role_arn
  handler = "helloWorldHandler.handler"
  runtime = var.runtime
  s3_bucket = var.minimal_lambda_function_bucket.bucket
  s3_key = var.minimal_lambda_function_bucket.key
  function_name = var.lambdas_names.minimal_lambda_function
  source_code_hash = base64sha256(var.minimal_lambda_function_bucket.etag)
}

resource "aws_lambda_function" "sample_lambda_function" {
  role = var.minimal_lambda_function_exec_role_arn
  handler = "testSampleHandler.handler"
  runtime = var.runtime
  s3_bucket = var.sample_lambda_function_bucket.bucket
  s3_key = var.sample_lambda_function_bucket.key
  function_name = var.lambdas_names.sample_lambda_function
  source_code_hash = base64sha256(var.sample_lambda_function_bucket.etag)
}
