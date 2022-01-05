import json
import os
import boto3


def handler(event, context):
    try:
        session = boto3.Session(
            aws_access_key_id=os.environ.get("ACCESS_KEY"),
            aws_secret_access_key=os.environ.get("SECRET_KEY"),
        )

        client = boto3.client("cognito-idp")

        username = event["userName"]
        poolId = event["userPoolId"]
        group = "customer"

        client.admin_add_user_to_group(
            UserPoolId=poolId, Username=username, GroupName=group
        )

        return event

    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": {"Content-Type": "application/json"},
        }
