import json
import logging
import datetime
from company_report_vs_peers_service import CompanyReportvsPeersService
from connection import create_db_engine, create_db_session
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL
from company_anonymization import CompanyAnonymization
from base_metrics_repository import BaseMetricsRepository
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


def get_company_report_instance():
    user_service = get_user_details_service_instance()
    company_anonymization = CompanyAnonymization(user_service)
    calculator = CalculatorService(logger)
    repository = BaseMetricsRepository(
        logger, session, QuerySQLBuilder(), ResponseSQL()
    )
    profile_range = ProfileRange(session, QuerySQLBuilder(), logger, ResponseSQL())

    return CompanyReportvsPeersService(
        logger, calculator, repository, profile_range, company_anonymization
    )


def handler(event, _):
    try:
        company_report_service = get_company_report_instance()
        user_id = get_user_id_from_event(event)
        access = verify_user_access(user_id)
        company_id = event.get("pathParameters").get("company_id")
        year = datetime.datetime.today().year

        if event.get("queryStringParameters"):
            params = event.get("queryStringParameters")
            year = int(params.get("year", year))

        username = get_username_from_user_id(user_id)
        company_report = company_report_service.get_company_report(
            company_id, username, year, access
        )

        return {
            "statusCode": 200,
            "body": json.dumps(company_report),
            "headers": headers.get_headers(),
        }

    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": headers.get_headers(),
        }
