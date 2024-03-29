# ----------------------------------------------------------------------------------------------------------------------
# UPLOAD THE ZIP CODE TO S3
# @param bucket Bucket to upload code
# @param key Object name
# @param source Local directory to get zip code
# @param etag Triggers updates when the value changes
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_s3_bucket_object" "get_company_details_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/get_company_details_handler.zip"
  source = "${path.module}/../../dist/get_company_details_handler.zip"
  etag = filemd5("${path.module}/../../dist/get_company_details_handler.zip")
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

resource "aws_s3_bucket_object" "download_comparison_vs_peers_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/download_comparison_vs_peers_handler.zip"
  source = "${path.module}/../../dist/download_comparison_vs_peers_handler.zip"
  etag = filemd5("${path.module}/../../dist/download_comparison_vs_peers_handler.zip")
}

resource "aws_s3_bucket_object" "get_by_metric_report_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/get_by_metric_report_handler.zip"
  source = "${path.module}/../../dist/get_by_metric_report_handler.zip"
  etag = filemd5("${path.module}/../../dist/get_by_metric_report_handler.zip")
}

resource "aws_s3_bucket_object" "get_dynamic_report_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/get_dynamic_report_handler.zip"
  source = "${path.module}/../../dist/get_dynamic_report_handler.zip"
  etag = filemd5("${path.module}/../../dist/get_dynamic_report_handler.zip")
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

resource "aws_s3_bucket_object" "upload_file_s3_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/upload_file_s3_handler.zip"
  source = "${path.module}/../../dist/upload_file_s3_handler.zip"
  etag = filemd5("${path.module}/../../dist/upload_file_s3_handler.zip")
}

resource "aws_s3_bucket_object" "connect_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/connect.zip"
  source = "${path.module}/../../dist/connect.zip"
  etag = filemd5("${path.module}/../../dist/connect.zip")
}

resource "aws_s3_bucket_object" "disconnect_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/disconnect.zip"
  source = "${path.module}/../../dist/disconnect.zip"
  etag = filemd5("${path.module}/../../dist/disconnect.zip")
}

resource "aws_s3_bucket_object" "message_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/message.zip"
  source = "${path.module}/../../dist/message.zip"
  etag = filemd5("${path.module}/../../dist/message.zip")
}

resource "aws_s3_bucket_object" "register_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/register.zip"
  source = "${path.module}/../../dist/register.zip"
  etag = filemd5("${path.module}/../../dist/register.zip")
}

resource "aws_s3_bucket_object" "validate_data_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/validate_data_handler.zip"
  source = "${path.module}/../../dist/validate_data_handler.zip"
  etag = filemd5("${path.module}/../../dist/validate_data_handler.zip")
}

resource "aws_s3_bucket_object" "get_company_investments_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/get_company_investments_handler.zip"
  source = "${path.module}/../../dist/get_company_investments_handler.zip"
  etag = filemd5("${path.module}/../../dist/get_company_investments_handler.zip")
}

resource "aws_s3_bucket_object" "add_investment_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/add_investment_handler.zip"
  source = "${path.module}/../../dist/add_investment_handler.zip"
  etag = filemd5("${path.module}/../../dist/add_investment_handler.zip")
}

resource "aws_s3_bucket_object" "update_data_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/update_data.zip"
  source = "${path.module}/../../dist/update_data.zip"
  etag = filemd5("${path.module}/../../dist/update_data.zip")
}

resource "aws_s3_bucket_object" "add_scenario_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/add_scenario_handler.zip"
  source = "${path.module}/../../dist/add_scenario_handler.zip"
  etag = filemd5("${path.module}/../../dist/add_scenario_handler.zip")
}

resource "aws_s3_bucket_object" "edit_modify_data_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/edit_modify_data_handler.zip"
  source = "${path.module}/../../dist/edit_modify_data_handler.zip"
  etag = filemd5("${path.module}/../../dist/edit_modify_data_handler.zip")
}

resource "aws_s3_bucket_object" "get_edit_modify_data_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/get_edit_modify_data_handler.zip"
  source = "${path.module}/../../dist/get_edit_modify_data_handler.zip"
  etag = filemd5("${path.module}/../../dist/get_edit_modify_data_handler.zip")
}

resource "aws_s3_bucket_object" "delete_scenarios_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/delete_scenarios_handler.zip"
  source = "${path.module}/../../dist/delete_scenarios_handler.zip"
  etag = filemd5("${path.module}/../../dist/delete_scenarios_handler.zip")
}

resource "aws_s3_bucket_object" "delete_company_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/delete_company_handler.zip"
  source = "${path.module}/../../dist/delete_company_handler.zip"
  etag = filemd5("${path.module}/../../dist/delete_company_handler.zip")
}

resource "aws_s3_bucket_object" "get_metric_types_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/get_metric_types_handler.zip"
  source = "${path.module}/../../dist/get_metric_types_handler.zip"
  etag = filemd5("${path.module}/../../dist/get_metric_types_handler.zip")
}
resource "aws_s3_bucket_object" "get_investment_date_report_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/get_investment_date_report_handler.zip"
  source = "${path.module}/../../dist/get_investment_date_report_handler.zip"
  etag = filemd5("${path.module}/../../dist/get_investment_date_report_handler.zip")
}
resource "aws_s3_bucket_object" "get_all_tags_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/get_all_tags_handler.zip"
  source = "${path.module}/../../dist/get_all_tags_handler.zip"
  etag = filemd5("${path.module}/../../dist/get_all_tags_handler.zip")
}

resource "aws_s3_bucket_object" "get_tags_by_company_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/get_tags_by_company_handler.zip"
  source = "${path.module}/../../dist/get_tags_by_company_handler.zip"
  etag = filemd5("${path.module}/../../dist/get_tags_by_company_handler.zip")
}

resource "aws_s3_bucket_object" "add_tag_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/add_tag_handler.zip"
  source = "${path.module}/../../dist/add_tag_handler.zip"
  etag = filemd5("${path.module}/../../dist/add_tag_handler.zip")
}

resource "aws_s3_bucket_object" "update_tags_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/update_tags_handler.zip"
  source = "${path.module}/../../dist/update_tags_handler.zip"
  etag = filemd5("${path.module}/../../dist/update_tags_handler.zip")
}

resource "aws_s3_bucket_object" "delete_tags_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/delete_tags_handler.zip"
  source = "${path.module}/../../dist/delete_tags_handler.zip"
  etag = filemd5("${path.module}/../../dist/delete_tags_handler.zip")
}
resource "aws_s3_bucket_object" "get_all_ranges_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/get_all_ranges_handler.zip"
  source = "${path.module}/../../dist/get_all_ranges_handler.zip"
  etag = filemd5("${path.module}/../../dist/get_all_ranges_handler.zip")
}

resource "aws_s3_bucket_object" "get_ranges_by_metric_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/get_ranges_by_metric_handler.zip"
  source = "${path.module}/../../dist/get_ranges_by_metric_handler.zip"
  etag = filemd5("${path.module}/../../dist/get_ranges_by_metric_handler.zip")
}
resource "aws_s3_bucket_object" "modify_ranges_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/modify_ranges_handler.zip"
  source = "${path.module}/../../dist/modify_ranges_handler.zip"
  etag = filemd5("${path.module}/../../dist/modify_ranges_handler.zip")
}
resource "aws_s3_bucket_object" "get_full_year_total_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/get_full_year_total_handler.zip"
  source = "${path.module}/../../dist/get_full_year_total_handler.zip"
  etag = filemd5("${path.module}/../../dist/get_full_year_total_handler.zip")
}

resource "aws_s3_bucket_object" "get_quarters_report_function_object" {
  bucket = var.bucket_name
  key = "${var.lambda_resource_name}/${var.environment}/get_quarters_report_handler.zip"
  source = "${path.module}/../../dist/get_quarters_report_handler.zip"
  etag = filemd5("${path.module}/../../dist/get_quarters_report_handler.zip")
}

