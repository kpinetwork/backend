import json
import logging

from base_exception import AppError
from ranges_service import RangesService
from ranges_repository import RangesRepository
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL
from app_http_headers import AppHttpHeaders
from connection import create_db_engine, create_db_session
from verify_user_permissions import verify_user_access, get_user_id_from_event

headers = AppHttpHeaders("application/json", "OPTIONS,PUT")
engine = create_db_engine()
session = create_db_session(engine)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_body(event: dict) -> dict:
    try:
        return json.loads(event.get("body"))
    except Exception as error:
        logger.info(error)
        raise AppError("Invalid body")


def get_ranges_service():
    query_builder = QuerySQLBuilder()
    response_sql = ResponseSQL()
    repository = RangesRepository(session, query_builder, response_sql, logger)
    return RangesService(logger, repository)


def handler(event, _):
    try:
        ranges_service = get_ranges_service()
        user_id = get_user_id_from_event(event)
        access = verify_user_access(user_id)

        if not access:
            raise AppError("No permissions to modify ranges")

        body = get_body(event)

        updated = ranges_service.modify_ranges(body)

        return {
            "statusCode": 200,
            "body": json.dumps({"updated": updated}, default=str),
            "headers": headers.get_headers(),
        }

    except Exception as error:
        logger.error(error)
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": headers.get_headers(),
        }
