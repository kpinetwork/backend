import json
import logging

from base_exception import AppError
from tags_repository import TagsRepository
from tags_service import TagsService
from connection import create_db_engine, create_db_session
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL
from verify_user_permissions import verify_user_access, get_user_id_from_event
from app_http_headers import AppHttpHeaders

headers = AppHttpHeaders("application/json", "OPTIONS,POST")
engine = create_db_engine()
session = create_db_session(engine)
query_builder = QuerySQLBuilder()
response_sql = ResponseSQL()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

tags_repository = TagsRepository(session, query_builder, response_sql, logger)
tags_service = TagsService(logger, tags_repository)


def handler(event, _):
    try:
        user_id = get_user_id_from_event(event)
        access = verify_user_access(user_id)

        if not access:
            raise AppError("No permissions to add tags")

        if not event.get("body"):
            raise AppError("No data provided")

        tag = json.loads(event.get("body"))
        response = tags_service.add_tag(tag)

        return {
            "statusCode": 201,
            "body": json.dumps(
                {
                    "tag": response,
                    "added": True,
                }
            ),
            "headers": headers.get_headers(),
        }

    except Exception as error:
        logger.error(error)
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": headers.get_headers(),
        }
