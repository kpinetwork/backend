import json


def handler(event, context):
    try:
        return {"statusCode": 200, "body": json.dumps({"connected": True})}

    except Exception as error:
        return {"statusCode": 400, "body": json.dumps({"error": str(error)})}
