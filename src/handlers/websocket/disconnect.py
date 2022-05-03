import json
import logging
from base_exception import AppError
from connection import create_db_engine, create_db_session
from connection_service import WebsocketConnectionService


engine = create_db_engine()
session = create_db_session(engine)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_connection_id(event):
    request_context = event.get("requestContext", {})
    if "connectionId" not in request_context:
        raise AppError("Connection id not found")

    return request_context["connectionId"]


def handler(event, context):
    try:
        connection_id = get_connection_id(event)

        service = WebsocketConnectionService(session, logger)
        service.remove_connection(connection_id)

        return {"statusCode": 200, "body": json.dumps({"send": True})}
    except Exception as error:
        logger.info(error)
        return {"statusCode": 400, "error": str(error)}
