import json


def handler(_):
    try:
        return {"statusCode": 200, "body": json.dumps({"connected": False})}

    except Exception as error:
        return {"statusCode": 400, "body": json.dumps({"error": str(error)})}
