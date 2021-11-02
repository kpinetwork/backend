import json
import logging
import boto3
from glueService import GlueService

client = boto3.client("glue")
logger = logging.getLogger()
logger.setLevel(logging.INFO)
glueService = GlueService()


def handler(event, context):
    return {
        "statusCode": 202,
        "body": json.dumps(glueService.trigger(client, event, logger)),
        "headers": {"Content-Type": "application/json"},
    }
