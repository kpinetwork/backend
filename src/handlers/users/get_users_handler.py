import os
import json
import boto3
import logging
from users_service import UsersService

logger = logging.getLogger()
logger.setLevel(logging.INFO)

boto3.Session(
    aws_access_key_id=os.environ.get("ACCESS_KEY"),
    aws_secret_access_key=os.environ.get("SECRET_KEY"),
)

cognito = boto3.client("cognito-idp")
users_service = UsersService(logger, cognito)


def handler(event, context):
    try:

        poolId = os.environ.get("USER_POOL_ID")
        users = users_service.get_users(poolId)

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
