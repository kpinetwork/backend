import json
import logging
import datetime
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
        year = datetime.datetime.today().year
        sector = ""
        vertical = ""

        if event.get("queryStringParameters"):
            params = event.get("queryStringParameters")
            year = params.get("year", year)
            sector = params.get("sector", sector)
            vertical = params.get("vertical", vertical)

        companies_kpi_average = company_service.get_companies_kpi_average(
            year, sector, vertical
        )

        return {
            "statusCode": 200,
            "body": json.dumps(companies_kpi_average, default=str),
            "headers": {"Content-Type": "application/json"},
        }

    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": {"Content-Type": "application/json"},
        }
