# ----------------------------------------------------------------------------------------------------------------------
# UPLOAD THE ZIP CODE TO S3
# @param bucket Bucket to upload code
# @param key Object name
# @param source Local directory to get zip code
# @param etag Triggers updates when the value changes
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_s3_bucket_object" "get_company_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/get_company_handler.zip"
  source = "${path.module}/../../dist/get_company_handler.zip"
  etag = filemd5("${path.module}/../../dist/get_company_handler.zip")
}

resource "aws_s3_bucket_object" "get_all_companies_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/get_all_companies_handler.zip"
  source = "${path.module}/../../dist/get_all_companies_handler.zip"
  etag = filemd5("${path.module}/../../dist/get_all_companies_handler.zip")
}

resource "aws_s3_bucket_object" "layer_libraries_object" {
  bucket = var.bucket_name
  key = "${var.lambda_layer_resource_name}/${var.environment}/layer_libraries.zip"
  source = "${path.module}/../../dist/layer_libraries.zip"
  etag = filemd5("${path.module}/../../dist/layer_libraries.zip")
}

resource "aws_s3_bucket_object" "glue_trigger_function_object" {
  bucket = var.bucket_name
  key    = "${var.lambda_resource_name}/${var.environment}/glue_trigger_handler.zip"
  source = "${path.module}/../../dist/glue_trigger_handler.zip"
  etag   = filemd5("${path.module}/../../dist/glue_trigger_handler.zip")
}

resource "aws_s3_bucket_object" "etl_script_object" {
  bucket = var.bucket_name
  key    = "pyspark/kpinetwork_analizer.py"
  source = "${path.module}/../../etl/kpinetwork_analizer.py"
  etag   = filemd5("${path.module}/../../etl/kpinetwork_analizer.py")
}

resource "aws_s3_bucket_object" "get_universe_overview_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/get_universe_overview_handler.zip"
  source = "${path.module}/../../dist/get_universe_overview_handler.zip"
  etag = filemd5("${path.module}/../../dist/get_universe_overview_handler.zip")
}

resource "aws_s3_bucket_object" "get_company_report_vs_peers_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/get_company_report_vs_peers_handler.zip"
  source = "${path.module}/../../dist/get_company_report_vs_peers_handler.zip"
  etag = filemd5("${path.module}/../../dist/get_company_report_vs_peers_handler.zip")
}

resource "aws_s3_bucket_object" "get_comparison_vs_peers_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/get_comparison_vs_peers_handler.zip"
  source = "${path.module}/../../dist/get_comparison_vs_peers_handler.zip"
  etag = filemd5("${path.module}/../../dist/get_comparison_vs_peers_handler.zip")
}

resource "aws_s3_bucket_object" "add_user_to_customer_group_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/add_user_to_customer_group_handler.zip"
  source = "${path.module}/../../dist/add_user_to_customer_group_handler.zip"
  etag = filemd5("${path.module}/../../dist/add_user_to_customer_group_handler.zip")
}


resource "aws_s3_bucket_object" "authorize_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/authorize_handler.zip"
  source = "${path.module}/../../dist/authorize_handler.zip"
  etag = filemd5("${path.module}/../../dist/authorize_handler.zip")
}

resource "aws_s3_bucket_object" "verify_users_with_same_email_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/verify_users_with_same_email_handler.zip"
  source = "${path.module}/../../dist/verify_users_with_same_email_handler.zip"
  etag = filemd5("${path.module}/../../dist/verify_users_with_same_email_handler.zip")
}

resource "aws_s3_bucket_object" "get_users_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/get_users_handler.zip"
  source = "${path.module}/../../dist/get_users_handler.zip"
  etag = filemd5("${path.module}/../../dist/get_users_handler.zip")
}

resource "aws_s3_bucket_object" "get_roles_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/get_roles_handler.zip"
  source = "${path.module}/../../dist/get_roles_handler.zip"
  etag = filemd5("${path.module}/../../dist/get_roles_handler.zip")
}

resource "aws_s3_bucket_object" "get_user_details_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/get_user_details_handler.zip"
  source = "${path.module}/../../dist/get_user_details_handler.zip"
  etag = filemd5("${path.module}/../../dist/get_user_details_handler.zip")
}

resource "aws_s3_bucket_object" "change_user_role_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/change_user_role_handler.zip"
  source = "${path.module}/../../dist/change_user_role_handler.zip"
  etag = filemd5("${path.module}/../../dist/change_user_role_handler.zip")
}

resource "aws_s3_bucket_object" "assign_company_permissions_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/assign_company_permissions_handler.zip"
  source = "${path.module}/../../dist/assign_company_permissions_handler.zip"
  etag = filemd5("${path.module}/../../dist/assign_company_permissions_handler.zip")
}

resource "aws_s3_bucket_object" "get_company_permissions_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/get_company_permissions_handler.zip"
  source = "${path.module}/../../dist/get_company_permissions_handler.zip"
  etag = filemd5("${path.module}/../../dist/get_company_permissions_handler.zip")
}

resource "aws_s3_bucket_object" "change_company_publicly_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/change_company_publicly_handler.zip"
  source = "${path.module}/../../dist/change_company_publicly_handler.zip"
  etag = filemd5("${path.module}/../../dist/change_company_publicly_handler.zip")
}

resource "aws_s3_bucket_object" "get_all_public_companies_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/get_all_public_companies_handler.zip"
  source = "${path.module}/../../dist/get_all_public_companies_handler.zip"
  etag = filemd5("${path.module}/../../dist/get_all_public_companies_handler.zip")
}
