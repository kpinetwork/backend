import json
import logging

from base_exception import AppError
from tags_service import TagsService
from tags_repository import TagsRepository
from connection import create_db_engine, create_db_session
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL
from verify_user_permissions import verify_user_access, get_user_id_from_event
from app_http_headers import AppHttpHeaders

headers = AppHttpHeaders("application/json", "OPTIONS,GET")
engine = create_db_engine()
session = create_db_session(engine)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_tag_service():
    query_builder = QuerySQLBuilder()
    response_sql = ResponseSQL()
    repository = TagsRepository(session, query_builder, response_sql, logger)
    return TagsService(logger, repository)


def handler(event, _):
    try:
        tags_service = get_tag_service()
        user_id = get_user_id_from_event(event)
        access = verify_user_access(user_id)

        if not access:
            raise AppError("No permissions to load tags")

        if not event.get("pathParameters").get("id", None):
            raise AppError("No data provided")

        company_id = event.get("pathParameters").get("id")
        tags = tags_service.get_tags_by_company(company_id)

        return {
            "statusCode": 200,
            "body": json.dumps(tags),
            "headers": headers.get_headers(),
        }

    except Exception as error:
        logger.error(error)
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": headers.get_headers(),
        }
