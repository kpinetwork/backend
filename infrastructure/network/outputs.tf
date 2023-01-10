output "api_gateway_references" {
  value = {
    "apigw_get_all_companies_lambda_function": {
      resource_path: aws_api_gateway_resource.companies.path,
      http_method: aws_api_gateway_method.get_all_companies_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_all_public_companies_lambda_function": {
      resource_path: aws_api_gateway_resource.public_companies.path,
      http_method: aws_api_gateway_method.get_all_public_companies_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_company_details_lambda_function": {
      resource_path: aws_api_gateway_resource.company_details.path,
      http_method: aws_api_gateway_method.get_company_details_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_delete_company_lambda_function": {
      resource_path: aws_api_gateway_resource.company_details.path,
      http_method: aws_api_gateway_method.delete_company_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_universe_overview_lambda_function": {
      resource_path: aws_api_gateway_resource.universe_overview.path,
      http_method: aws_api_gateway_method.get_universe_overview_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_company_report_vs_peers_lambda_function": {
      resource_path: aws_api_gateway_resource.company_report_vs_peers_id.path,
      http_method: aws_api_gateway_method.get_company_report_vs_peers_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_comparison_vs_peers_lambda_function": {
      resource_path: aws_api_gateway_resource.comparison_vs_peers_id.path,
      http_method: aws_api_gateway_method.get_comparison_vs_peers_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }
    "apigw_download_comparison_vs_peers_lambda_function": {
      resource_path: aws_api_gateway_resource.download_comparison_vs_peers.path,
      http_method: aws_api_gateway_method.download_comparison_vs_peers_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }
    
    "apigw_get_investment_date_report_lambda_function": {
      resource_path: aws_api_gateway_resource.investment_date_report.path,
      http_method: aws_api_gateway_method.get_investment_date_report_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_by_metric_report_lambda_function": {
      resource_path: aws_api_gateway_resource.by_metric_report_id.path,
      http_method: aws_api_gateway_method.get_by_metric_report_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_dynamic_report_lambda_function": {
      resource_path: aws_api_gateway_resource.dynamic_report_id.path,
      http_method: aws_api_gateway_method.dynamic_report_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_users_lambda_function": {
      resource_path: aws_api_gateway_resource.users.path,
      http_method: aws_api_gateway_method.get_users_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_roles_lambda_function": {
      resource_path: aws_api_gateway_resource.roles.path,
      http_method: aws_api_gateway_method.get_roles_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_user_details_lambda_function": {
      resource_path: aws_api_gateway_resource.user.path,
      http_method: aws_api_gateway_method.get_user_details_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_change_user_role_lambda_function": {
      resource_path: aws_api_gateway_resource.user_roles.path,
      http_method: aws_api_gateway_method.change_user_role_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_assign_company_permissions_lambda_function": {
      resource_path: aws_api_gateway_resource.company_permissions.path,
      http_method: aws_api_gateway_method.assign_company_permissions_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_company_permissions_lambda_function": {
      resource_path: aws_api_gateway_resource.company_permissions.path,
      http_method: aws_api_gateway_method.get_company_permissions_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_change_company_publicly_lambda_function": {
      resource_path: aws_api_gateway_resource.change_company_publicly.path,
      http_method: aws_api_gateway_method.change_company_publicly_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_upload_file_s3_lambda_function": {
      resource_path: aws_api_gateway_resource.upload_file_s3.path,
      http_method: aws_api_gateway_method.upload_file_s3_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_validate_data_lambda_function": {
      resource_path: aws_api_gateway_resource.validate_data.path,
      http_method: aws_api_gateway_method.validate_data_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_company_investments_lambda_function": {
      resource_path: aws_api_gateway_resource.company_investments.path,
      http_method: aws_api_gateway_method.get_company_investments_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_add_investment_lambda_function": {
      resource_path: aws_api_gateway_resource.company_investments.path,
      http_method: aws_api_gateway_method.add_investment_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_delete_scenarios_lambda_function": {
      resource_path: aws_api_gateway_resource.scenarios.path,
      http_method: aws_api_gateway_method.delete_scenarios_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_add_scenario_lambda_function": {
      resource_path: aws_api_gateway_resource.scenarios.path,
      http_method: aws_api_gateway_method.add_scenario_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_edit_modify_data_lambda_function": {
      resource_path: aws_api_gateway_resource.edit_modify.path,
      http_method: aws_api_gateway_method.edit_modify_data_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_edit_modify_data_lambda_function": {
      resource_path: aws_api_gateway_resource.edit_modify.path,
      http_method: aws_api_gateway_method.get_edit_modify_data_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_metric_types_lambda_function": {
      resource_path: aws_api_gateway_resource.metric_types.path,
      http_method: aws_api_gateway_method.get_metric_types_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }
    "apigw_get_all_tags_lambda_function": {
      resource_path: aws_api_gateway_resource.tags.path,
      http_method: aws_api_gateway_method.get_all_tags_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_tags_by_company_lambda_function": {
      resource_path: aws_api_gateway_resource.tags_by_company.path,
      http_method: aws_api_gateway_method.get_tags_by_company_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }
  
     "apigw_add_tag_lambda_function": {
      resource_path: aws_api_gateway_resource.tags.path,
      http_method: aws_api_gateway_method.add_tag_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_update_tags_lambda_function": {
      resource_path: aws_api_gateway_resource.tags.path,
      http_method: aws_api_gateway_method.update_tags_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_delete_tags_lambda_function": {
      resource_path: aws_api_gateway_resource.tags.path,
      http_method: aws_api_gateway_method.delete_tags_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }
    "apigw_get_all_ranges_lambda_function": {
      resource_path: aws_api_gateway_resource.ranges.path,
      http_method: aws_api_gateway_method.get_all_ranges_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }

    "apigw_get_ranges_by_metric_lambda_function": {
      resource_path: aws_api_gateway_resource.ranges_by_metric.path,
      http_method: aws_api_gateway_method.get_ranges_by_metric_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }
    "apigw_modify_ranges_lambda_function": {
      resource_path: aws_api_gateway_resource.ranges.path,
      http_method: aws_api_gateway_method.modify_ranges_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }
    "apigw_get_full_year_total_lambda_function": {
      resource_path: aws_api_gateway_resource.full_year_by_company.path,
      http_method: aws_api_gateway_method.get_full_year_total_method.http_method,
      api_id: aws_api_gateway_rest_api.api.id
    }
  }
}

output "websocket_api_references" {
  value = {
    "api": {
      arn: aws_apigatewayv2_api.websocket_api.execution_arn
      invoke_url: aws_apigatewayv2_stage.stage.invoke_url
    }
  }
}

output "api_gateway_domain" {
  value = aws_api_gateway_domain_name.domain
}

output "api_gateway_rest_api_id" {
  value = aws_api_gateway_rest_api.api.id
}