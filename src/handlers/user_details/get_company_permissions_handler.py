import json
from get_user_details_service import get_user_details_service_instance
from verify_user_permissions import verify_user_access, get_user_id_from_event
from base_exception import AppError


def handler(event, context):
    try:
        user_id = get_user_id_from_event(event)
        access = verify_user_access(user_id)

        if not access:
            raise AppError("No permissions to get user comany permissions")

        user_service = get_user_details_service_instance()
        username = event.get("pathParameters").get("username")
        if not (username and username.strip()):
            raise AppError("No username provided")

        response = user_service.get_user_company_permissions(username)

        return {
            "statusCode": 200,
            "body": json.dumps(response, default=str),
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
