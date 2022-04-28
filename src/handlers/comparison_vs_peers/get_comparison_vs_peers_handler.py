import json
from get_peers_data import get_comparison_vs_peers


def handler(event, _):
    try:
        comparison_peers = get_comparison_vs_peers(event)

        return {
            "statusCode": 200,
            "body": json.dumps(comparison_peers),
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
