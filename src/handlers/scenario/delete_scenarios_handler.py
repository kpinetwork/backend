import json
import logging
from base_exception import AppError
from delete_scenarios_service import DeleteScenariosService
from connection import create_db_engine, create_db_session
from query_builder import QuerySQLBuilder
from verify_user_permissions import verify_user_access, get_user_id_from_event
from response_sql import ResponseSQL

engine = create_db_engine()
session = create_db_session(engine)
query_builder = QuerySQLBuilder()
response_sql = ResponseSQL()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
delete_scenario_service = DeleteScenariosService(
    session, query_builder, logger, response_sql
)


def get_headers() -> dict:
    return {
        "Content-Type": "application/json",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,DELETE,GET",
    }


def handler(event, _):

    try:
        user_id = get_user_id_from_event(event)
        access = verify_user_access(user_id)

        if not access:
            raise AppError("No permissions to delete scenarios")

        if not event.get("body"):
            raise AppError("No scenarios data provided")

        body = json.loads(event.get("body"))
        scenarios = body.get("scenarios")
        response = delete_scenario_service.delete_scenarios(scenarios)

        return {
            "statusCode": 200,
            "body": json.dumps({"scenarios deleted": response}),
            "headers": get_headers(),
        }

    except Exception as error:

        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": get_headers(),
        }
