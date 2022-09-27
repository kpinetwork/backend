import json
import os
import logging
from get_users_service_instance import get_users_service_instance
from app_http_headers import AppHttpHeaders

headers = AppHttpHeaders("application/json", "OPTIONS,GET")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, _):
    try:
        users_service = get_users_service_instance(event, logger)
        groups = users_service.get_roles(os.environ.get("USER_POOL_ID"))
        return {
            "statusCode": 200,
            "body": json.dumps(groups, default=str),
            "headers": headers.get_headers(),
        }
    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": headers.get_headers(),
        }
