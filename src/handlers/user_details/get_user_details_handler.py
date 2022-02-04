import os
import json
import boto3
import logging
from user_details_service import UserDetailsService
from response_user import ResponseUser

logger = logging.getLogger()
logger.setLevel(logging.INFO)

boto3.Session(
    aws_access_key_id=os.environ.get("ACCESS_KEY"),
    aws_secret_access_key=os.environ.get("SECRET_KEY"),
)

cognito = boto3.client("cognito-idp")
response_user = ResponseUser()
user_service = UserDetailsService(logger, cognito, response_user)


def handler(event, context):
    try:
        email = event.get("pathParameters").get("username")
        pool_id = os.environ.get("USER_POOL_ID")
        user = user_service.get_user_details(pool_id, email)

        return {
            "statusCode": 200,
            "body": json.dumps(user, default=str),
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
