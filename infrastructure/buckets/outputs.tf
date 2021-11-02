#output "minimal_function_bucket" {
#  value = {
#    etag : aws_s3_bucket_object.minimal_function_object.etag,
#    key : aws_s3_bucket_object.minimal_function_object.key,
#    bucket : aws_s3_bucket_object.minimal_function_object.bucket
#  }
#}
#
#output "db_sample_function_bucket" {
#  value = {
#    etag : aws_s3_bucket_object.db_sample_function_object.etag,
#    key : aws_s3_bucket_object.db_sample_function_object.key,
#    bucket : aws_s3_bucket_object.db_sample_function_object.bucket
#  }
#}

output "object_references" {
  value = {
    "minimal_function_object" : {
      etag : aws_s3_bucket_object.minimal_function_object.etag,
      key : aws_s3_bucket_object.minimal_function_object.key,
      bucket : aws_s3_bucket_object.minimal_function_object.bucket
    }
    "db_sample_function_object" : {
      etag : aws_s3_bucket_object.db_sample_function_object.etag,
      key : aws_s3_bucket_object.db_sample_function_object.key,
      bucket : aws_s3_bucket_object.db_sample_function_object.bucket
    }
    "glue_trigger_function_object" : {
      etag : aws_s3_bucket_object.glue_trigger_function_object.etag,
      key : aws_s3_bucket_object.glue_trigger_function_object.key,
      bucket : aws_s3_bucket_object.glue_trigger_function_object.bucket
    }
  }
}

output "layer_libraries_bucket" {
  value = {
    etag : aws_s3_bucket_object.layer_libraries_object.etag,
    key : aws_s3_bucket_object.layer_libraries_object.key,
    bucket : aws_s3_bucket_object.layer_libraries_object.bucket
  }
}