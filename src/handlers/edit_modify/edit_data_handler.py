import json
import logging
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL
from edit_service import EditModifyService
from scenario_service import ScenarioService
from metric_type_service import MetricTypesService
from base_exception import AppError, AuthError
from connection import create_db_engine, create_db_session
from verify_user_permissions import verify_user_access, get_user_id_from_event


engine = create_db_engine()
session = create_db_session(engine)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_body(event: dict) -> dict:
    try:
        return json.loads(event.get("body"))
    except Exception as error:
        logger.info(error)
        raise AppError("Invalid body")


def get_headers() -> dict:
    return {
        "Content-Type": "application/json",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,PUT",
    }


def get_service():
    metric_service = MetricTypesService(
        session, QuerySQLBuilder(), ResponseSQL(), logger
    )
    scenario_service = ScenarioService(
        session, QuerySQLBuilder(), metric_service, logger
    )
    return EditModifyService(
        session, QuerySQLBuilder(), scenario_service, object(), logger
    )


def handler(event, _):
    try:
        service = get_service()
        user_id = get_user_id_from_event(event)
        access = verify_user_access(user_id)

        if not access:
            raise AuthError("No permissions to edit company and scenarios information")

        body = get_body(event)
        data = service.edit_modify_data(body)

        return {
            "statusCode": 200,
            "body": json.dumps(data),
            "headers": get_headers(),
        }

    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": get_headers(),
        }
