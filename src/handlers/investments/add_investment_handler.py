import json
import logging
from base_exception import AppError
from investments_service import InvestmentsService
from connection import create_db_engine, create_db_session
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL
from app_http_headers import AppHttpHeaders

headers = AppHttpHeaders("application/json", "OPTIONS,POST")
engine = create_db_engine()
session = create_db_session(engine)
query_builder = QuerySQLBuilder()
response_sql = ResponseSQL()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
investment_service = InvestmentsService(session, query_builder, logger, response_sql)


def handler(event, _):
    try:

        if not event.get("body") or not event.get("pathParameters").get("company_id"):
            raise AppError("No data provided")

        company_id = event.get("pathParameters").get("company_id")
        investment = json.loads(event.get("body"))
        response = investment_service.add_investment(company_id, investment)

        return {
            "statusCode": 201,
            "body": json.dumps(
                {
                    "company_id": company_id,
                    "investment": response,
                    "added": True,
                }
            ),
            "headers": headers.get_headers(),
        }

    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": headers.get_headers(),
        }
