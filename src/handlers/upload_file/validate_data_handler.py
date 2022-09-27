import json
import logging
from preview_data_validation_service import PreviewDataValidationService
from connection import create_db_engine, create_db_session
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL
from base_exception import AppError
from app_http_headers import AppHttpHeaders

headers = AppHttpHeaders("application/json", "OPTIONS,POST,GET")
engine = create_db_engine()
session = create_db_session(engine)
query_builder = QuerySQLBuilder()
response_sql = ResponseSQL()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
preview_data_validation_service = PreviewDataValidationService(
    session, query_builder, logger, response_sql
)


def handler(event, _):
    try:
        if not event.get("body"):
            raise AppError("No company data provided")

        data = json.loads(event.get("body"))

        response = preview_data_validation_service.validate_companies_data(data)

        return {
            "statusCode": 200,
            "body": json.dumps(response, default=str),
            "headers": headers.get_headers(),
        }

    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": headers.get_headers(),
        }
