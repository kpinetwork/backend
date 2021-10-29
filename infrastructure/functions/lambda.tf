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
  role             = var.lambdas_exec_roles_arn.company_exec_role_arn
  handler          = "get_company_handler.handler"
  runtime          = var.runtime
  s3_bucket        = var.object_bucket_references.get_company_function_bucket.bucket
  s3_key           = var.object_bucket_references.get_company_function_bucket.key
  function_name    = "${var.environment}_${var.lambdas_names.get_company_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.get_company_function_bucket.etag)

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [var.public_subnet_a_id]
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

resource "aws_lambda_function" "get_all_companies_lambda_function" {
  role             = var.lambdas_exec_roles_arn.companies_exec_role_arn
  handler          = "get_all_companies_handler.handler"
  runtime          = var.runtime
  s3_bucket        = var.object_bucket_references.get_all_companies_function_bucket.bucket
  s3_key           = var.object_bucket_references.get_all_companies_function_bucket.key
  function_name    = "${var.environment}_${var.lambdas_names.get_all_companies_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.get_all_companies_function_bucket.etag)

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [var.public_subnet_a_id]
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

resource "aws_lambda_function" "glue_trigger_lambda_function" {
  role             = var.lambdas_exec_roles_arn.glue_trigger_lambda_exec_role
  handler          = "glue_trigger_handler.handler"
  runtime          = var.runtime
  s3_bucket        = var.object_bucket_references.glue_trigger_function_bucket.bucket
  s3_key           = var.object_bucket_references.glue_trigger_function_bucket.key
  function_name    = "${var.environment}_${var.lambdas_names.glue_trigger_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.glue_trigger_function_bucket.etag)
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

resource "aws_lambda_function" "get_metric_by_company_id_function" {
  role               = var.lambdas_exec_roles_arn.metric_exec_role_arn
  handler            = "get_metric_by_company_id_handler.handler"
  runtime            = var.runtime
  s3_bucket          = var.object_bucket_references.get_metric_by_company_id_function_bucket.bucket
  s3_key             = var.object_bucket_references.get_metric_by_company_id_function_bucket.key
  function_name      = "${var.environment}_${var.lambdas_names.get_metric_by_company_id_lambda_function}"
  source_code_hash   = base64sha256(var.object_bucket_references.get_metric_by_company_id_function_bucket.etag)
  layers             = [aws_lambda_layer_version.db_lambda_layer.arn]
  depends_on         = [
    aws_lambda_layer_version.db_lambda_layer
  ]
  vpc_config {
    subnet_ids         = [var.public_subnet_a_id]
    security_group_ids = [var.security_group_id]
  }
  environment {
    variables = {
      DB_HOST     = var.db_host
      DB_NAME     = var.db_name
      DB_USERNAME = var.db_username
      DB_PASSWORD = var.db_password
    }
  }
}

resource "aws_lambda_function" "get_average_metrics_function" {
  role               = var.lambdas_exec_roles_arn.get_average_metrics_exec_role_arn
  handler            = "get_average_metrics_handler.handler"
  runtime            = var.runtime
  s3_bucket          = var.object_bucket_references.get_average_metrics_function_bucket.bucket
  s3_key             = var.object_bucket_references.get_average_metrics_function_bucket.key
  function_name      = "${var.environment}_${var.lambdas_names.get_average_metrics_lambda_function}"
  source_code_hash   = base64sha256(var.object_bucket_references.get_average_metrics_function_bucket.etag)
  layers             = [aws_lambda_layer_version.db_lambda_layer.arn]
  depends_on         = [
    aws_lambda_layer_version.db_lambda_layer
  ]
  vpc_config {
    subnet_ids         = [var.public_subnet_a_id]
    security_group_ids = [var.security_group_id]
  }
  environment {
    variables = {
      DB_HOST     = var.db_host
      DB_NAME     = var.db_name
      DB_USERNAME = var.db_username
      DB_PASSWORD = var.db_password
    }
  }
}

resource "aws_lambda_function" "get_average_metrics_by_cohort_function" {
  role               = var.lambdas_exec_roles_arn.get_average_metrics_by_cohort_exec_role_arn
  handler            = "get_average_metrics_by_cohort_handler.handler"
  runtime            = var.runtime
  s3_bucket          = var.object_bucket_references.get_average_metrics_by_cohort_function_bucket.bucket
  s3_key             = var.object_bucket_references.get_average_metrics_by_cohort_function_bucket.key
  function_name      = "${var.environment}_${var.lambdas_names.get_average_metrics_by_cohort_lambda_function}"
  source_code_hash   = base64sha256(var.object_bucket_references.get_average_metrics_by_cohort_function_bucket.etag)
  layers             = [aws_lambda_layer_version.db_lambda_layer.arn]
  depends_on         = [
    aws_lambda_layer_version.db_lambda_layer
  ]
  vpc_config {
    subnet_ids         = [var.public_subnet_a_id]
    security_group_ids = [var.security_group_id]
  }
  environment {
    variables = {
      DB_HOST     = var.db_host
      DB_NAME     = var.db_name
      DB_USERNAME = var.db_username
      DB_PASSWORD = var.db_password
    }
  }
}

resource "aws_lambda_function" "get_metrics_by_cohort_id_function" {
  role               = var.lambdas_exec_roles_arn.get_metrics_by_cohort_id_exec_role_arn
  handler            = "get_metrics_by_cohort_id_handler.handler"
  runtime            = var.runtime
  s3_bucket          = var.object_bucket_references.get_metrics_by_cohort_id_function_object.bucket
  s3_key             = var.object_bucket_references.get_metrics_by_cohort_id_function_object.key
  function_name      = "${var.environment}_${var.lambdas_names.get_metrics_by_cohort_id_lambda_function}"
  source_code_hash   = base64sha256(var.object_bucket_references.get_metrics_by_cohort_id_function_object.etag)
  
  layers             = [aws_lambda_layer_version.db_lambda_layer.arn]

  vpc_config {
    subnet_ids         = [var.public_subnet_a_id]
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

resource "aws_lambda_function" "get_scenarios_lambda_function" {
  role = var.lambdas_exec_roles_arn.get_scenarios_exec_role_arn
  handler = "get_scenarios_handler.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.get_scenarios_function_bucket.bucket
  s3_key = var.object_bucket_references.get_scenarios_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.get_scenarios_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.get_scenarios_function_bucket.etag)

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

resource "aws_lambda_function" "get_company_scenarios_lambda_function" {
  role = var.lambdas_exec_roles_arn.get_company_scenarios_exec_role_arn
  handler = "get_company_scenarios_handler.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.get_company_scenarios_function_bucket.bucket
  s3_key = var.object_bucket_references.get_company_scenarios_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.get_company_scenarios_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.get_company_scenarios_function_bucket.etag)

  layers = [aws_lambda_layer_version.db_lambda_layer.arn]

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

resource "aws_lambda_function" "get_metrics_function" {
  role               = var.lambdas_exec_roles_arn.metrics_exec_role_arn
  handler            = "get_metrics_handler.handler"
  runtime            = var.runtime
  s3_bucket          = var.object_bucket_references.get_metrics_function_bucket.bucket
  s3_key             = var.object_bucket_references.get_metrics_function_bucket.key
  function_name      = "${var.environment}_${var.lambdas_names.get_metrics_lambda_function}"
  source_code_hash   = base64sha256(var.object_bucket_references.get_metrics_function_bucket.etag)
  layers             = [aws_lambda_layer_version.db_lambda_layer.arn]
  depends_on         = [
    aws_lambda_layer_version.db_lambda_layer
  ]
  vpc_config {
    subnet_ids         = [var.public_subnet_a_id]
    security_group_ids = [var.security_group_id]
  }

  environment {
    variables = {
      DB_HOST     = var.db_host
      DB_NAME     = var.db_name
      DB_USERNAME = var.db_username
      DB_PASSWORD = var.db_password
    }
  }
}

resource "aws_lambda_function" "list_scenarios_lambda_function" {
  role = var.lambdas_exec_roles_arn.list_scenarios_exec_role_arn
  handler = "list_scenarios_handler.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.list_scenarios_function_bucket.bucket
  s3_key = var.object_bucket_references.list_scenarios_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.list_scenarios_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.list_scenarios_function_bucket.etag)

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

resource "aws_lambda_function" "get_revenue_sum_by_company_lambda_function" {
  role = var.lambdas_exec_roles_arn.get_revenue_sum_by_company_exec_role_arn
  handler = "get_revenue_sum_by_company_handler.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.get_revenue_sum_by_company_function_bucket.bucket
  s3_key = var.object_bucket_references.get_revenue_sum_by_company_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.get_revenue_sum_by_company_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.get_revenue_sum_by_company_function_bucket.etag)

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

resource "aws_lambda_function" "get_cohort_by_id_function" {
  role               = var.lambdas_exec_roles_arn.cohort_exec_role_arn
  handler            = "get_cohort_by_id_handler.handler"
  runtime            = var.runtime
  s3_bucket          = var.object_bucket_references.get_cohort_by_id_function_bucket.bucket
  s3_key             = var.object_bucket_references.get_cohort_by_id_function_bucket.key
  function_name      = "${var.environment}_${var.lambdas_names.get_cohort_by_id_lambda_function}"
  source_code_hash   = base64sha256(var.object_bucket_references.get_cohort_by_id_function_bucket.etag)
  layers             = [aws_lambda_layer_version.db_lambda_layer.arn]
  depends_on         = [
    aws_lambda_layer_version.db_lambda_layer
  ]
  vpc_config {
    subnet_ids         = [var.public_subnet_a_id]
    security_group_ids = [var.security_group_id]
  }
  environment {
    variables = {
      DB_HOST     = var.db_host
      DB_NAME     = var.db_name
      DB_USERNAME = var.db_username
      DB_PASSWORD = var.db_password
    }
  }
}

resource "aws_lambda_function" "get_cohorts_function" {
  role               = var.lambdas_exec_roles_arn.cohorts_exec_role_arn
  handler            = "get_cohorts_handler.handler"
  runtime            = var.runtime
  s3_bucket          = var.object_bucket_references.get_cohorts_function_bucket.bucket
  s3_key             = var.object_bucket_references.get_cohorts_function_bucket.key
  function_name      = "${var.environment}_${var.lambdas_names.get_cohorts_lambda_function}"
  source_code_hash   = base64sha256(var.object_bucket_references.get_cohorts_function_bucket.etag)
  layers             = [aws_lambda_layer_version.db_lambda_layer.arn]
  depends_on         = [
    aws_lambda_layer_version.db_lambda_layer
  ]
  vpc_config {
    subnet_ids         = [var.public_subnet_a_id]
    security_group_ids = [var.security_group_id]
  }

  environment {
    variables = {
      DB_HOST     = var.db_host
      DB_NAME     = var.db_name
      DB_USERNAME = var.db_username
      DB_PASSWORD = var.db_password
    }
  }
}

resource "aws_lambda_function" "get_cohorts_scenarios_function" {
  role               = var.lambdas_exec_roles_arn.cohort_scenario_exec_role_arn
  handler            = "get_cohort_scenarios_handler.handler"
  runtime            = var.runtime
  s3_bucket          = var.object_bucket_references.get_cohort_scenarios_function_bucket.bucket
  s3_key             = var.object_bucket_references.get_cohort_scenarios_function_bucket.key
  function_name      = "${var.environment}_${var.lambdas_names.get_cohort_scenarios_lambda_function}"
  source_code_hash   = base64sha256(var.object_bucket_references.get_cohort_scenarios_function_bucket.etag)
  layers             = [aws_lambda_layer_version.db_lambda_layer.arn]
  depends_on         = [
    aws_lambda_layer_version.db_lambda_layer
  ]
  vpc_config {
    subnet_ids         = [var.public_subnet_a_id]
    security_group_ids = [var.security_group_id]
  }

  environment {
    variables = {
      DB_HOST     = var.db_host
      DB_NAME     = var.db_name
      DB_USERNAME = var.db_username
      DB_PASSWORD = var.db_password
    }
  }
}

resource "aws_lambda_function" "get_revenue_sum_by_cohort_lambda_function" {
  role = var.lambdas_exec_roles_arn.get_revenue_sum_by_cohort_exec_role_arn
  handler = "get_revenue_sum_by_cohort_handler.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.get_revenue_sum_by_cohort_function_bucket.bucket
  s3_key = var.object_bucket_references.get_revenue_sum_by_cohort_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.get_revenue_sum_by_cohort_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.get_revenue_sum_by_cohort_function_bucket.etag)

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

resource "aws_lambda_function" "get_universe_overview_lambda_function" {
  role = var.lambdas_exec_roles_arn.get_universe_overview_exec_role_arn
  handler = "get_universe_overview_handler.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.get_universe_overview_function_bucket.bucket
  s3_key = var.object_bucket_references.get_universe_overview_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.get_universe_overview_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.get_universe_overview_function_bucket.etag)

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

resource "aws_lambda_function" "get_company_report_vs_peers_lambda_function" {
  role = var.lambdas_exec_roles_arn.get_company_report_vs_peers_exec_role_arn
  handler = "get_company_report_vs_peers_handler.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.get_company_report_vs_peers_function_bucket.bucket
  s3_key = var.object_bucket_references.get_company_report_vs_peers_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.get_company_report_vs_peers_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.get_company_report_vs_peers_function_bucket.etag)

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

resource "aws_lambda_function" "get_comparison_vs_peers_lambda_function" {
  role = var.lambdas_exec_roles_arn.get_comparison_vs_peers_exec_role_arn
  handler = "get_comparison_vs_peers_handler.handler"
  runtime = var.runtime
  s3_bucket = var.object_bucket_references.get_comparison_vs_peers_function_bucket.bucket
  s3_key = var.object_bucket_references.get_comparison_vs_peers_function_bucket.key
  function_name = "${var.environment}_${var.lambdas_names.get_comparison_vs_peers_lambda_function}"
  source_code_hash = base64sha256(var.object_bucket_references.get_comparison_vs_peers_function_bucket.etag)
  timeout = 100

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