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