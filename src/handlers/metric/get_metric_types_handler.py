import json
import logging
from metric_type_service import MetricTypesService
from connection import create_db_engine, create_db_session
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL

engine = create_db_engine()
session = create_db_session(engine)
query_builder = QuerySQLBuilder()
response_sql = ResponseSQL()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_headers() -> dict:
    return {
        "Content-Type": "application/json",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,GET",
    }


def handler(__, _):
    try:
        service = MetricTypesService(session, query_builder, response_sql, logger)
        metric_names = service.get_metric_types()

        return {
            "statusCode": 200,
            "body": json.dumps(metric_names, default=str),
            "headers": get_headers(),
        }

    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": get_headers(),
        }
