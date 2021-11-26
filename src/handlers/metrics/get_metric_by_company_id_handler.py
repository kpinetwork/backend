import json
import logging
from metrics_service import MetricsService
from connection import create_db_engine, create_db_session
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL

engine = create_db_engine()
session = create_db_session(engine)
query_builder = QuerySQLBuilder()
response_sql = ResponseSQL()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
metrics_service = MetricsService(session, query_builder, logger, response_sql)


def handler(event, context):

    try:
        company_id = event.get("pathParameters", {}).get("company_id")
        name = ""
        scenario_type = ""

        if event.get("queryStringParameters"):
            params = event.get("queryStringParameters")
            name = params.get("name")
            scenario_type = params.get("scenario_type")

        metric = metrics_service.get_metric_by_company_id(
            company_id, name, scenario_type
        )

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
