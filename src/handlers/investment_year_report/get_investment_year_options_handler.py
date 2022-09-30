import json
import logging
from investment_options_service import InvestmentOptionsService
from connection import create_db_engine, create_db_session
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL
from app_http_headers import AppHttpHeaders

headers = AppHttpHeaders("application/json", "OPTIONS,GET")
engine = create_db_engine()
session = create_db_session(engine)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(__, _):
    try:
        service = InvestmentOptionsService(
            session, QuerySQLBuilder(), logger, ResponseSQL()
        )
        options = service.get_years_options()

        return {
            "statusCode": 200,
            "body": json.dumps(options),
            "headers": headers.get_headers(),
        }

    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": headers.get_headers(),
        }
