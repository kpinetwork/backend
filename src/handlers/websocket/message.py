import os
import json
import boto3
import logging
from base_exception import AppError
from connection import create_db_engine, create_db_session
from connection_service import WebsocketConnectionService


engine = create_db_engine()
session = create_db_session(engine)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_api_url(api_url):
    if api_url and "wss://" in api_url:
        return api_url.replace("wss://", "https://")
    return api_url


def get_connection_id(event):
    request_context = event.get("requestContext", {})
    if "connectionId" not in request_context:
        raise AppError("Connection id not found")

    return request_context["connectionId"]


def get_file_name(file: str) -> str:
    file_name = file.split(":")[1]
    return "{name}.csv".format(name=file_name)


def send_message(client, connection_id: str, file: str):
    file = get_file_name(file)
    message = f"Your file {file} was proccessed!"
    body = json.dumps(message, default=str).encode("utf-8")
    client.post_to_connection(ConnectionId=connection_id, Data=body)


def remove_connection(connection_id: str):
    service = WebsocketConnectionService(session, logger)
    service.remove_connection(connection_id)


def handler(event, context):
    try:
        api = get_api_url(os.environ.get("WEBSOCKET_API"))
        client = boto3.client("apigatewaymanagementapi", endpoint_url=api)

        connection_id = get_connection_id(event)
        data = json.loads(event.get("body"))

        send_message(client, connection_id, data.get("file"))

        remove_connection(connection_id)

        return {"statusCode": 200, "body": json.dumps({"send": True})}
    except Exception as error:
        logger.info(error)
        return {"statusCode": 400, "error": str(error)}
