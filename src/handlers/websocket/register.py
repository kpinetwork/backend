import json
import logging
from base_exception import AppError
from connection import create_db_engine, create_db_session
from connection_service import WebsocketConnectionService


engine = create_db_engine()
session = create_db_session(engine)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_websocket_connection_service():
    return WebsocketConnectionService(session, logger)


def get_connection_id(event):
    request_context = event.get("requestContext", {})
    if "connectionId" not in request_context:
        raise AppError("Connection id not found")

    return request_context["connectionId"]


def get_username_and_filename(body: str) -> tuple:
    try:
        data = json.loads(body)
        user = data.get("user")
        file = data.get("file")
        if user and file:
            return (user, file)
        raise AppError("You must provide a valid user id and filename")
    except Exception as error:
        logger.info(error)
        raise error


def handler(event, context):
    try:
        service = WebsocketConnectionService(session, logger)
        connection_id = get_connection_id(event)

        username, filename = get_username_and_filename(event.get("body"))
        is_registered = service.register_connection(connection_id, username, filename)

        body = json.dumps({"registered": is_registered})

        return {"statusCode": 200, "body": body}

    except Exception as error:
        logger.info(error)
        return {"statusCode": 400}
