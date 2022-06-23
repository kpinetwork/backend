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


def get_company_id(event: str, from_details: bool) -> str:
    if from_details and event.get("pathParameters").get("id"):
        company_id = event.get("pathParameters").get("id")
    else:
        body = json.loads(event.get("body"))
        company_id = body.get("company_id")
    return company_id


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

        from_details = event.get("pathParameters").get("from_details")
        body = json.loads(event.get("body"))
        company_id = get_company_id(event, from_details)

        scenarios = body.get("scenarios")
        response = delete_scenario_service.delete_scenarios(
            company_id, scenarios, from_details
        )

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
