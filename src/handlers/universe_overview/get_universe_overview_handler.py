import json
import logging
import datetime
from universe_overview_service import UniverseOverviewService
from connection import create_db_engine, create_db_session
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL

engine = create_db_engine()
session = create_db_session(engine)
query_builder = QuerySQLBuilder()
response_sql = ResponseSQL()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
overview_service = UniverseOverviewService(session, query_builder, logger, response_sql)


def handler(event, context):
    try:
        sector = ""
        vertical = ""
        year = datetime.datetime.today().year
        if event.get("queryStringParameters"):
            params = event.get("queryStringParameters")
            sector = params.get("sector", sector)
            vertical = params.get("vertical", vertical)
            year = params.get("year", year)

        growth_and_margin = overview_service.get_universe_overview(
            sector, vertical, year
        )

        return {
            "statusCode": 200,
            "body": json.dumps(growth_and_margin, default=str),
            "headers": {"Content-Type": "application/json"},
        }

    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": {"Content-Type": "application/json"},
        }
