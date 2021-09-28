output "minimal_function_bucket" {
  value = {
    etag : aws_s3_bucket_object.minimal_function_object.etag,
    key : aws_s3_bucket_object.minimal_function_object.key,
    bucket : aws_s3_bucket_object.minimal_function_object.bucket
  }
}

output "db_sample_function_bucket" {
  value = {
    etag : aws_s3_bucket_object.db_sample_function_object.etag,
    key : aws_s3_bucket_object.db_sample_function_object.key,
    bucket : aws_s3_bucket_object.db_sample_function_object.bucket
  }
}