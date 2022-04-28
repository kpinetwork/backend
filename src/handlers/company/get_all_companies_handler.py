import json
import logging
from company_service import CompanyService
from connection import create_db_engine, create_db_session
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL
from company_anonymization import CompanyAnonymization

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
        offset = 0
        max_count = 20

        if event.get("queryStringParameters"):
            params = event.get("queryStringParameters")
            offset = int(params.get("offset", offset))
            max_count = int(params.get("limit", max_count))

        companies = company_service.get_all_companies(offset, max_count)

        return {
            "statusCode": 200,
            "body": json.dumps(companies, default=str),
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
