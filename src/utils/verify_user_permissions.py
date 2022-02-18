import os
import boto3
from response_user import ResponseUser


def get_user_id_from_event(event: dict):
    context = event.get("requestContext")

    if context and context.get("authorizer"):
        authorizer = context.get("authorizer")
        return authorizer.get("principalId")

    raise Exception("No user found")


def get_cognito_client():
    boto3.Session(
        aws_access_key_id=os.environ.get("ACCESS_KEY"),
        aws_secret_access_key=os.environ.get("SECRET_KEY"),
        region_name="us-west-2",
    )
    return boto3.client("cognito-idp")


def get_roles(user_id: str, user_pool_id: str, client) -> list:
    response_user = ResponseUser()
    groups = client.admin_list_groups_for_user(
        Username=user_id, UserPoolId=user_pool_id
    )
    return response_user.process_user_roles(groups)


def verify_user_access(user_id: str) -> bool:
    cognito = get_cognito_client()
    user_pool_id = os.environ.get("USER_POOL_ID")

    roles = get_roles(user_id, user_pool_id, cognito)

    if isinstance(roles, list):
        return "admin" in roles
    raise Exception("Cannot verified permissions")
