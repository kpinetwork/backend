import json
import logging

from company_details_service import CompanyDetails
from calculator_service import CalculatorService
from profile_range import ProfileRange
from connection import create_db_engine, create_db_session
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL
from verify_user_permissions import verify_user_access, get_user_id_from_event
from base_exception import AppError
from app_http_headers import AppHttpHeaders

headers = AppHttpHeaders("application/json", "OPTIONS,GET")
engine = create_db_engine()
session = create_db_session(engine)
query_builder = QuerySQLBuilder()
response_sql = ResponseSQL()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
calculator = CalculatorService(logger)


def get_company_details_service():
    profile_range = ProfileRange(session, QuerySQLBuilder(), logger, ResponseSQL())
    return CompanyDetails(
        session, query_builder, response_sql, calculator, profile_range, logger
    )


def handler(event, _):
    try:
        user_id = get_user_id_from_event(event)
        access = verify_user_access(user_id)
        if not access:
            raise AppError("No permissions to get the total")

        company_id = event.get("pathParameters").get("company_id")
        company_service = get_company_details_service()
        params = event.get("queryStringParameters")
        if params:
            scenario_name = params.get("scenario")
            metric = params.get("metric")
            year = params.get("year")

        details = company_service.get_full_year_total_amount(
            company_id, scenario_name, metric, year
        )

        return {
            "statusCode": 200,
            "body": json.dumps(details, default=str),
            "headers": headers.get_headers(),
        }

    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": headers.get_headers(),
        }
