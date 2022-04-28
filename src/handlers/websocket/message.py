import os
import json
import boto3
from base_exception import AppError


def get_api_url(api_url):
    if api_url and "wss://" in api_url:
        return api_url.replace("wss://", "https://")
    return api_url


def get_connection_id(event):
    request_context = event.get("requestContext", {})
    if "connectionId" not in request_context:
        raise AppError("Connection id not found")

    return request_context["connectionId"]


def handler(event, _):
    try:
        api = get_api_url(os.environ.get("WEBSOCKET_API"))
        client = boto3.client("apigatewaymanagementapi", endpoint_url=api)
        connection_id = get_connection_id(event)

        body = json.dumps("Connect to websocket").encode("utf-8")

        client.post_to_connection(ConnectionId=connection_id, Data=body)

        return {"statusCode": 200, "body": json.dumps({"send": True})}
    except Exception as error:
        return {"statusCode": 400, "error": str(error)}
