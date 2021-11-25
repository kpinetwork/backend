import json
import logging
from financial_scenario_service import FinancialScenarioService
from connection import create_db_engine, create_db_session
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL

engine = create_db_engine()
session = create_db_session(engine)
query_builder = QuerySQLBuilder()
response_sql = ResponseSQL()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
scenario_service = FinancialScenarioService(
    session, query_builder, logger, response_sql
)


def handler(event, context):
    try:
        offset = 0
        max_count = 40
        scenario_type = ""
        company_id = event.get("pathParameters", dict()).get("company_id")

        if event.get("queryStringParameters"):
            params = event.get("queryStringParameters")
            scenario_type = params.get("scenario_type", "")
            offset = int(params.get("offset", offset))
            max_count = int(params.get("limit", max_count))

        scenarios = scenario_service.get_company_scenarios(
            company_id, scenario_type, offset, max_count
        )

        return {
            "statusCode": 200,
            "body": json.dumps(scenarios, default=str),
            "headers": {"Content-Type": "application/json"},
        }

    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": {"Content-Type": "application/json"},
        }
