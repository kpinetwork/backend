import json
from get_user_details_service import get_user_details_service

user_service = get_user_details_service()


def handler(event, context):
    try:
        if not event.get("body"):
            raise Exception("No company data provided")

        data = json.loads(event.get("body"))
        username = event.get("pathParameters").get("username")
        companies = data.get("companies")

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
