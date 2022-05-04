import json
import os
import logging
from src.handlers.users.get_users_service_instance import get_users_service_instance

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, _):
    try:
        users_service = get_users_service_instance(event, logger)
        groups = users_service.get_roles(os.environ.get("USER_POOL_ID"))
        print("groups", groups)
        return {
            "statusCode": 200,
            "body": json.dumps(groups, default=str),
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
