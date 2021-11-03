output "object_references" {
  value = {
    "get_company_function_bucket": {
      etag : aws_s3_bucket_object.get_company_function_object.etag,
      key : aws_s3_bucket_object.get_company_function_object.key,
      bucket : aws_s3_bucket_object.get_company_function_object.bucket
    }
    "get_all_companies_function_bucket": {
      etag : aws_s3_bucket_object.get_all_companies_function_object.etag,
      key : aws_s3_bucket_object.get_all_companies_function_object.key,
      bucket : aws_s3_bucket_object.get_all_companies_function_object.bucket
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