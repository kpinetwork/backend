import json
import logging

from base_exception import AppError
from tags_repository import TagsRepository
from tags_service import TagsService
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL
from app_http_headers import AppHttpHeaders
from connection import create_db_engine, create_db_session
from verify_user_permissions import verify_user_access, get_user_id_from_event

headers = AppHttpHeaders("application/json", "OPTIONS,PUT")
engine = create_db_engine()
session = create_db_session(engine)
query_builder = QuerySQLBuilder()
response_sql = ResponseSQL()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_body(event: dict) -> dict:
    try:
        return json.loads(event.get("body"))
    except Exception as error:
        logger.info(error)
        raise AppError("Invalid body")


def get_tags_service():
    repository = TagsRepository(session, query_builder, response_sql, logger)
    return TagsService(logger, repository)


def handler(event, _):
    try:
        tags_service = get_tags_service()
        user_id = get_user_id_from_event(event)
        access = verify_user_access(user_id)

        if not access:
            raise AppError("No permissions to delete tags")

        tags = get_body(event)

        deleted = tags_service.delete_tags(tags)

        return {
            "statusCode": 200,
            "body": json.dumps({"deleted": deleted}),
            "headers": headers.get_headers(),
        }

    except Exception as error:
        logger.error(error)
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": headers.get_headers(),
        }
