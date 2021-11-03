
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

resource "aws_lambda_function" "get_company_lambda_function" {
  role = var.lambdas_exec_roles_arn.company_exec_role_arn
  handler = "getCompanyHandler.handler"
  runtime = var.runtime
  s3_bucket = var.lambdas_function_buckets.get_company_function_bucket.bucket
  s3_key = var.lambdas_function_buckets.get_company_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.get_company_lambda_function}"
  source_code_hash = base64sha256(var.lambdas_function_buckets.get_company_function_bucket.etag)

  vpc_config {
    subnet_ids = [var.public_subnet_a_id]
    security_group_ids = [var.security_group_id]
  }

  environment {
    variables = {
      DB_HOST = var.db_host
      DB_NAME = var.db_name
      DB_USERNAME = var.db_username
      DB_PASSWORD = var.db_password
    }
  }
}

resource "aws_lambda_function" "get_all_companies_lambda_function" {
  role = var.lambdas_exec_roles_arn.companies_exec_role_arn
  handler = "getAllCompaniesHandler.handler"
  runtime = var.runtime
  s3_bucket = var.lambdas_function_buckets.get_all_companies_function_bucket.bucket
  s3_key = var.lambdas_function_buckets.get_all_companies_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.get_all_companies_lambda_function}"
  source_code_hash = base64sha256(var.lambdas_function_buckets.get_all_companies_function_bucket.etag)

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids = [var.public_subnet_a_id]
    security_group_ids = [var.security_group_id]
  }

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]
  
  environment {
    variables = {
      DB_HOST = var.db_host
      DB_NAME = var.db_name
      DB_USERNAME = var.db_username
      DB_PASSWORD = var.db_password
    }
  }
}
