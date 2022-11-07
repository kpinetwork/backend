import json
import logging
from typing import Union

from base_exception import AppError
from ranges_service import RangesService
from ranges_repository import RangesRepository
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

ranges_repository = RangesRepository(session, query_builder, response_sql, logger)
ranges_service = RangesService(logger, ranges_repository)


def get_max_count(max_count: str) -> Union[int, None]:
    try:
        return int(max_count)
    except Exception:
        return None


def handler(event, _):
    try:
        user_id = get_user_id_from_event(event)
        access = verify_user_access(user_id)
        offset = 0
        max_count = None

        if not access:
            raise AppError("No permissions to load ranges")

        if event.get("queryStringParameters"):
            params = event.get("queryStringParameters")
            offset = int(params.get("offset", offset))
            max_count = get_max_count(params.get("limit"))

        ranges = ranges_service.get_all_ranges(offset, max_count)

        return {
            "statusCode": 200,
            "body": json.dumps(ranges),
            "headers": headers.get_headers(),
        }

    except Exception as error:
        logger.error(error)
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": headers.get_headers(),
        }
