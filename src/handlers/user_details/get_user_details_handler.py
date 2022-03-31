import os
import json
from get_user_details_service import get_user_details_service_instance
from verify_user_permissions import verify_user_access, get_user_id_from_event
from base_exception import AppError


def handler(event, context):
    try:
        user_id = get_user_id_from_event(event)
        access = verify_user_access(user_id)

        if not access:
            raise AppError("No permissions to get user details")

        user_service = get_user_details_service_instance()
        email = event.get("pathParameters").get("username")
        pool_id = os.environ.get("USER_POOL_ID")
        user = user_service.get_user_details(pool_id, email)

        return {
            "statusCode": 200,
            "body": json.dumps(user, default=str),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
        }

    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": {"Content-Type": "application/json"},
        }
