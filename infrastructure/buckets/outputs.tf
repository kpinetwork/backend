output "minimal_function_bucket" {
  value = {
    etag : data.aws_s3_bucket_object.minimal_function_zip.etag,
    key : aws_s3_bucket_object.minimal_function_object.key,
    bucket : aws_s3_bucket_object.minimal_function_object.bucket
  }
}

output "sample_function_bucket" {
  value = {
    etag : data.aws_s3_bucket_object.sample_function_zip.etag,
    key : aws_s3_bucket_object.sample_function_object.key,
    bucket : aws_s3_bucket_object.sample_function_object.bucket
  }
}