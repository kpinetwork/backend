import json
from get_user_details_service import get_user_details_service

user_service = get_user_details_service()


def handler(event, context):
    try:
        username = event.get("pathParameters").get("username")
        if not (username and username.strip()):
            raise Exception("No username provided")

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
