import os
import json
import boto3
import logging
from user_details_service import UserDetailsService
from response_user import ResponseUser
from policy_manager import PolicyManager

logger = logging.getLogger()
logger.setLevel(logging.INFO)

boto3.Session(
    aws_access_key_id=os.environ.get("ACCESS_KEY"),
    aws_secret_access_key=os.environ.get("SECRET_KEY"),
)

cognito = boto3.client("cognito-idp")
response_user = ResponseUser()
policy_manager = PolicyManager()
user_service = UserDetailsService(logger, cognito, response_user, policy_manager)


def handler(event, context):
    try:
        username = event.get("pathParameters").get("username")
        if not (username and username.strip()):
            raise Exception("No username provided")

        response = user_service.get_user_company_permissions(username)

        return {
            "statusCode": 200,
            "body": json.dumps({"modified": response}, default=str),
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
