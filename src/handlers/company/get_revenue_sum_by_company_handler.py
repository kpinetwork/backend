import json
import logging
from company_service import CompanyService
from connection import create_db_engine, create_db_session
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL

engine = create_db_engine()
session = create_db_session(engine)
query_builder = QuerySQLBuilder()
response_sql = ResponseSQL()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
company_service = CompanyService(session, query_builder, logger, response_sql)


def handler(event, context):
    try:
        sum_revenue_by_companies = company_service.get_revenue_sum_by_company()

        return {
            "statusCode": 200,
            "body": json.dumps(sum_revenue_by_companies, default=str),
            "headers": {"Content-Type": "application/json"},
        }

    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": {"Content-Type": "application/json"},
        }