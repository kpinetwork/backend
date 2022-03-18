import os
import boto3
import logging
from user_details_service import UserDetailsService
from response_user import ResponseUser
from policy_manager import PolicyManager
from connection import create_db_engine, create_db_session
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL


def get_cognito_resource():
    boto3.Session(
        aws_access_key_id=os.environ.get("ACCESS_KEY"),
        aws_secret_access_key=os.environ.get("SECRET_KEY"),
    )
    return boto3.client("cognito-idp")


def get_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    return logger


def get_session():
    engine = create_db_engine()
    return create_db_session(engine)


def get_user_details_service_instance():
    cognito = get_cognito_resource()
    logger = get_logger()
    session = get_session()
    query_builder = QuerySQLBuilder()
    response_sql = ResponseSQL()
    response_user = ResponseUser()
    policy_manager = PolicyManager()
    return UserDetailsService(
        logger,
        cognito,
        response_user,
        policy_manager,
        session,
        query_builder,
        response_sql,
    )
