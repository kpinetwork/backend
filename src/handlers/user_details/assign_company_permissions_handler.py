import os
import json
import boto3
import logging
from user_details_service import UserDetailsService
from response_user import ResponseUser
from policy_manager import PolicyManager
from connection import create_db_engine, create_db_session
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL

logger = logging.getLogger()
logger.setLevel(logging.INFO)

boto3.Session(
    aws_access_key_id=os.environ.get("ACCESS_KEY"),
    aws_secret_access_key=os.environ.get("SECRET_KEY"),
)
cognito = boto3.client("cognito-idp")
engine = create_db_engine()
session = create_db_session(engine)
query_builder = QuerySQLBuilder()
response_sql = ResponseSQL()
response_user = ResponseUser()
policy_manager = PolicyManager()
user_service = UserDetailsService(
    logger, cognito, response_user, policy_manager, session, query_builder, response_sql
)


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
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
        }

    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": {"Content-Type": "application/json"},
        }
