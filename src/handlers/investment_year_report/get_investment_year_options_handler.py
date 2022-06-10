import json
import logging
from investment_options_service import InvestmentOptionsService
from connection import create_db_engine, create_db_session
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL


engine = create_db_engine()
session = create_db_session(engine)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_headers() -> dict:
    return {
        "Content-Type": "application/json",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
    }


def handler(__, _):
    try:
        service = InvestmentOptionsService(
            session, QuerySQLBuilder(), logger, ResponseSQL()
        )
        options = service.get_years_options()

        return {
            "statusCode": 200,
            "body": json.dumps(options),
            "headers": get_headers(),
        }

    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": get_headers(),
        }
