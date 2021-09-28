import json

from dbSample import DBSample

dbSample = DBSample()


def handler(event, context):
    return {
        "statusCode": 202,
        "body": json.dumps(dbSample.sample()),
        "headers": {"Content-Type": "application/json"},
    }
