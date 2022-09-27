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


def get_number_from_query(params: dict, type: str, default: int) -> int:
    try:
        return int(params.get(type))
    except Exception as error:
        logger.info(error)
        return default


def get_boolean_from_query(params: dict, type: str) -> bool:
    return params.get(type) == "true"


def handler(event, _):
    try:
        user_id = get_user_id_from_event(event)
        access = verify_user_access(user_id)
        if not access:
            raise AppError("No permissions to get company details")

        company_id = event.get("pathParameters").get("id")
        company_service = get_company_details_service()
        offset = 0
        limit = 20
        ordered = True
        if event.get("queryStringParameters"):
            params = event.get("queryStringParameters")
            offset = get_number_from_query(params, "offset", offset)
            limit = get_number_from_query(params, "limit", limit)
            ordered = get_boolean_from_query(params, "ordered")

        details = company_service.get_company_details(
            company_id, offset, limit, ordered
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
