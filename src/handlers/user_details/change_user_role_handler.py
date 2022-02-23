import os
import json
from get_user_details_service import get_user_details_service

user_service = get_user_details_service()


def handler(event, context):
    try:
        if not event.get("body"):
            raise Exception("No roles data provided")

        roles = json.loads(event.get("body"))
        email = event.get("pathParameters").get("username")
        user_pool_id = os.environ.get("USER_POOL_ID")
        env = os.environ.get("ENVIRONMENT")

        response = user_service.change_user_role(user_pool_id, env, email, roles)

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
