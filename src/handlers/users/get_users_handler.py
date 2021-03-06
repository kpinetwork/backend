import json
import os
import logging
from get_users_service_instance import get_users_service_instance

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, _):
    try:
        users_service = get_users_service_instance(event, logger)
        limit = 10
        token = ""
        if event.get("queryStringParameters"):
            params = event.get("queryStringParameters")
            limit = int(params.get("limit", limit))
            token = params.get("token", token)

        users = users_service.get_users(os.environ.get("USER_POOL_ID"), limit, token)

        return {
            "statusCode": 200,
            "body": json.dumps(users, default=str),
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
