import json

from src.service.helloWorld import HelloWorld

hello_world = HelloWorld()


def lambda_handler(event, context):

    return {
        "statusCode": 200,
        "body": json.dumps(hello_world.hello_world()),
        "headers": {"Content-Type": "application/json"},
    }
