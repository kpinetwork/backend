import json
import logging
import datetime
from cohort_service import CohortService
from connection import create_db_engine, create_db_session
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL

engine = create_db_engine()
session = create_db_session(engine)
query_builder = QuerySQLBuilder()
response_sql = ResponseSQL()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
cohort_service = CohortService(session, query_builder, logger, response_sql)


def handler(event, context):
    try:
        offset = 0
        max_count = 20
        year = datetime.datetime.today().year
        scenario_type = "Budget"
        cohort_id = ""

        if event.get("queryStringParameters"):
            params = event.get("queryStringParameters")
            offset = params.get("offset", offset)
            max_count = params.get("limit", max_count)
            scenario_type = params.get("scenario_type", scenario_type)
            cohort_id = params.get("pathParameters").get("id")
            year = params.get("year", year)

        cohorts = cohort_service.get_cohort_scenarios(
            cohort_id, scenario_type, year, offset, max_count
        )

        return {
            "statusCode": 200,
            "body": json.dumps(cohorts, default=str),
            "headers": {"Content-Type": "application/json"},
        }

    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": {"Content-Type": "application/json"},
        }
