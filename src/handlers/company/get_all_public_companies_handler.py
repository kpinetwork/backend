import json
import logging
from company_service import CompanyService
from connection import create_db_engine, create_db_session
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL
from company_anonymization import CompanyAnonymization
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
query_builder = QuerySQLBuilder()
response_sql = ResponseSQL()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, _):
    try:
        user_service = get_user_details_service_instance()
        company_anonymization = CompanyAnonymization(user_service)
        company_service = CompanyService(
            session, query_builder, logger, response_sql, company_anonymization
        )
        offset = 0
        max_count = None
        user_id = get_user_id_from_event(event)
        access = verify_user_access(user_id)
        if event.get("queryStringParameters"):
            params = event.get("queryStringParameters")
            offset = int(params.get("offset", offset))
            max_count = int(params.get("limit", max_count))

        username = get_username_from_user_id(user_id)
        company_anonymization.set_company_permissions(username)
        companies = company_service.get_all_public_companies(offset, max_count, access)

        return {
            "statusCode": 200,
            "body": json.dumps(companies, default=str),
            "headers": headers.get_headers(),
        }

    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": headers.get_headers(),
        }
