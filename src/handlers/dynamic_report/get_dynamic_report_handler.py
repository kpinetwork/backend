import json
import logging
from connection import create_db_engine, create_db_session
from commons_functions import get_condition_params, get_list_param
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL
from company_anonymization import CompanyAnonymization
from dynamic_report import DynamicReport
from by_metric_report import ByMetricReport
from metric_report_repository import MetricReportRepository
from calculator_service import CalculatorService
from profile_range import ProfileRange
from verify_user_permissions import (
    verify_user_access,
    get_user_id_from_event,
    get_username_from_user_id,
)
from get_user_details_service import get_user_details_service_instance
from app_http_headers import AppHttpHeaders
from by_year_report_service import ByYearReportService
from base_metrics_report import BaseMetricsReport
from base_metrics_repository import BaseMetricsRepository

headers = AppHttpHeaders("application/json", "OPTIONS,GET")
engine = create_db_engine()
session = create_db_session(engine)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_metric_report_service(calculator, profile_range, company_anonymization):
    metric_report_repository = MetricReportRepository(
        session, QuerySQLBuilder(), ResponseSQL(), logger
    )

    return ByMetricReport(
        logger,
        calculator,
        metric_report_repository,
        profile_range,
        company_anonymization,
    )


def get_dynamic_report_service():
    user_service = get_user_details_service_instance()
    company_anonymization = CompanyAnonymization(user_service)
    calculator = CalculatorService(logger)
    profile_range = ProfileRange(session, QuerySQLBuilder(), logger, ResponseSQL())
    repository = BaseMetricsRepository(
        logger, session, QuerySQLBuilder(), ResponseSQL()
    )
    base_metric_report = BaseMetricsReport(
        logger, calculator, profile_range, company_anonymization
    )
    metric_report = get_metric_report_service(
        calculator, profile_range, company_anonymization
    )
    calendar_report = ByYearReportService(logger, base_metric_report, repository)

    return DynamicReport(
        logger,
        metric_report,
        calendar_report,
        repository,
        profile_range,
    )


def get_value(params, value, default_value):
    return int(params.get(value, default_value)) if params.get(value) else None


def handler(event, _):
    try:
        report_service = get_dynamic_report_service()
        user_id = get_user_id_from_event(event)
        access = verify_user_access(user_id)
        company_id = event.get("pathParameters").get("company_id")
        metrics = []
        calendar_year = None
        from_main = False
        conditions = dict()

        if event.get("queryStringParameters"):
            params = event.get("queryStringParameters")
            params.pop("tag", None)
            conditions = get_condition_params(params)
            from_main = params.get("from_main", from_main)
            metrics = get_list_param(params.get("metrics"))
            calendar_year = get_value(params, "calendar_year", calendar_year)

        username = get_username_from_user_id(user_id)
        report = report_service.get_dynamic_report(
            company_id,
            username,
            metrics,
            calendar_year,
            from_main,
            access,
            **conditions
        )
        return {
            "statusCode": 200,
            "body": json.dumps(report),
            "headers": headers.get_headers(),
        }

    except Exception as error:

        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": headers.get_headers(),
        }
