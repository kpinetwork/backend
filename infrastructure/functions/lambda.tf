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

resource "aws_lambda_function" "get_company_details_lambda_function" {
  role             = var.lambdas_exec_roles_arn.get_company_details_exec_role_arn
  handler          = "get_company_details_handler.handler"
  runtime          = var.runtime
  s3_bucket        = var.object_bucket_references.get_company_details_function_bucket.bucket
  s3_key           = var.object_bucket_references.get_company_details_function_bucket.key
  function_name    = "${var.environment}_${var.lambdas_names.get_company_details_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.get_company_details_function_bucket.etag)
  timeout = 100

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
    security_group_ids = [var.security_group_id]
  }

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  environment {
    variables = {
      ACCESS_KEY   = var.aws_access_key_id
      SECRET_KEY   = var.aws_secret_access_key
      USER_POOL_ID = var.user_pool_id
      DB_HOST      = var.db_host
      DB_NAME      = var.db_name
      DB_USERNAME  = var.db_username
      DB_PASSWORD  = var.db_password
    }
  }
}

resource "aws_lambda_function" "get_all_companies_lambda_function" {
  role             = var.lambdas_exec_roles_arn.companies_exec_role_arn
  handler          = "get_all_companies_handler.handler"
  runtime          = var.runtime
  s3_bucket        = var.object_bucket_references.get_all_companies_function_bucket.bucket
  s3_key           = var.object_bucket_references.get_all_companies_function_bucket.key
  function_name    = "${var.environment}_${var.lambdas_names.get_all_companies_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.get_all_companies_function_bucket.etag)
  timeout = 100

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
    security_group_ids = [var.security_group_id]
  }

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  environment {
    variables = {
      DB_HOST     = var.db_host
      DB_NAME     = var.db_name
      DB_USERNAME = var.db_username
      DB_PASSWORD = var.db_password
    }
  }
}

resource "aws_lambda_function" "get_all_public_companies_lambda_function" {
  role             = var.lambdas_exec_roles_arn.get_all_public_companies_exec_role_arn
  handler          = "get_all_public_companies_handler.handler"
  runtime          = var.runtime
  s3_bucket        = var.object_bucket_references.get_all_public_companies_function_bucket.bucket
  s3_key           = var.object_bucket_references.get_all_public_companies_function_bucket.key
  function_name    = "${var.environment}_${var.lambdas_names.get_all_public_companies_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.get_all_public_companies_function_bucket.etag)
  timeout = 100

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
    security_group_ids = [var.security_group_id]
  }

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  environment {
    variables = {
      ACCESS_KEY   = var.aws_access_key_id
      SECRET_KEY   = var.aws_secret_access_key
      USER_POOL_ID = var.user_pool_id
      DB_HOST      = var.db_host
      DB_NAME      = var.db_name
      DB_USERNAME  = var.db_username
      DB_PASSWORD  = var.db_password
    }
  }
}

resource "aws_lambda_function" "glue_trigger_lambda_function" {
  role             = var.lambdas_exec_roles_arn.glue_trigger_lambda_exec_role
  handler          = "glue_trigger_handler.handler"
  runtime          = var.runtime
  s3_bucket        = var.object_bucket_references.glue_trigger_function_bucket.bucket
  s3_key           = var.object_bucket_references.glue_trigger_function_bucket.key
  function_name    = "${var.environment}_${var.lambdas_names.glue_trigger_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.glue_trigger_function_bucket.etag)

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

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


resource "aws_lambda_function" "get_universe_overview_lambda_function" {
  role = var.lambdas_exec_roles_arn.get_universe_overview_exec_role_arn
  handler = "get_universe_overview_handler.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.get_universe_overview_function_bucket.bucket
  s3_key = var.object_bucket_references.get_universe_overview_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.get_universe_overview_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.get_universe_overview_function_bucket.etag)
  memory_size = 128
  timeout = 100

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
    security_group_ids = [var.security_group_id]
  }

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  environment {
    variables = {
      ACCESS_KEY   = var.aws_access_key_id
      SECRET_KEY   = var.aws_secret_access_key
      USER_POOL_ID = var.user_pool_id
      DB_HOST      = var.db_host
      DB_NAME      = var.db_name
      DB_USERNAME  = var.db_username
      DB_PASSWORD  = var.db_password
    }
  }
}

resource "aws_lambda_function" "get_company_report_vs_peers_lambda_function" {
  role = var.lambdas_exec_roles_arn.get_company_report_vs_peers_exec_role_arn
  handler = "get_company_report_vs_peers_handler.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.get_company_report_vs_peers_function_bucket.bucket
  s3_key = var.object_bucket_references.get_company_report_vs_peers_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.get_company_report_vs_peers_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.get_company_report_vs_peers_function_bucket.etag)
  memory_size = 128
  timeout = 100

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
    security_group_ids = [var.security_group_id]
  }

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  environment {
    variables = {
      ACCESS_KEY   = var.aws_access_key_id
      SECRET_KEY   = var.aws_secret_access_key
      USER_POOL_ID = var.user_pool_id
      DB_HOST      = var.db_host
      DB_NAME      = var.db_name
      DB_USERNAME  = var.db_username
      DB_PASSWORD  = var.db_password
    }
  }
}

resource "aws_lambda_function" "get_comparison_vs_peers_lambda_function" {
  role = var.lambdas_exec_roles_arn.get_comparison_vs_peers_exec_role_arn
  handler = "get_comparison_vs_peers_handler.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.get_comparison_vs_peers_function_bucket.bucket
  s3_key = var.object_bucket_references.get_comparison_vs_peers_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.get_comparison_vs_peers_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.get_comparison_vs_peers_function_bucket.etag)
  memory_size = 128
  timeout = 100

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
    security_group_ids = [var.security_group_id]
  }

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  environment {
    variables = {
      ACCESS_KEY   = var.aws_access_key_id
      SECRET_KEY   = var.aws_secret_access_key
      USER_POOL_ID = var.user_pool_id
      DB_HOST      = var.db_host
      DB_NAME      = var.db_name
      DB_USERNAME  = var.db_username
      DB_PASSWORD  = var.db_password
    }
  }
}

resource "aws_lambda_function" "download_comparison_vs_peers_lambda_function" {
  role = var.lambdas_exec_roles_arn.download_comparison_vs_peers_exec_role_arn
  handler = "download_comparison_vs_peers_handler.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.download_comparison_vs_peers_function_bucket.bucket
  s3_key = var.object_bucket_references.download_comparison_vs_peers_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.download_comparison_vs_peers_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.download_comparison_vs_peers_function_bucket.etag)
  memory_size = 128
  timeout = 100

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
    security_group_ids = [var.security_group_id]
  }

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  environment {
    variables = {
      ACCESS_KEY   = var.aws_access_key_id
      SECRET_KEY   = var.aws_secret_access_key
      USER_POOL_ID = var.user_pool_id
      DB_HOST      = var.db_host
      DB_NAME      = var.db_name
      DB_USERNAME  = var.db_username
      DB_PASSWORD  = var.db_password
      FILE_PATH    = var.comparison_file_path
    }
  }
}

resource "aws_lambda_function" "get_by_metric_report_lambda_function" {
  role = var.lambdas_exec_roles_arn.get_by_metric_report_exec_role_arn
  handler = "get_by_metric_report_handler.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.get_by_metric_report_function_bucket.bucket
  s3_key = var.object_bucket_references.get_by_metric_report_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.get_by_metric_report_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.get_by_metric_report_function_bucket.etag)
  memory_size = 128
  timeout = 100

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
    security_group_ids = [var.security_group_id]
  }

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  environment {
    variables = {
      ACCESS_KEY   = var.aws_access_key_id
      SECRET_KEY   = var.aws_secret_access_key
      USER_POOL_ID = var.user_pool_id
      DB_HOST      = var.db_host
      DB_NAME      = var.db_name
      DB_USERNAME  = var.db_username
      DB_PASSWORD  = var.db_password
    }
  }
}

resource "aws_lambda_function" "get_dynamic_report_lambda_function" {
  role = var.lambdas_exec_roles_arn.get_dynamic_report_exec_role_arn
  handler = "get_dynamic_report_handler.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.get_dynamic_report_function_bucket.bucket
  s3_key = var.object_bucket_references.get_dynamic_report_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.get_dynamic_report_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.get_dynamic_report_function_bucket.etag)
  memory_size = 256
  timeout = 100

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
    security_group_ids = [var.security_group_id]
  }

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  environment {
    variables = {
      ACCESS_KEY   = var.aws_access_key_id
      SECRET_KEY   = var.aws_secret_access_key
      USER_POOL_ID = var.user_pool_id
      DB_HOST      = var.db_host
      DB_NAME      = var.db_name
      DB_USERNAME  = var.db_username
      DB_PASSWORD  = var.db_password
    }
  }
}

resource "aws_lambda_function" "add_user_to_customer_group_lambda_function" {
  role = var.lambdas_exec_roles_arn.add_user_to_customer_group_exec_role_arn
  handler = "add_user_to_customer_group_handler.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.add_user_to_customer_group_function_bucket.bucket
  s3_key = var.object_bucket_references.add_user_to_customer_group_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.add_user_to_customer_group_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.add_user_to_customer_group_function_bucket.etag)
  layers = [aws_lambda_layer_version.db_lambda_layer.arn]
  timeout = 100

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  environment {
    variables = {
      ACCESS_KEY = var.aws_access_key_id
      SECRET_KEY = var.aws_secret_access_key
      ENVIRONMENT = var.environment
    }
  }
}


resource "aws_lambda_function" "authorize_lambda_function" {
  role = var.lambdas_exec_roles_arn.authorize_exec_role_arn
  handler = "authorize_handler.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.authorize_function_bucket.bucket
  s3_key = var.object_bucket_references.authorize_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.authorize_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.authorize_function_bucket.etag)
  layers = [aws_lambda_layer_version.db_lambda_layer.arn]
  
  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  environment {
    variables = {
      REGION = var.region
      API_GATEWAY = var.api_gateway
      USER_POOL_ID = var.user_pool_id
      APP_CLIENT_ID = var.app_client_id
      AWS_ACCOUNT_ID = var.aws_account_id
    }
  }
}

resource "aws_lambda_function" "verify_users_with_same_email_lambda_function" {
  role = var.lambdas_exec_roles_arn.verify_users_with_same_email_exec_role_arn
  handler = "verify_users_with_same_email_handler.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.verify_users_with_same_email_function_bucket.bucket
  s3_key = var.object_bucket_references.verify_users_with_same_email_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.verify_users_with_same_email_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.verify_users_with_same_email_function_bucket.etag)
  layers = [aws_lambda_layer_version.db_lambda_layer.arn]
  timeout = 100

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  environment {
    variables = {
      ACCESS_KEY = var.aws_access_key_id
      SECRET_KEY = var.aws_secret_access_key
    }
  }
}

resource "aws_lambda_function" "get_users_lambda_function" {
  role = var.lambdas_exec_roles_arn.get_users_exec_role_arn
  handler = "get_users_handler.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.get_users_function_bucket.bucket
  s3_key = var.object_bucket_references.get_users_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.get_users_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.get_users_function_bucket.etag)
  layers = [aws_lambda_layer_version.db_lambda_layer.arn]
  timeout = 100

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  environment {
    variables = {
      REGION = var.region
      ACCESS_KEY = var.aws_access_key_id
      SECRET_KEY = var.aws_secret_access_key
      USER_POOL_ID = var.user_pool_id
      ENVIRONMENT = var.environment
    }
  }
}
  
resource "aws_lambda_function" "get_roles_lambda_function" {
  role = var.lambdas_exec_roles_arn.get_roles_exec_role_arn
  handler = "get_roles_handler.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.get_roles_function_bucket.bucket
  s3_key = var.object_bucket_references.get_roles_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.get_roles_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.get_roles_function_bucket.etag)
  layers = [aws_lambda_layer_version.db_lambda_layer.arn]
  timeout = 100

  
  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  environment {
    variables = {
      ACCESS_KEY = var.aws_access_key_id
      SECRET_KEY = var.aws_secret_access_key
      USER_POOL_ID = var.user_pool_id
    }
  }
}

resource "aws_lambda_function" "get_user_details_lambda_function" {
  role = var.lambdas_exec_roles_arn.get_user_details_exec_role_arn
  handler = "get_user_details_handler.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.get_user_details_function_bucket.bucket
  s3_key = var.object_bucket_references.get_user_details_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.get_user_details_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.get_user_details_function_bucket.etag)
  layers = [aws_lambda_layer_version.db_lambda_layer.arn]
  timeout = 100

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
    security_group_ids = [var.security_group_id]
  }

  environment {
    variables = {
      ACCESS_KEY = var.aws_access_key_id
      SECRET_KEY = var.aws_secret_access_key
      USER_POOL_ID = var.user_pool_id
      DB_HOST = var.db_host
      DB_NAME = var.db_name
      DB_USERNAME = var.db_username
      DB_PASSWORD = var.db_password
    }
  }
}

resource "aws_lambda_function" "change_user_role_lambda_function" {
  role = var.lambdas_exec_roles_arn.change_user_role_exec_role_arn
  handler = "change_user_role_handler.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.change_user_role_function_bucket.bucket
  s3_key = var.object_bucket_references.change_user_role_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.change_user_role_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.change_user_role_function_bucket.etag)
  layers = [aws_lambda_layer_version.db_lambda_layer.arn]
  timeout = 100

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
    security_group_ids = [var.security_group_id]
  }

  environment {
    variables = {
      ACCESS_KEY = var.aws_access_key_id
      SECRET_KEY = var.aws_secret_access_key
      USER_POOL_ID = var.user_pool_id
      DB_HOST = var.db_host
      DB_NAME = var.db_name
      DB_USERNAME = var.db_username
      DB_PASSWORD = var.db_password
      ENVIRONMENT = var.environment
    }
  }
}

resource "aws_lambda_function" "assign_company_permissions_lambda_function" {
  role = var.lambdas_exec_roles_arn.assign_company_permissions_exec_role_arn
  handler = "assign_company_permissions_handler.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.assign_company_permissions_function_bucket.bucket
  s3_key = var.object_bucket_references.assign_company_permissions_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.assign_company_permissions_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.assign_company_permissions_function_bucket.etag)
  layers = [aws_lambda_layer_version.db_lambda_layer.arn]
  timeout = 100

  
  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
    security_group_ids = [var.security_group_id]
  }

  environment {
    variables = {
      ACCESS_KEY = var.aws_access_key_id
      SECRET_KEY = var.aws_secret_access_key
      USER_POOL_ID = var.user_pool_id
      DB_HOST = var.db_host
      DB_NAME = var.db_name
      DB_USERNAME = var.db_username
      DB_PASSWORD = var.db_password
    }
  }
}

resource "aws_lambda_function" "get_company_permissions_lambda_function" {
  role = var.lambdas_exec_roles_arn.get_company_permissions_exec_role_arn
  handler = "get_company_permissions_handler.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.get_company_permissions_function_bucket.bucket
  s3_key = var.object_bucket_references.get_company_permissions_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.get_company_permissions_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.get_company_permissions_function_bucket.etag)
  layers = [aws_lambda_layer_version.db_lambda_layer.arn]
  timeout = 100

  
  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
    security_group_ids = [var.security_group_id]
  }

  environment {
    variables = {
      ACCESS_KEY = var.aws_access_key_id
      SECRET_KEY = var.aws_secret_access_key
      USER_POOL_ID = var.user_pool_id
      DB_HOST = var.db_host
      DB_NAME = var.db_name
      DB_USERNAME = var.db_username
      DB_PASSWORD = var.db_password
    }
  }
}

resource "aws_lambda_function" "change_company_publicly_lambda_function" {
  role = var.lambdas_exec_roles_arn.change_company_publicly_exec_role_arn
  handler = "change_company_publicly_handler.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.change_company_publicly_function_bucket.bucket
  s3_key = var.object_bucket_references.change_company_publicly_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.change_company_publicly_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.change_company_publicly_function_bucket.etag)
  timeout = 100

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
    security_group_ids = [var.security_group_id]
  }

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  environment {
    variables = {
      ACCESS_KEY   = var.aws_access_key_id
      SECRET_KEY   = var.aws_secret_access_key
      USER_POOL_ID = var.user_pool_id
      DB_HOST = var.db_host
      DB_NAME = var.db_name
      DB_USERNAME = var.db_username
      DB_PASSWORD = var.db_password
    }
  }
}

resource "aws_lambda_function" "upload_file_s3_lambda_function" {
  role = var.lambdas_exec_roles_arn.upload_file_s3_exec_role_arn
  handler = "upload_file_s3_handler.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.upload_file_s3_function_bucket.bucket
  s3_key = var.object_bucket_references.upload_file_s3_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.upload_file_s3_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.upload_file_s3_function_bucket.etag)
  timeout = 100

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  environment {
    variables = {
      ACCESS_KEY   = var.aws_access_key_id
      SECRET_KEY   = var.aws_secret_access_key
      BUCKET_FILES = var.bucket_files
      ENV          = var.environment
    }
  }
}

resource "aws_lambda_function" "connect_lambda_function" {
  role             = var.lambdas_exec_roles_arn.connect_exec_role_arn
  handler          = "connect.handler"
  runtime          = var.runtime
  s3_bucket        = var.object_bucket_references.connect_function_bucket.bucket
  s3_key           = var.object_bucket_references.connect_function_bucket.key
  function_name    = "${var.environment}_${var.lambdas_names.connect_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.connect_function_bucket.etag)
}

resource "aws_lambda_function" "disconnect_lambda_function" {
  role             = var.lambdas_exec_roles_arn.disconnect_exec_role_arn
  handler          = "disconnect.handler"
  runtime          = var.runtime
  s3_bucket        = var.object_bucket_references.disconnect_function_bucket.bucket
  s3_key           = var.object_bucket_references.disconnect_function_bucket.key
  function_name    = "${var.environment}_${var.lambdas_names.disconnect_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.disconnect_function_bucket.etag)
  timeout = 100
  
  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
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

resource "aws_lambda_function" "message_lambda_function" {
  role             = var.lambdas_exec_roles_arn.message_exec_role_arn
  handler          = "message.handler"
  runtime          = var.runtime
  s3_bucket        = var.object_bucket_references.message_function_bucket.bucket
  s3_key           = var.object_bucket_references.message_function_bucket.key
  function_name    = "${var.environment}_${var.lambdas_names.message_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.message_function_bucket.etag)
  timeout = 100
  
  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
    security_group_ids = [var.security_group_id]
  }

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  environment {
    variables = {
      WEBSOCKET_API = var.websocket_api_invoke_url
      DB_HOST = var.db_host
      DB_NAME = var.db_name
      DB_USERNAME = var.db_username
      DB_PASSWORD = var.db_password
    }
  }
}

resource "aws_lambda_function" "register_lambda_function" {
  role             = var.lambdas_exec_roles_arn.register_exec_role_arn
  handler          = "register.handler"
  runtime          = var.runtime
  s3_bucket        = var.object_bucket_references.register_function_bucket.bucket
  s3_key           = var.object_bucket_references.register_function_bucket.key
  function_name    = "${var.environment}_${var.lambdas_names.register_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.register_function_bucket.etag)
  timeout = 100
  
  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
    security_group_ids = [var.security_group_id]
  }

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  environment {
    variables = {
      WEBSOCKET_API = var.websocket_api_invoke_url
      DB_HOST = var.db_host
      DB_NAME = var.db_name
      DB_USERNAME = var.db_username
      DB_PASSWORD = var.db_password
    }
  }
}

resource "aws_lambda_function" "validate_data_lambda_function" {
  role = var.lambdas_exec_roles_arn.validate_data_exec_role_arn
  handler = "validate_data_handler.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.validate_data_function_bucket.bucket
  s3_key = var.object_bucket_references.validate_data_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.validate_data_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.validate_data_function_bucket.etag)
  timeout = 100

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
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

resource "aws_lambda_function" "get_company_investments_lambda_function" {
  role = var.lambdas_exec_roles_arn.company_investments_exec_role_arn
  handler = "get_company_investments_handler.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.get_company_investments_function_bucket.bucket
  s3_key = var.object_bucket_references.get_company_investments_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.get_company_investments_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.get_company_investments_function_bucket.etag)
  timeout = 100

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
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

resource "aws_lambda_function" "add_investment_lambda_function" {
  role = var.lambdas_exec_roles_arn.add_investment_exec_role_arn
  handler = "add_investment_handler.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.add_investment_function_bucket.bucket
  s3_key = var.object_bucket_references.add_investment_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.add_investment_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.add_investment_function_bucket.etag)
  timeout = 100

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
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

resource "aws_lambda_function" "update_data_lambda_function" {
  role = var.lambdas_exec_roles_arn.update_data_exec_role_arn
  handler = "update_data.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.update_data_function_bucket.bucket
  s3_key = var.object_bucket_references.update_data_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.update_data_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.update_data_function_bucket.etag)
  timeout = 100

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
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


resource "aws_lambda_function" "add_scenario_lambda_function" {
  role = var.lambdas_exec_roles_arn.add_scenario_exec_role_arn
  handler = "add_scenario_handler.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.add_scenario_function_bucket.bucket
  s3_key = var.object_bucket_references.add_scenario_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.add_scenario_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.add_scenario_function_bucket.etag)
  timeout = 100

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
    security_group_ids = [var.security_group_id]
  }

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  environment {
    variables = {
      ACCESS_KEY = var.aws_access_key_id
      SECRET_KEY = var.aws_secret_access_key
      USER_POOL_ID = var.user_pool_id
      DB_HOST = var.db_host
      DB_NAME = var.db_name
      DB_USERNAME = var.db_username
      DB_PASSWORD = var.db_password
    }
  }
}

resource "aws_lambda_function" "edit_modify_data_lambda_function" {
  role = var.lambdas_exec_roles_arn.edit_modify_data_exec_role_arn
  handler = "edit_data_handler.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.edit_modify_data_function_bucket.bucket
  s3_key = var.object_bucket_references.edit_modify_data_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.edit_modify_data_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.edit_modify_data_function_bucket.etag)
  timeout = 600

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
    security_group_ids = [var.security_group_id]
  }

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  environment {
    variables = {
      ACCESS_KEY = var.aws_access_key_id
      SECRET_KEY = var.aws_secret_access_key
      USER_POOL_ID = var.user_pool_id
      DB_HOST = var.db_host
      DB_NAME = var.db_name
      DB_USERNAME = var.db_username
      DB_PASSWORD = var.db_password
    }
  }
}

resource "aws_lambda_function" "get_edit_modify_data_lambda_function" {
  role = var.lambdas_exec_roles_arn.get_edit_modify_data_exec_role_arn
  handler = "get_edit_modify_data_handler.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.get_edit_modify_data_function_bucket.bucket
  s3_key = var.object_bucket_references.get_edit_modify_data_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.get_edit_modify_data_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.get_edit_modify_data_function_bucket.etag)
  timeout = 600

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
    security_group_ids = [var.security_group_id]
  }

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  environment {
    variables = {
      ACCESS_KEY = var.aws_access_key_id
      SECRET_KEY = var.aws_secret_access_key
      USER_POOL_ID = var.user_pool_id
      DB_HOST = var.db_host
      DB_NAME = var.db_name
      DB_USERNAME = var.db_username
      DB_PASSWORD = var.db_password
    }
  }
}

resource "aws_lambda_function" "delete_scenarios_lambda_function" {
  role = var.lambdas_exec_roles_arn.delete_scenarios_exec_role_arn
  handler = "delete_scenarios_handler.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.delete_scenarios_function_bucket.bucket
  s3_key = var.object_bucket_references.delete_scenarios_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.delete_scenarios_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.delete_scenarios_function_bucket.etag)
  timeout = 600

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
    security_group_ids = [var.security_group_id]
  }

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  environment {
    variables = {
      ACCESS_KEY = var.aws_access_key_id
      SECRET_KEY = var.aws_secret_access_key
      USER_POOL_ID = var.user_pool_id
      DB_HOST = var.db_host
      DB_NAME = var.db_name
      DB_USERNAME = var.db_username
      DB_PASSWORD = var.db_password
    }
  }
}

resource "aws_lambda_function" "delete_company_lambda_function" {
  role = var.lambdas_exec_roles_arn.delete_company_exec_role_arn
  handler = "delete_company_handler.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.delete_company_function_bucket.bucket
  s3_key = var.object_bucket_references.delete_company_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.delete_company_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.delete_company_function_bucket.etag)
  timeout = 100

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
    security_group_ids = [var.security_group_id]
  }

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  environment {
    variables = {
      ACCESS_KEY = var.aws_access_key_id
      SECRET_KEY = var.aws_secret_access_key
      USER_POOL_ID = var.user_pool_id
      DB_HOST = var.db_host
      DB_NAME = var.db_name
      DB_USERNAME = var.db_username
      DB_PASSWORD = var.db_password
    }
  }
}

resource "aws_lambda_function" "get_metric_types_lambda_function" {
  role = var.lambdas_exec_roles_arn.get_metric_types_exec_role_arn
  handler = "get_metric_types_handler.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.get_metric_types_function_bucket.bucket
  s3_key = var.object_bucket_references.get_metric_types_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.get_metric_types_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.get_metric_types_function_bucket.etag)
  timeout = 3

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
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

resource "aws_lambda_function" "get_investment_date_report_lambda_function" {
  role = var.lambdas_exec_roles_arn.get_investment_date_report_exec_role_arn
  handler = "get_investment_date_report_handler.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.get_investment_date_report_function_bucket.bucket
  s3_key = var.object_bucket_references.get_investment_date_report_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.get_investment_date_report_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.get_investment_date_report_function_bucket.etag)
  timeout = 100

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
    security_group_ids = [var.security_group_id]
  }

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  environment {
    variables = {
      ACCESS_KEY   = var.aws_access_key_id
      SECRET_KEY   = var.aws_secret_access_key
      USER_POOL_ID = var.user_pool_id
      DB_HOST      = var.db_host
      DB_NAME      = var.db_name
      DB_USERNAME  = var.db_username
      DB_PASSWORD  = var.db_password
    }
  }
}
resource "aws_lambda_function" "get_all_tags_lambda_function" {
  role             = var.lambdas_exec_roles_arn.get_all_tags_exec_role_arn
  handler          = "get_all_tags_handler.handler"
  runtime          = var.runtime
  s3_bucket        = var.object_bucket_references.get_all_tags_function_bucket.bucket
  s3_key           = var.object_bucket_references.get_all_tags_function_bucket.key
  function_name    = "${var.environment}_${var.lambdas_names.get_all_tags_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.get_all_tags_function_bucket.etag)
  timeout = 100

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
    security_group_ids = [var.security_group_id]
  }

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  environment {
    variables = {
      ACCESS_KEY   = var.aws_access_key_id
      SECRET_KEY   = var.aws_secret_access_key
      USER_POOL_ID = var.user_pool_id
      DB_HOST      = var.db_host
      DB_NAME      = var.db_name
      DB_USERNAME  = var.db_username
      DB_PASSWORD  = var.db_password
    }
  }
}

resource "aws_lambda_function" "get_tags_by_company_lambda_function" {
  role             = var.lambdas_exec_roles_arn.get_tags_by_company_exec_role_arn
  handler          = "get_tags_by_company_handler.handler"
  runtime          = var.runtime
  s3_bucket        = var.object_bucket_references.get_tags_by_company_function_bucket.bucket
  s3_key           = var.object_bucket_references.get_tags_by_company_function_bucket.key
  function_name    = "${var.environment}_${var.lambdas_names.get_tags_by_company_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.get_tags_by_company_function_bucket.etag)
    timeout = 100

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
    security_group_ids = [var.security_group_id]
  }

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  environment {
    variables = {
      ACCESS_KEY   = var.aws_access_key_id
      SECRET_KEY   = var.aws_secret_access_key
      USER_POOL_ID = var.user_pool_id
      DB_HOST      = var.db_host
      DB_NAME      = var.db_name
      DB_USERNAME  = var.db_username
      DB_PASSWORD  = var.db_password
    }
  }
}

resource "aws_lambda_function" "add_tag_lambda_function" {
  role             = var.lambdas_exec_roles_arn.add_tag_exec_role_arn
  handler          = "add_tag_handler.handler"
  runtime          = var.runtime
  s3_bucket        = var.object_bucket_references.add_tag_function_bucket.bucket
  s3_key           = var.object_bucket_references.add_tag_function_bucket.key
  function_name    = "${var.environment}_${var.lambdas_names.add_tag_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.add_tag_function_bucket.etag)
  timeout = 100

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
    security_group_ids = [var.security_group_id]
  }

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  environment {
    variables = {
      ACCESS_KEY   = var.aws_access_key_id
      SECRET_KEY   = var.aws_secret_access_key
      USER_POOL_ID = var.user_pool_id
      DB_HOST      = var.db_host
      DB_NAME      = var.db_name
      DB_USERNAME  = var.db_username
      DB_PASSWORD  = var.db_password
    }
  }
}

resource "aws_lambda_function" "update_tags_lambda_function" {
  role             = var.lambdas_exec_roles_arn.update_tags_exec_role_arn
  handler          = "update_tags_handler.handler"
  runtime          = var.runtime
  s3_bucket        = var.object_bucket_references.update_tags_function_bucket.bucket
  s3_key           = var.object_bucket_references.update_tags_function_bucket.key
  function_name    = "${var.environment}_${var.lambdas_names.update_tags_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.update_tags_function_bucket.etag)
  timeout = 100

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
    security_group_ids = [var.security_group_id]
  }

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  environment {
    variables = {
      ACCESS_KEY   = var.aws_access_key_id
      SECRET_KEY   = var.aws_secret_access_key
      USER_POOL_ID = var.user_pool_id
      DB_HOST      = var.db_host
      DB_NAME      = var.db_name
      DB_USERNAME  = var.db_username
      DB_PASSWORD  = var.db_password
    }
  }
}

resource "aws_lambda_function" "delete_tags_lambda_function" {
  role             = var.lambdas_exec_roles_arn.delete_tags_exec_role_arn
  handler          = "delete_tags_handler.handler"
  runtime          = var.runtime
  s3_bucket        = var.object_bucket_references.delete_tags_function_bucket.bucket
  s3_key           = var.object_bucket_references.delete_tags_function_bucket.key
  function_name    = "${var.environment}_${var.lambdas_names.delete_tags_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.delete_tags_function_bucket.etag)
  timeout = 100

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
    security_group_ids = [var.security_group_id]
  }

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  environment {
    variables = {
      ACCESS_KEY   = var.aws_access_key_id
      SECRET_KEY   = var.aws_secret_access_key
      USER_POOL_ID = var.user_pool_id
      DB_HOST      = var.db_host
      DB_NAME      = var.db_name
      DB_USERNAME  = var.db_username
      DB_PASSWORD  = var.db_password
    }
  }
}
resource "aws_lambda_function" "get_all_ranges_lambda_function" {
  role             = var.lambdas_exec_roles_arn.get_all_ranges_exec_role_arn
  handler          = "get_all_ranges_handler.handler"
  runtime          = var.runtime
  s3_bucket        = var.object_bucket_references.get_all_ranges_function_bucket.bucket
  s3_key           = var.object_bucket_references.get_all_ranges_function_bucket.key
  function_name    = "${var.environment}_${var.lambdas_names.get_all_ranges_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.get_all_ranges_function_bucket.etag)
  timeout = 100

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
    security_group_ids = [var.security_group_id]
  }

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  environment {
    variables = {
      ACCESS_KEY   = var.aws_access_key_id
      SECRET_KEY   = var.aws_secret_access_key
      USER_POOL_ID = var.user_pool_id
      DB_HOST      = var.db_host
      DB_NAME      = var.db_name
      DB_USERNAME  = var.db_username
      DB_PASSWORD  = var.db_password
    }
  }
}


resource "aws_lambda_function" "get_ranges_by_metric_lambda_function" {
  role             = var.lambdas_exec_roles_arn.get_ranges_by_metric_exec_role_arn
  handler          = "get_ranges_by_metric_handler.handler"
  runtime          = var.runtime
  s3_bucket        = var.object_bucket_references.get_ranges_by_metric_function_bucket.bucket
  s3_key           = var.object_bucket_references.get_ranges_by_metric_function_bucket.key
  function_name    = "${var.environment}_${var.lambdas_names.get_ranges_by_metric_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.get_ranges_by_metric_function_bucket.etag)
  timeout = 100

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
    security_group_ids = [var.security_group_id]
  }

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  environment {
    variables = {
      ACCESS_KEY   = var.aws_access_key_id
      SECRET_KEY   = var.aws_secret_access_key
      USER_POOL_ID = var.user_pool_id
      DB_HOST      = var.db_host
      DB_NAME      = var.db_name
      DB_USERNAME  = var.db_username
      DB_PASSWORD  = var.db_password
    }
  }
}
resource "aws_lambda_function" "modify_ranges_lambda_function" {
  role             = var.lambdas_exec_roles_arn.modify_ranges_exec_role_arn
  handler          = "modify_ranges_handler.handler"
  runtime          = var.runtime
  s3_bucket        = var.object_bucket_references.modify_ranges_function_bucket.bucket
  s3_key           = var.object_bucket_references.modify_ranges_function_bucket.key
  function_name    = "${var.environment}_${var.lambdas_names.modify_ranges_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.modify_ranges_function_bucket.etag)
  timeout = 100

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
    security_group_ids = [var.security_group_id]
  }

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  environment {
    variables = {
      ACCESS_KEY   = var.aws_access_key_id
      SECRET_KEY   = var.aws_secret_access_key
      USER_POOL_ID = var.user_pool_id
      DB_HOST      = var.db_host
      DB_NAME      = var.db_name
      DB_USERNAME  = var.db_username
      DB_PASSWORD  = var.db_password
    }
  }
}
resource "aws_lambda_function" "get_full_year_total_lambda_function" {
  role             = var.lambdas_exec_roles_arn.get_full_year_total_exec_role_arn
  handler          = "get_full_year_total_handler.handler"
  runtime          = var.runtime
  s3_bucket        = var.object_bucket_references.get_full_year_total_function_bucket.bucket
  s3_key           = var.object_bucket_references.get_full_year_total_function_bucket.key
  function_name    = "${var.environment}_${var.lambdas_names.get_full_year_total_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.get_full_year_total_function_bucket.etag)
  timeout = 100

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
    security_group_ids = [var.security_group_id]
  }

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  environment {
    variables = {
      ACCESS_KEY   = var.aws_access_key_id
      SECRET_KEY   = var.aws_secret_access_key
      USER_POOL_ID = var.user_pool_id
      DB_HOST      = var.db_host
      DB_NAME      = var.db_name
      DB_USERNAME  = var.db_username
      DB_PASSWORD  = var.db_password
    }
  }
}

resource "aws_lambda_function" "get_quarters_report_lambda_function" {
  role = var.lambdas_exec_roles_arn.get_quarters_report_exec_role_arn
  handler = "get_quarters_report_handler.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.get_quarters_report_function_bucket.bucket
  s3_key = var.object_bucket_references.get_quarters_report_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.get_quarters_report_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.get_quarters_report_function_bucket.etag)
  memory_size = 128
  timeout = 100

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [element(var.private_subnet_ids, 0)]
    security_group_ids = [var.security_group_id]
  }

  depends_on = [
    aws_lambda_layer_version.db_lambda_layer
  ]

  environment {
    variables = {
      ACCESS_KEY   = var.aws_access_key_id
      SECRET_KEY   = var.aws_secret_access_key
      USER_POOL_ID = var.user_pool_id
      DB_HOST      = var.db_host
      DB_NAME      = var.db_name
      DB_USERNAME  = var.db_username
      DB_PASSWORD  = var.db_password
    }
  }
}
