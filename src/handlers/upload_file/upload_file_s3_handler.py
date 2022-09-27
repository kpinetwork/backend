import os
import json
import boto3
import logging
import datetime
from base_exception import AppError
from app_http_headers import AppHttpHeaders

headers = AppHttpHeaders("application/json", "OPTIONS,POST")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_s3_client():
    boto3.Session(
        aws_access_key_id=os.environ.get("ACCESS_KEY"),
        aws_secret_access_key=os.environ.get("SECRET_KEY"),
    )
    return boto3.client("s3")


def get_user_id(event):
    try:
        return event["requestContext"]["authorizer"]["principalId"]
    except Exception as error:
        logger.info(error)
        return ""


def verify_valid_data(file, filename) -> None:
    if not file or not filename:
        raise AppError("No file provided")

    if not filename.endswith((".csv")):
        raise AppError("Extension not allowed")


def get_file_name(file_name: str) -> str:
    return file_name.split(".csv")[0]


def get_valid_file_name(user_id: str, filename: str) -> str:
    now = datetime.datetime.utcnow()
    file_name = get_file_name(filename)
    return "{name}:{user}:{date}.csv".format(
        name=file_name, user=user_id, date=now.strftime("%m_%d_%y_%H_%M_%S")
    )


def upload_file(bucket_name: str, file_info: dict, user_id: str) -> str:
    file = file_info.get("file")
    file_name = file_info.get("fileName")
    env = os.environ.get("ENV")

    verify_valid_data(file, file_name)
    s3_client = get_s3_client()
    filename = get_valid_file_name(user_id, file_name)

    s3_client.put_object(Bucket=bucket_name, Key=f"{env}/{filename}", Body=file)

    return filename


def handler(event, _):
    try:
        if not event.get("body"):
            raise AppError("No data provided")

        bucket_files = os.environ.get("BUCKET_FILES")
        body = json.loads(event.get("body"))
        user_id = get_user_id(event)
        filename = upload_file(bucket_files, body, user_id)

        return {
            "statusCode": 200,
            "body": json.dumps({"uploaded": True, "filename": filename}),
            "headers": headers.get_headers(),
        }

    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": headers.get_headers(),
        }
