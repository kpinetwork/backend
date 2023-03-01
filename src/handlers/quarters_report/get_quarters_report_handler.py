import json
import logging

from connection import create_db_engine, create_db_session
from commons_functions import get_condition_params, get_list_param
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL
from company_anonymization import CompanyAnonymization
from quarters_report import QuartersReport
from quarters_report_repository import QuartersReportRepository
from calculator_service import CalculatorService
from profile_range import ProfileRange
from verify_user_permissions import (
    verify_user_access,
    get_user_id_from_event,
    get_username_from_user_id,
)
from get_user_details_service import get_user_details_service_instance
from app_http_headers import AppHttpHeaders

headers = AppHttpHeaders("application/json", "OPTIONS,GET")
engine = create_db_engine()
session = create_db_session(engine)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_quarters_report_service():
    user_service = get_user_details_service_instance()
    company_anonymization = CompanyAnonymization(user_service)
    calculator = CalculatorService(logger)
    profile_range = ProfileRange(session, QuerySQLBuilder(), logger, ResponseSQL())
    repository = QuartersReportRepository(
        session, QuerySQLBuilder(), ResponseSQL(), logger
    )

    return QuartersReport(
        logger, calculator, repository, profile_range, company_anonymization
    )


def handler(event, _):
    try:
        report_service = get_quarters_report_service()
        user_id = get_user_id_from_event(event)
        access = verify_user_access(user_id)
        company_id = event.get("pathParameters").get("company_id")
        report_type = "Year to year"
        scenario = None
        metric = None
        years = []
        period = None
        from_main = False
        conditions = dict()

        if event.get("queryStringParameters"):
            params = event.get("queryStringParameters")
            conditions = get_condition_params(params)
            from_main = params.get("from_main", from_main)
            metric = params.get("metric", metric)
            scenario = params.get("scenario", scenario)
            report_type = params.get("report_type", report_type)
            years = get_list_param(params.get("years"))
            period = params.get("period", period)

        username = get_username_from_user_id(user_id)
        report = report_service.get_quarters_peers(
            company_id,
            username,
            report_type,
            metric,
            scenario,
            years,
            period,
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
