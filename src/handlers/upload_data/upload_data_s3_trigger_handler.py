import os
import json
import boto3
from base_exception import AppError


def handler(event, context):
    try:
        if not event.get("body"):
            raise AppError("No data provided")

        bucket_files = "kpinetwork-test"
        # bucket_files = os.environ.get("BUCKET_FILES")
        body = json.loads(event.get("body"))
        upload_file(bucket_files, body)

        return {
            "statusCode": 200,
            "body": json.dumps({"uploaded": True}),
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
            "headers": {
                "Content-Type": "application/json",
            },
        }


def upload_file(bucket_name: str, file_info: dict) -> None:
    filename = file_info.get("fileName")
    file = file_info.get("file")

    if not file or not filename:
        raise AppError("No file provided")
    if not filename.endswith((".csv")):
        raise AppError("Extension not allowed")

    boto3.Session(
        aws_access_key_id=os.environ.get("ACCESS_KEY"),
        aws_secret_access_key=os.environ.get("SECRET_KEY"),
    )
    s3_client = boto3.client("s3")
    s3_client.put_object(
        Bucket=bucket_name, Key=f"{os.environ.get('ENV')}/{filename}", Body=file
    )
