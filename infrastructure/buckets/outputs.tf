output "object_references" {
  value = {
    "get_company_function_bucket" : {
      etag : aws_s3_bucket_object.get_company_function_object.etag,
      key : aws_s3_bucket_object.get_company_function_object.key,
      bucket : aws_s3_bucket_object.get_company_function_object.bucket
    }
    "get_all_companies_function_bucket" : {
      etag : aws_s3_bucket_object.get_all_companies_function_object.etag,
      key : aws_s3_bucket_object.get_all_companies_function_object.key,
      bucket : aws_s3_bucket_object.get_all_companies_function_object.bucket
    }
    "get_companies_kpi_average_function_bucket" : {
      etag : aws_s3_bucket_object.get_companies_kpi_average_function_object.etag,
      key : aws_s3_bucket_object.get_companies_kpi_average_function_object.key,
      bucket : aws_s3_bucket_object.get_companies_kpi_average_function_object.bucket
    }
    "get_companies_count_by_size_function_bucket" : {
      etag : aws_s3_bucket_object.get_companies_count_by_size_function_object.etag,
      key : aws_s3_bucket_object.get_companies_count_by_size_function_object.key,
      bucket : aws_s3_bucket_object.get_companies_count_by_size_function_object.bucket
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
    "get_metric_by_company_id_function_bucket" : {
      etag : aws_s3_bucket_object.get_metric_by_company_id_function_object.etag,
      key : aws_s3_bucket_object.get_metric_by_company_id_function_object.key,
      bucket : aws_s3_bucket_object.get_metric_by_company_id_function_object.bucket
    }
    "get_metrics_function_bucket" : {
      etag : aws_s3_bucket_object.get_metrics_function_object.etag,
      key : aws_s3_bucket_object.get_metrics_function_object.key,
      bucket : aws_s3_bucket_object.get_metrics_function_object.bucket
    }

    "get_average_metrics_function_bucket" : {
      etag : aws_s3_bucket_object.get_average_metrics_function_object.etag,
      key : aws_s3_bucket_object.get_average_metrics_function_object.key,
      bucket : aws_s3_bucket_object.get_average_metrics_function_object.bucket
    }

    "get_average_metrics_by_cohort_function_bucket" : {
      etag : aws_s3_bucket_object.get_average_metrics_by_cohort_function_object.etag,
      key : aws_s3_bucket_object.get_average_metrics_by_cohort_function_object.key,
      bucket : aws_s3_bucket_object.get_average_metrics_by_cohort_function_object.bucket
    }
    "get_metrics_by_cohort_id_function_object" : {
      etag : aws_s3_bucket_object.get_metrics_by_cohort_id_function_object.etag,
      key : aws_s3_bucket_object.get_metrics_by_cohort_id_function_object.key,
      bucket : aws_s3_bucket_object.get_metrics_by_cohort_id_function_object.bucket
    }

    "get_scenarios_function_bucket" : {
      etag : aws_s3_bucket_object.get_scenarios_function_object.etag,
      key : aws_s3_bucket_object.get_scenarios_function_object.key,
      bucket : aws_s3_bucket_object.get_scenarios_function_object.bucket
    }

    "get_company_scenarios_function_bucket" : {
      etag : aws_s3_bucket_object.get_company_scenarios_function_object.etag,
      key : aws_s3_bucket_object.get_company_scenarios_function_object.key,
      bucket : aws_s3_bucket_object.get_company_scenarios_function_object.bucket
    }
    "list_scenarios_function_bucket" : {
      etag : aws_s3_bucket_object.list_scenarios_function_object.etag,
      key : aws_s3_bucket_object.list_scenarios_function_object.key,
      bucket : aws_s3_bucket_object.list_scenarios_function_object.bucket
    }
    "get_revenue_sum_by_company_function_bucket" : {
      etag : aws_s3_bucket_object.get_revenue_sum_by_company_function_object.etag,
      key : aws_s3_bucket_object.get_revenue_sum_by_company_function_object.key,
      bucket : aws_s3_bucket_object.get_revenue_sum_by_company_function_object.bucket
    }
    "get_cohort_by_id_function_bucket" : {
      etag : aws_s3_bucket_object.get_cohort_by_id_function_object.etag,
      key : aws_s3_bucket_object.get_cohort_by_id_function_object.key,
      bucket : aws_s3_bucket_object.get_cohort_by_id_function_object.bucket
    }
    "get_cohort_scenarios_function_bucket" : {
      etag : aws_s3_bucket_object.get_cohort_scenarios_function_object.etag,
      key : aws_s3_bucket_object.get_cohort_scenarios_function_object.key,
      bucket : aws_s3_bucket_object.get_cohort_scenarios_function_object.bucket
    }
    "get_cohorts_function_bucket" : {
      etag : aws_s3_bucket_object.get_cohorts_function_object.etag,
      key : aws_s3_bucket_object.get_cohorts_function_object.key,
      bucket : aws_s3_bucket_object.get_cohorts_function_object.bucket
    }

    "get_revenue_sum_by_cohort_function_bucket" : {
      etag : aws_s3_bucket_object.get_revenue_sum_by_cohort_function_object.etag,
      key : aws_s3_bucket_object.get_revenue_sum_by_cohort_function_object.key,
      bucket : aws_s3_bucket_object.get_revenue_sum_by_cohort_function_object.bucket
    }
    
    "get_growth_and_margin_function_bucket" : {
      etag : aws_s3_bucket_object.get_growth_and_margin_function_object.etag,
      key : aws_s3_bucket_object.get_growth_and_margin_function_object.key,
      bucket : aws_s3_bucket_object.get_growth_and_margin_function_object.bucket
    }

    "get_expected_growth_and_margin_function_bucket" : {
      etag : aws_s3_bucket_object.get_expected_growth_and_margin_function_object.etag,
      key : aws_s3_bucket_object.get_expected_growth_and_margin_function_object.key,
      bucket : aws_s3_bucket_object.get_expected_growth_and_margin_function_object.bucket
    }
    
    "get_revenue_and_ebitda_function_bucket" : {
      etag : aws_s3_bucket_object.get_revenue_and_ebitda_function_object.etag,
      key : aws_s3_bucket_object.get_revenue_and_ebitda_function_object.key,
      bucket : aws_s3_bucket_object.get_revenue_and_ebitda_function_object.bucket
    }
  }
}