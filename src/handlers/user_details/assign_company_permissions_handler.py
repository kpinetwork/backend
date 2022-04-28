import json
from get_user_details_service import get_user_details_service_instance
from verify_user_permissions import verify_user_access, get_user_id_from_event
from base_exception import AppError


def handler(event, _):
    try:
        if not event.get("body"):
            raise AppError("No company data provided")

        user_service = get_user_details_service_instance()
        data = json.loads(event.get("body"))
        username = event.get("pathParameters").get("username")
        companies = data.get("companies")
        user_id = get_user_id_from_event(event)
        access = verify_user_access(user_id)

        if not access:
            raise AppError("No permissions to assign company permissions")

        response = user_service.assign_company_permissions(username, companies)

        return {
            "statusCode": 200,
            "body": json.dumps({"modified": response}, default=str),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,PUT,GET",
            },
        }

    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": {"Content-Type": "application/json"},
        }
