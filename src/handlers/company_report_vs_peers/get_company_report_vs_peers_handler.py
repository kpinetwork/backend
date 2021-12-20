import json
import logging
import datetime
from company_report_vs_peers import CompanyReportvsPeersService
from connection import create_db_engine, create_db_session
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL

engine = create_db_engine()
session = create_db_session(engine)
query_builder = QuerySQLBuilder()
response_sql = ResponseSQL()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
company_report_service = CompanyReportvsPeersService(
    session, query_builder, logger, response_sql
)


def handler(event, context):
    try:
        company_id = event.get("pathParameters").get("company_id")
        sectors = ""
        verticals = ""
        investor_profile = ""
        growth_profile = ""
        size = ""
        year = datetime.datetime.today().year

        if event.get("queryStringParameters"):
            params = event.get("queryStringParameters")
            sectors = params.get("sector", sectors).split(",")
            verticals = params.get("vertical", verticals).split(",")
            investor_profile = params.get("investor_profile", investor_profile).split(
                ","
            )
            growth_profile = params.get("growth_profile", growth_profile).split(",")
            size = params.get("size", size).split(",")
            year = params.get("year", year)

        growth_and_margin = company_report_service.get_company_report_vs_peers(
            company_id, sectors, verticals, investor_profile, growth_profile, size, year
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
