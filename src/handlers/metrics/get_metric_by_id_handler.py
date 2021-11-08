import json
import logging
from metrics_service import MetricsService
from connection import create_db_engine, create_db_session
from query_sql import QuerySQL

engine = create_db_engine()
session = create_db_session(engine)
query_sql = QuerySQL()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
metrics_service = MetricsService(session, query_sql, logger)


def handler(event, context):

    try:
        id = event.get("pathParameters").get("id")
        metric = metrics_service.get_metric_by_id(id)

        return {
            "statusCode": 200,
            "body": json.dumps(metric, default=str),
            "headers": {"Content-Type": "application/json"},
        }

    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": {"Content-Type": "application/json"},
        }
