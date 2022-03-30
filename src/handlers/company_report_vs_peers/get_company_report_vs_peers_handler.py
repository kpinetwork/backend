import json
import logging
import datetime
from company_report_vs_peers_service import CompanyReportvsPeersService
from connection import create_db_engine, create_db_session
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL
from company_anonymization import CompanyAnonymization
from calculator_repository import CalculatorRepository
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


def get_company_report_instance():
    user_service = get_user_details_service_instance()
    company_anonymization = CompanyAnonymization(user_service)
    calculator = CalculatorService(logger)
    repository = CalculatorRepository(session, QuerySQLBuilder(), ResponseSQL(), logger)
    profile_range = ProfileRange(session, QuerySQLBuilder(), logger, ResponseSQL())

    return CompanyReportvsPeersService(
        logger, calculator, repository, profile_range, company_anonymization
    )


def handler(event, context):
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
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
        }

    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": {"Content-Type": "application/json"},
        }
