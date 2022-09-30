import json
from get_peers_data import get_comparison_vs_peers
from app_http_headers import AppHttpHeaders

headers = AppHttpHeaders("application/json", "OPTIONS,GET")


def handler(event, _):
    try:
        comparison_peers = get_comparison_vs_peers(event)

        return {
            "statusCode": 200,
            "body": json.dumps(comparison_peers),
            "headers": headers.get_headers(),
        }

    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": headers.get_headers(),
        }
