output "object_references" {
  value = {
    "get_company_details_function_bucket" : {
      etag : aws_s3_bucket_object.get_company_details_function_object.etag,
      key : aws_s3_bucket_object.get_company_details_function_object.key,
      bucket : aws_s3_bucket_object.get_company_details_function_object.bucket
    }
    "get_all_companies_function_bucket" : {
      etag : aws_s3_bucket_object.get_all_companies_function_object.etag,
      key : aws_s3_bucket_object.get_all_companies_function_object.key,
      bucket : aws_s3_bucket_object.get_all_companies_function_object.bucket
    }
    "lambda_layer_bucket" : {
      etag : aws_s3_bucket_object.layer_libraries_object.etag,
      key : aws_s3_bucket_object.layer_libraries_object.key,
      bucket : aws_s3_bucket_object.layer_libraries_object.bucket
    }
    "glue_trigger_function_bucket" : {
      etag : aws_s3_bucket_object.glue_trigger_function_object.etag,
      key : aws_s3_bucket_object.glue_trigger_function_object.key,
      bucket : aws_s3_bucket_object.glue_trigger_function_object.bucket
    }
    
    "get_universe_overview_function_bucket" : {
      etag : aws_s3_bucket_object.get_universe_overview_function_object.etag,
      key : aws_s3_bucket_object.get_universe_overview_function_object.key,
      bucket : aws_s3_bucket_object.get_universe_overview_function_object.bucket
    }

    "get_company_report_vs_peers_function_bucket" : {
      etag : aws_s3_bucket_object.get_company_report_vs_peers_function_object.etag,
      key : aws_s3_bucket_object.get_company_report_vs_peers_function_object.key,
      bucket : aws_s3_bucket_object.get_company_report_vs_peers_function_object.bucket
    }

    "get_comparison_vs_peers_function_bucket" : {
      etag : aws_s3_bucket_object.get_comparison_vs_peers_function_object.etag,
      key : aws_s3_bucket_object.get_comparison_vs_peers_function_object.key,
      bucket : aws_s3_bucket_object.get_comparison_vs_peers_function_object.bucket
    }
    "download_comparison_vs_peers_function_bucket" : {
      etag : aws_s3_bucket_object.download_comparison_vs_peers_function_object.etag,
      key : aws_s3_bucket_object.download_comparison_vs_peers_function_object.key,
      bucket : aws_s3_bucket_object.download_comparison_vs_peers_function_object.bucket
    }

    "get_by_metric_report_function_bucket": {
      etag : aws_s3_bucket_object.get_by_metric_report_function_object.etag,
      key : aws_s3_bucket_object.get_by_metric_report_function_object.key,
      bucket : aws_s3_bucket_object.get_by_metric_report_function_object.bucket
    }

    "get_dynamic_report_function_bucket": {
      etag : aws_s3_bucket_object.get_dynamic_report_function_object.etag,
      key : aws_s3_bucket_object.get_dynamic_report_function_object.key,
      bucket : aws_s3_bucket_object.get_dynamic_report_function_object.bucket
    }

    "add_user_to_customer_group_function_bucket" : {
      etag : aws_s3_bucket_object.add_user_to_customer_group_function_object.etag,
      key : aws_s3_bucket_object.add_user_to_customer_group_function_object.key,
      bucket : aws_s3_bucket_object.add_user_to_customer_group_function_object.bucket
    }

    "authorize_function_bucket" : {
      etag: aws_s3_bucket_object.authorize_function_object.etag,
      key : aws_s3_bucket_object.authorize_function_object.key,
      bucket : aws_s3_bucket_object.authorize_function_object.bucket
    }

    "verify_users_with_same_email_function_bucket" : {
      etag : aws_s3_bucket_object.verify_users_with_same_email_function_object.etag,
      key : aws_s3_bucket_object.verify_users_with_same_email_function_object.key,
      bucket : aws_s3_bucket_object.verify_users_with_same_email_function_object.bucket
    }

    "get_users_function_bucket" : {
      etag: aws_s3_bucket_object.get_users_function_object.etag,
      key : aws_s3_bucket_object.get_users_function_object.key,
      bucket : aws_s3_bucket_object.get_users_function_object.bucket
    }
    
    "get_roles_function_bucket" : {
      etag : aws_s3_bucket_object.get_roles_function_object.etag,
      key : aws_s3_bucket_object.get_roles_function_object.key,
      bucket : aws_s3_bucket_object.get_roles_function_object.bucket
    }

    "get_user_details_function_bucket": {
      etag : aws_s3_bucket_object.get_user_details_function_object.etag,
      key : aws_s3_bucket_object.get_user_details_function_object.key,
      bucket : aws_s3_bucket_object.get_user_details_function_object.bucket
    }

    "change_user_role_function_bucket": {
      etag : aws_s3_bucket_object.change_user_role_function_object.etag,
      key : aws_s3_bucket_object.change_user_role_function_object.key,
      bucket : aws_s3_bucket_object.change_user_role_function_object.bucket
    }

    "assign_company_permissions_function_bucket": {
      etag : aws_s3_bucket_object.assign_company_permissions_function_object.etag,
      key : aws_s3_bucket_object.assign_company_permissions_function_object.key,
      bucket : aws_s3_bucket_object.assign_company_permissions_function_object.bucket
    }

    "get_company_permissions_function_bucket": {
      etag : aws_s3_bucket_object.get_company_permissions_function_object.etag,
      key : aws_s3_bucket_object.get_company_permissions_function_object.key,
      bucket : aws_s3_bucket_object.get_company_permissions_function_object.bucket
    }

    "change_company_publicly_function_bucket": {
      etag : aws_s3_bucket_object.change_company_publicly_function_object.etag,
      key : aws_s3_bucket_object.change_company_publicly_function_object.key,
      bucket : aws_s3_bucket_object.change_company_publicly_function_object.bucket
     }

    "get_all_public_companies_function_bucket" : {
      etag : aws_s3_bucket_object.get_all_public_companies_function_object.etag,
      key : aws_s3_bucket_object.get_all_public_companies_function_object.key,
      bucket : aws_s3_bucket_object.get_all_public_companies_function_object.bucket
    }

    "upload_file_s3_function_bucket" : {
      etag : aws_s3_bucket_object.upload_file_s3_function_object.etag,
      key : aws_s3_bucket_object.upload_file_s3_function_object.key,
      bucket : aws_s3_bucket_object.upload_file_s3_function_object.bucket
    }

    "connect_function_bucket" : {
      etag : aws_s3_bucket_object.connect_function_object.etag,
      key : aws_s3_bucket_object.connect_function_object.key,
      bucket : aws_s3_bucket_object.connect_function_object.bucket
    }

    "disconnect_function_bucket" : {
      etag : aws_s3_bucket_object.disconnect_function_object.etag,
      key : aws_s3_bucket_object.disconnect_function_object.key,
      bucket : aws_s3_bucket_object.disconnect_function_object.bucket
    }

    "message_function_bucket" : {
      etag : aws_s3_bucket_object.message_function_object.etag,
      key : aws_s3_bucket_object.message_function_object.key,
      bucket : aws_s3_bucket_object.message_function_object.bucket
    }

    "register_function_bucket" : {
      etag : aws_s3_bucket_object.register_function_object.etag,
      key : aws_s3_bucket_object.register_function_object.key,
      bucket : aws_s3_bucket_object.register_function_object.bucket
    }
    
    "validate_data_function_bucket" : {
      etag : aws_s3_bucket_object.validate_data_function_object.etag,
      key : aws_s3_bucket_object.validate_data_function_object.key,
      bucket : aws_s3_bucket_object.validate_data_function_object.bucket
    }

    "get_company_investments_function_bucket" : {
      etag : aws_s3_bucket_object.get_company_investments_function_object.etag,
      key : aws_s3_bucket_object.get_company_investments_function_object.key,
      bucket : aws_s3_bucket_object.get_company_investments_function_object.bucket
    }

    "add_investment_function_bucket" : {
      etag : aws_s3_bucket_object.add_investment_function_object.etag,
      key : aws_s3_bucket_object.add_investment_function_object.key,
      bucket : aws_s3_bucket_object.add_investment_function_object.bucket
    }

    "update_data_function_bucket" : {
      etag : aws_s3_bucket_object.update_data_function_object.etag,
      key : aws_s3_bucket_object.update_data_function_object.key,
      bucket : aws_s3_bucket_object.update_data_function_object.bucket
    }

    "add_scenario_function_bucket" : {
      etag : aws_s3_bucket_object.add_scenario_function_object.etag,
      key : aws_s3_bucket_object.add_scenario_function_object.key,
      bucket : aws_s3_bucket_object.add_scenario_function_object.bucket
    }

    "edit_modify_data_function_bucket" : {
      etag : aws_s3_bucket_object.edit_modify_data_function_object.etag,
      key : aws_s3_bucket_object.edit_modify_data_function_object.key,
      bucket : aws_s3_bucket_object.edit_modify_data_function_object.bucket
    }

    "get_edit_modify_data_function_bucket" : {
      etag : aws_s3_bucket_object.get_edit_modify_data_function_object.etag,
      key : aws_s3_bucket_object.get_edit_modify_data_function_object.key,
      bucket : aws_s3_bucket_object.get_edit_modify_data_function_object.bucket
    }

    "delete_scenarios_function_bucket" : {
      etag : aws_s3_bucket_object.delete_scenarios_function_object.etag,
      key : aws_s3_bucket_object.delete_scenarios_function_object.key,
      bucket : aws_s3_bucket_object.delete_scenarios_function_object.bucket
    }

    "delete_company_function_bucket" : {
      etag : aws_s3_bucket_object.delete_company_function_object.etag,
      key : aws_s3_bucket_object.delete_company_function_object.key,
      bucket : aws_s3_bucket_object.delete_company_function_object.bucket
    }

    "get_metric_types_function_bucket" : {
      etag : aws_s3_bucket_object.get_metric_types_function_object.etag,
      key : aws_s3_bucket_object.get_metric_types_function_object.key,
      bucket : aws_s3_bucket_object.get_metric_types_function_object.bucket
    }
    "get_investment_date_report_function_bucket" : {
      etag : aws_s3_bucket_object.get_investment_date_report_function_object.etag,
      key : aws_s3_bucket_object.get_investment_date_report_function_object.key,
      bucket : aws_s3_bucket_object.get_investment_date_report_function_object.bucket
    }

    "get_all_tags_function_bucket" : {
      etag : aws_s3_bucket_object.get_all_tags_function_object.etag,
      key : aws_s3_bucket_object.get_all_tags_function_object.key,
      bucket : aws_s3_bucket_object.get_all_tags_function_object.bucket
    }
    
    "get_tags_by_company_function_bucket" : {
      etag : aws_s3_bucket_object.get_tags_by_company_function_object.etag,
      key : aws_s3_bucket_object.get_tags_by_company_function_object.key,
      bucket : aws_s3_bucket_object.get_tags_by_company_function_object.bucket
    }

    "add_tag_function_bucket" : {
      etag : aws_s3_bucket_object.add_tag_function_object.etag,
      key : aws_s3_bucket_object.add_tag_function_object.key,
      bucket : aws_s3_bucket_object.add_tag_function_object.bucket
    }

    "update_tags_function_bucket" : {
      etag : aws_s3_bucket_object.update_tags_function_object.etag,
      key : aws_s3_bucket_object.update_tags_function_object.key,
      bucket : aws_s3_bucket_object.update_tags_function_object.bucket
    }

    "delete_tags_function_bucket" : {
      etag : aws_s3_bucket_object.delete_tags_function_object.etag,
      key : aws_s3_bucket_object.delete_tags_function_object.key,
      bucket : aws_s3_bucket_object.delete_tags_function_object.bucket
    }

    "get_all_ranges_function_bucket" : {
      etag : aws_s3_bucket_object.get_all_ranges_function_object.etag,
      key : aws_s3_bucket_object.get_all_ranges_function_object.key,
      bucket : aws_s3_bucket_object.get_all_ranges_function_object.bucket
    }

    "get_ranges_by_metric_function_bucket": {
      etag : aws_s3_bucket_object.get_ranges_by_metric_function_object.etag,
      key : aws_s3_bucket_object.get_ranges_by_metric_function_object.key,
      bucket : aws_s3_bucket_object.get_ranges_by_metric_function_object.bucket
    }
  }
}
