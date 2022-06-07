import json
import logging
from commons_functions import get_condition_params
from connection import create_db_engine, create_db_session
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL
from company_anonymization import CompanyAnonymization
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


engine = create_db_engine()
session = create_db_session(engine)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_metric_report_service():
    user_service = get_user_details_service_instance()
    company_anonymization = CompanyAnonymization(user_service)
    calculator = CalculatorService(logger)
    repository = MetricReportRepository(
        session, QuerySQLBuilder(), ResponseSQL(), logger
    )
    profile_range = ProfileRange(session, QuerySQLBuilder(), logger, ResponseSQL())

    return ByMetricReport(
        logger, calculator, repository, profile_range, company_anonymization
    )


def get_header() -> dict:
    return {
        "Content-Type": "application/json",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
    }


def handler(event, _):
    try:
        report_service = get_metric_report_service()
        user_id = get_user_id_from_event(event)
        access = verify_user_access(user_id)
        company_id = event.get("pathParameters").get("company_id")
        metric = "actuals_revenue"
        from_main = False
        conditions = dict()

        if event.get("queryStringParameters"):
            params = event.get("queryStringParameters")
            conditions = get_condition_params(params)
            from_main = params.get("from_main", from_main)
            metric = params.get("metric", metric)

        username = get_username_from_user_id(user_id)
        report = report_service.get_by_metric_peers(
            company_id, username, metric, from_main, access, **conditions
        )
        return {
            "statusCode": 200,
            "body": json.dumps(report),
            "headers": get_header(),
        }

    except Exception as error:

        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": get_header(),
        }
