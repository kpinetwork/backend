import os
import boto3


def handler(event, context):

    boto3.Session(
        aws_access_key_id=os.environ.get("ACCESS_KEY"),
        aws_secret_access_key=os.environ.get("SECRET_KEY"),
    )

    cognito = boto3.client("cognito-idp")

    if event["request"]["userAttributes"]["email"]:
        email = event["request"]["userAttributes"]["email"]
        params = {
            "UserPoolId": event["userPoolId"],
            "Filter": 'email = "' + email + '"',
            "AttributesToGet": ["email"],
        }

        result = cognito.list_users(**params)
        print("results", result)
        print("results[users]", result["Users"])
        if (
            len(result["Users"]) > 0
            and result["Users"][0]["Username"] != event["userName"]
        ):
            raise Exception("A user with the same email address exists")
        else:
            return event
