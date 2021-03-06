import json
import logging
from query_builder import QuerySQLBuilder
from edit_service import EditModifyService
from metric_type_service import MetricTypesService
from base_exception import AuthError
from response_sql import ResponseSQL
from commons_functions import get_edit_modify_condition_params
from connection import create_db_engine, create_db_session
from verify_user_permissions import verify_user_access, get_user_id_from_event


engine = create_db_engine()
session = create_db_session(engine)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


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
    return EditModifyService(
        session, QuerySQLBuilder(), object(), metric_service, ResponseSQL(), logger
    )


def handler(event, _):
    try:
        service = get_service()
        user_id = get_user_id_from_event(event)
        access = verify_user_access(user_id)

        if not access:
            raise AuthError("No permissions to get companies information")

        conditions = dict()
        if event.get("queryStringParameters"):
            params = event.get("queryStringParameters")
            conditions = get_edit_modify_condition_params(params)

        data = service.get_data(**conditions)

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
