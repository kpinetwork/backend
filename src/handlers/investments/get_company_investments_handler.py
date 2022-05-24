import json
import logging
from investments_service import InvestmentsService
from connection import create_db_engine, create_db_session
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL

engine = create_db_engine()
session = create_db_session(engine)
query_builder = QuerySQLBuilder()
response_sql = ResponseSQL()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
investment_service = InvestmentsService(session, query_builder, logger, response_sql)


def handler(event, _):
    try:
        company_id = event.get("pathParameters").get("company_id")
        company = investment_service.get_company_investments(company_id)

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
