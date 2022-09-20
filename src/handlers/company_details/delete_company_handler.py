import json
import logging
from company_details_service import CompanyDetails
from connection import create_db_engine, create_db_session
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL
from verify_user_permissions import verify_user_access, get_user_id_from_event
from base_exception import AppError
from app_http_headers import AppHttpHeaders

headers = AppHttpHeaders("application/json", "OPTIONS,DELETE")
engine = create_db_engine()
session = create_db_session(engine)
query_builder = QuerySQLBuilder()
response_sql = ResponseSQL()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_company_details_service():
    return CompanyDetails(
        session, query_builder, response_sql, object(), object(), logger
    )


def handler(event, _):
    try:
        user_id = get_user_id_from_event(event)
        access = verify_user_access(user_id)
        if not access:
            raise AppError("No permissions to delete companies")

        company_id = event.get("pathParameters").get("id")
        company_service = get_company_details_service()

        deleted = company_service.delete_company(company_id)

        return {
            "statusCode": 200,
            "body": json.dumps({"deleted": deleted}),
            "headers": headers.get_headers(),
        }

    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": headers.get_headers(),
        }
