import json
import os
import boto3


def handler(event, context):
    try:
        cognito = boto3.client(
            "cognito-idp",
            region_name=os.environ.get("REGION"),
            aws_access_key_id=os.environ.get("ACCESS_KEY"),
            aws_secret_access_key=os.environ.get("SECRET_KEY"),
        )

        poolId = os.environ.get("USER_POOL_ID")
        users = get_users(cognito, poolId)
        mapped_users = [
            {"username": user["Username"], "email": user["Attributes"][0]["Value"]}
            for user in users
        ]

        for user in mapped_users:
            groups = cognito.admin_list_groups_for_user(
                Username=user["username"], UserPoolId=poolId
            )
            filter_groups = [
                group["GroupName"]
                for group in groups["Groups"]
                if "Google" not in group["GroupName"]
            ]
            user.update({"roles": filter_groups})

        return {
            "statusCode": 200,
            "body": json.dumps(mapped_users, default=str),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
        }

    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": {"Content-Type": "application/json"},
        }


def get_users(client, pool_id):
    users = []
    next_page = None
    kwargs = {"UserPoolId": pool_id, "AttributesToGet": ["email"]}

    users_remain = True
    while users_remain:
        if next_page:
            kwargs["PaginationToken"] = next_page
        response = client.list_users(**kwargs)
        users.extend(response["Users"])
        next_page = response.get("PaginationToken", None)
        users_remain = next_page is not None

    return users
