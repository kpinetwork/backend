# ----------------------------------------------------------------------------------------------------------------------
# UPLOAD THE ZIP CODE TO S3
# @param bucket Bucket to upload code
# @param key Object name
# @param source Local directory to get zip code
# @param etag Triggers updates when the value changes
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_s3_bucket_object" "minimal_function_object" {
  bucket = var.bucket_name
  key = "helloWorldHandler.zip"
  source = "${path.module}/../../dist/helloWorldHandler.zip"
  etag = filemd5("${path.module}/../../dist/helloWorldHandler.zip")
}

resource "aws_s3_bucket_object" "db_sample_function_object" {
  bucket = var.bucket_name
  key = "dbSampleHandler.zip"
  source = "${path.module}/../../dist/dbSampleHandler.zip"
  etag = filemd5("${path.module}/../../dist/dbSampleHandler.zip")
}