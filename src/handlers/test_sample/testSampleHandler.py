import json

from helloWorld import HelloWorld

hello_world = HelloWorld()


def handler(event, context):
    return {
        "statusCode": 202,
        "body": json.dumps(hello_world.sample()),
        "headers": {"Content-Type": "application/json"},
    }
