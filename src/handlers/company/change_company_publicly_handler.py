import json
import logging
from company_service import CompanyService
from connection import create_db_engine, create_db_session
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL
from company_anonymization import CompanyAnonymization
from verify_user_permissions import verify_user_access, get_user_id_from_event
from base_exception import AppError
from app_http_headers import AppHttpHeaders

headers = AppHttpHeaders("application/json", "OPTIONS,POST,GET")
engine = create_db_engine()
session = create_db_session(engine)
query_builder = QuerySQLBuilder()
response_sql = ResponseSQL()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
company_anonymization = CompanyAnonymization(object())
company_service = CompanyService(
    session, query_builder, logger, response_sql, company_anonymization
)


def handler(event, _):
    try:
        user_id = get_user_id_from_event(event)
        access = verify_user_access(user_id)

        if not access:
            raise AppError("No permissions to change company publicly")

        if not event.get("body"):
            raise AppError("No company data provided")

        data = json.loads(event.get("body"))
        companies = data.get("companies")

        response = company_service.change_company_publicly(companies)

        return {
            "statusCode": 200,
            "body": json.dumps({"modified": response}, default=str),
            "headers": headers.get_headers(),
        }

    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": headers.get_headers(),
        }
