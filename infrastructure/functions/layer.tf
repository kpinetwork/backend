resource "aws_lambda_layer_version" "db_lambda_layer" {
  layer_name = "${var.environment}_${var.layer_name}"
  s3_bucket = var.object_bucket_references.lambda_layer_bucket.bucket
  s3_key = var.object_bucket_references.lambda_layer_bucket.key
  source_code_hash = base64sha256(var.object_bucket_references.lambda_layer_bucket.etag)
  compatible_runtimes = [var.runtime]
}