import os
import boto3
from users_service import UsersService
from response_user import ResponseUser
from verify_user_permissions import verify_user_access, get_user_id_from_event
from base_exception import AppError


def get_users_service_instance(event, logger):
    user_id = get_user_id_from_event(event)
    access = verify_user_access(user_id)
    boto3.Session(
        aws_access_key_id=os.environ.get("ACCESS_KEY"),
        aws_secret_access_key=os.environ.get("SECRET_KEY"),
    )
    cognito = boto3.client("cognito-idp")
    response_user = ResponseUser()
    if not access:
        raise AppError("No permissions to get data")

    return UsersService(logger, cognito, response_user)
