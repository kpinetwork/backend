import json
import logging
from metrics_service import MetricsService
from connection import create_db_engine, create_db_session
from query_sql import QuerySQL
from response_sql import ResponseSQL

engine = create_db_engine()
session = create_db_session(engine)
query_sql = QuerySQL()
response_sql = ResponseSQL()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
metrics_service = MetricsService(session, query_sql, logger, response_sql)


def handler(event, context):
    try:
        offset = 0
        max_count = 20

        if event.get("queryStringParameters"):
            params = event.get("queryStringParameters")
            offset = params.get("offset", offset)
            max_count = params.get("limit", max_count)

        metrics = metrics_service.get_metrics(offset, max_count)

        return {
            "statusCode": 200,
            "body": json.dumps(metrics, default=str),
            "headers": {"Content-Type": "application/json"},
        }

    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": {"Content-Type": "application/json"},
        }
