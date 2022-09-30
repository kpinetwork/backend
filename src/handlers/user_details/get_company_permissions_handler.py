import json
from get_user_details_service import get_user_details_service_instance
from verify_user_permissions import verify_user_access, get_user_id_from_event
from base_exception import AppError
from app_http_headers import AppHttpHeaders

headers = AppHttpHeaders("application/json", "OPTIONS,GET")


def handler(event, _):
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
            "headers": headers.get_headers(),
        }

    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": headers.get_headers(),
        }
