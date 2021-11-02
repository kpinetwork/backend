# ----------------------------------------------------------------------------------------------------------------------
# UPLOAD THE ZIP CODE TO S3
# @param bucket Bucket to upload code
# @param key Object name
# @param source Local directory to get zip code
# @param etag Triggers updates when the value changes
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_s3_bucket_object" "minimal_function_object" {
  bucket = var.bucket_name
  key    = "${var.lambda_resource_name}/${var.environment}/helloWorldHandler.zip"
  source = "${path.module}/../../dist/helloWorldHandler.zip"
  etag   = filemd5("${path.module}/../../dist/helloWorldHandler.zip")
}

resource "aws_s3_bucket_object" "db_sample_function_object" {
  bucket = var.bucket_name
  key    = "${var.lambda_resource_name}/${var.environment}/dbSampleHandler.zip"
  source = "${path.module}/../../dist/dbSampleHandler.zip"
  etag   = filemd5("${path.module}/../../dist/dbSampleHandler.zip")
}

resource "aws_s3_bucket_object" "layer_libraries_object" {
  bucket = var.bucket_name
  key = "${var.lambda_layer_resource_name}/${var.environment}/layerLibraries.zip"
  source = "${path.module}/../../dist/layerLibraries.zip"
  etag = filemd5("${path.module}/../../dist/layerLibraries.zip")
}

resource "aws_s3_bucket_object" "glue_trigger_function_object" {
  bucket = var.bucket_name
  key    = "${var.lambda_resource_name}/${var.environment}/glueTriggerHandler.zip"
  source = "${path.module}/../../dist/glueTriggerHandler.zip"
  etag   = filemd5("${path.module}/../../dist/glueTriggerHandler.zip")
}

resource "aws_s3_bucket_object" "etl_script_object" {
  bucket = var.bucket_name
  key    = "pyspark/kpinetwork_analizer.py"
  source = "${path.module}/../../etl/kpinetwork_analizer.py"
  etag   = filemd5("${path.module}/../../etl/kpinetwork_analizer.py")
}