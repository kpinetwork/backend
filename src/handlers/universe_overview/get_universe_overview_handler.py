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
        sectors = []
        verticals = []
        investor_profile = []
        growth_profile = []
        size = []
        year = datetime.datetime.today().year
        if event.get("queryStringParameters"):
            params = event.get("queryStringParameters")
            sectors = params.get("sector", sectors)
            verticals = params.get("vertical", verticals)
            investor_profile = params.get("investor_profile", investor_profile)
            growth_profile = params.get("growth_profile", growth_profile)
            size = params.get("size", size)
            year = params.get("year", year)

        growth_and_margin = overview_service.get_universe_overview(
            sectors, verticals, investor_profile, growth_profile, size, year
        )

        return {
            "statusCode": 200,
            "body": json.dumps(growth_and_margin, default=str),
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
