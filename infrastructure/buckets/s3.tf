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

# ----------------------------------------------------------------------------------------------------------------------
# CREATE REFERENCE FROM S3 FILE UPLOADED
# @param bucket Bucket reference
# @param key Object name
# @param depends_on Set of dependencies to execute the definition
# ----------------------------------------------------------------------------------------------------------------------

data "aws_s3_bucket_object" "minimal_function_zip" {
  bucket = "kpinetwork-backend"
  key = "helloWorldHandler.zip"
  depends_on = [
    aws_s3_bucket_object.minimal_function_object
  ]
}
