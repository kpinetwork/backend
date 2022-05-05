import json
import logging
from upload_file_service import UploadFileService
from connection import create_db_engine, create_db_session
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL
from base_exception import AppError

engine = create_db_engine()
session = create_db_session(engine)
query_builder = QuerySQLBuilder()
response_sql = ResponseSQL()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
upload_file_service = UploadFileService(session, query_builder, logger, response_sql)


def handler(event, _):
    try:
        if not event.get("body"):
            raise AppError("No company data provided")

        data = json.loads(event.get("body"))

        response = upload_file_service.validate_companies_data(data)

        return {
            "statusCode": 200,
            "body": json.dumps(response, default=str),
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
