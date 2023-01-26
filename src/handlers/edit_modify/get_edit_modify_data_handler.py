import json
import logging
from query_builder import QuerySQLBuilder
from edit_service import EditModifyService
from metric_type_service import MetricTypesService
from base_exception import AuthError
from response_sql import ResponseSQL
from edit_modify_repository import EditModifyRepository
from commons_functions import get_edit_modify_condition_params
from connection import create_db_engine, create_db_session
from verify_user_permissions import verify_user_access, get_user_id_from_event
from app_http_headers import AppHttpHeaders

headers = AppHttpHeaders("application/json", "OPTIONS,GET")
engine = create_db_engine()
session = create_db_session(engine)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_service():
    metric_service = MetricTypesService(
        session, QuerySQLBuilder(), ResponseSQL(), logger
    )
    edit_modify_repository = EditModifyRepository(
        session, QuerySQLBuilder(), ResponseSQL(), metric_service, logger
    )
    return EditModifyService(edit_modify_repository, object(), metric_service, logger)


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
            "headers": headers.get_headers(),
        }

    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": headers.get_headers(),
        }
