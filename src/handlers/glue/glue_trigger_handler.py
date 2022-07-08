import json
import logging
import boto3
from glue_service import GlueService

client = boto3.client("glue")
logger = logging.getLogger()
logger.setLevel(logging.INFO)
glue_service = GlueService(logger)


def handler(event, _):
    return {
        "statusCode": 200,
        "body": json.dumps(glue_service.trigger(client, event, logger)),
        "headers": {"Content-Type": "application/json"},
    }
