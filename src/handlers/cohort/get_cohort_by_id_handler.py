import json
import logging
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
        cohort_id = event.get("pathParameters").get("id")
        cohort = cohort_service.get_cohort_information_by_id(cohort_id)

        return {
            "statusCode": 200,
            "body": json.dumps(cohort, default=str),
            "headers": {"Content-Type": "application/json"},
        }

    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": {"Content-Type": "application/json"},
        }
