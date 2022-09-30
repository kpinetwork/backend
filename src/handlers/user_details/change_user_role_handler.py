import os
import json
from get_user_details_service import get_user_details_service_instance
from verify_user_permissions import verify_user_access, get_user_id_from_event
from base_exception import AppError
from app_http_headers import AppHttpHeaders

headers = AppHttpHeaders("application/json", "OPTIONS,PUT")


def handler(event, _):
    try:
        if not event.get("body"):
            raise AppError("No roles data provided")

        user_service = get_user_details_service_instance()
        roles = json.loads(event.get("body"))
        email = event.get("pathParameters").get("username")
        user_pool_id = os.environ.get("USER_POOL_ID")
        env = os.environ.get("ENVIRONMENT")
        user_id = get_user_id_from_event(event)
        access = verify_user_access(user_id)

        if not access:
            raise AppError("No permissions to change user role")

        response = user_service.change_user_role(user_pool_id, env, email, roles)

        return {
            "statusCode": 200,
            "body": json.dumps({"modified": response}, default=str),
            "headers": headers.get_headers(),
        }

    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": headers.get_headers(),
        }
