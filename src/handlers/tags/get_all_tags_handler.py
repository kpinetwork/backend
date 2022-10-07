import json
import logging

from tags_service import TagsService
from tags_repository import TagsRepository
from connection import create_db_engine, create_db_session
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL
from app_http_headers import AppHttpHeaders
from verify_user_permissions import (
    verify_user_access,
    get_user_id_from_event,
)

headers = AppHttpHeaders("application/json", "OPTIONS,GET")
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
        offset = 0
        max_count = None

        if event.get("queryStringParameters"):
            params = event.get("queryStringParameters")
            offset = int(params.get("offset", offset))
            max_count = int(params.get("limit", 20))

        tags = tags_service.get_all_tags(access, offset, max_count)

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
