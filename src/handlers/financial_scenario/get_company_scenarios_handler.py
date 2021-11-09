import json
from financial_scenario_service import FinancialScenarioService
from connection import create_db_engine, create_db_session
from query_builder import QuerySQLBuilder

engine = create_db_engine()
session = create_db_session(engine)
query_builder = QuerySQLBuilder()
scenario_service = FinancialScenarioService(session, query_builder)


def handler(event, context):
    try:
        offset = 0
        max_count = 20

        if event.get("queryStringParameters"):
            params = event.get("queryStringParameters")
            company_id = event.get("company")
            offset = params.get("offset", offset)
            max_count = params.get("limit", max_count)

        scenarios = scenario_service.get_company_scenarios(
            company_id, offset, max_count
        )

        return {
            "statusCode": 200,
            "body": json.dumps(scenarios),
            "headers": {"Content-Type": "application/json"},
        }

    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": {"Content-Type": "application/json"},
        }
