import os
import time
import logging
import requests
from jose import jwk, jwt
from jose.utils import base64url_decode

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_keys(region: str, user_pool_id: str) -> list:
    try:
        url = "https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json".format(
            region, user_pool_id
        )
        response = requests.get(url)
        keys = response.json()["keys"]
        return keys
    except Exception as error:
        logger.info(error)
        raise error


def get_public_key(keys: list, headers: dict):
    kid = headers.get("kid")
    key_index = -1
    for i in range(len(keys)):
        if kid == keys[i]["kid"]:
            key_index = i
            break
    if key_index == -1:
        raise Exception("Public key not found in jwks.json")

    return jwk.construct(keys[key_index])


def verify_token(token: str, public_key: object):
    message, encoded_signature = str(token).rsplit(".", 1)
    decoded_signature = base64url_decode(encoded_signature.encode("utf-8"))

    if not public_key.verify(message.encode("utf8"), decoded_signature):
        raise Exception("Invalid token")


def verify_token_expiration(claims: dict):
    if time.time() > claims["exp"]:
        raise Exception("Token is expired")


def verify_token_application(app_client_id: str, claims: dict):
    if claims["aud"] != app_client_id:
        raise Exception("Token was not issued for this audience")


def get_policy(permission: str, user: str) -> str:
    account_id = os.environ.get("AWS_ACCOUNT_ID")
    api_gateway = os.environ.get("API_GATEWAY")
    return {
        "principalId": user,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": permission,
                    "Action": "execute-api:Invoke",
                    "Resource": f"arn:aws:execute-api:us-west-2:{account_id}:{api_gateway}/*/*/*",
                },
            ],
        },
    }


def handler(event, context):
    try:
        region = os.environ.get("REGION")
        user_pool_id = os.environ.get("USER_POOL_ID")
        app_client_id = os.environ.get("APP_CLIENT_ID")

        keys = get_keys(region, user_pool_id)
        token = event.get("authorizationToken")
        if not token:
            raise Exception("No Token found")

        headers = jwt.get_unverified_headers(token)
        public_key = get_public_key(keys, headers)
        verify_token(token, public_key)

        claims = jwt.get_unverified_claims(token)
        verify_token_expiration(claims)
        verify_token_application(app_client_id, claims)

        user = claims.get("cognito:username") if claims.get("cognito:username") else ""

        return get_policy("Allow", user)

    except Exception as error:
        logger.info(error)
        return get_policy("Deny", "")
