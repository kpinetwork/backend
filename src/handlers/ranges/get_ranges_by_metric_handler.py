import json
import logging

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
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_ranges_service():
    ranges_repository = RangesRepository(
        session, QuerySQLBuilder(), ResponseSQL(), logger
    )
    return RangesService(logger, ranges_repository)


def handler(event, _):
    try:
        user_id = get_user_id_from_event(event)
        access = verify_user_access(user_id)

        if not access:
            raise AppError("No permissions to load ranges")
        if not event.get("pathParameters").get("metric", None):
            raise AppError("No metric provided")

        metric = event.get("pathParameters").get("metric")
        ranges_service = get_ranges_service()
        ranges = ranges_service.get_ranges_by_metric(metric)

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
