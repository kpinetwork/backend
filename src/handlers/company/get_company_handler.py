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
company_anonymization = CompanyAnonymization()
company_service = CompanyService(
    session, query_builder, logger, response_sql, company_anonymization
)


def handler(event, context):
    try:
        company_id = event.get("pathParameters").get("id")
        company = company_service.get_company(company_id)

        return {
            "statusCode": 200,
            "body": json.dumps(company, default=str),
            "headers": {"Content-Type": "application/json"},
        }

    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": {"Content-Type": "application/json"},
        }
