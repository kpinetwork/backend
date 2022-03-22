import os
import json
import boto3
import logging
from users_service import UsersService
from response_user import ResponseUser

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    try:
        boto3.Session(
            aws_access_key_id=os.environ.get("ACCESS_KEY"),
            aws_secret_access_key=os.environ.get("SECRET_KEY"),
        )

        cognito = boto3.client("cognito-idp")
        response_user = ResponseUser()
        users_service = UsersService(logger, cognito, response_user)
        pool_id = os.environ.get("USER_POOL_ID")

        limit = 10
        token = ""
        if event.get("queryStringParameters"):
            params = event.get("queryStringParameters")
            limit = int(params.get("limit", limit))
            token = params.get("token", token)

        users = users_service.get_users(pool_id, limit, token)

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
