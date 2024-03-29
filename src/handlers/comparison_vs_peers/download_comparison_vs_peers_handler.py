import os
from io import TextIOWrapper
import json
import csv
from get_peers_data import get_comparison_vs_peers
from app_http_headers import AppHttpHeaders

headers = AppHttpHeaders("application/octet-stream", "OPTIONS,GET")

header = [
    "name",
    "sector",
    "vertical",
    "revenue",
    "growth",
    "ebitda_margin",
    "revenue_vs_budget",
    "ebitda_vs_budget",
    "rule_of_40",
    "gross_profit",
    "gross_margin",
    "sales_and_marketing",
    "general_and_admin",
    "research_and_development",
    "clv_cac_ratio",
    "cac_ratio",
    "opex_of_revenue",
    "revenue_per_employee",
    "gross_retention",
    "net_retention",
    "new_bookings_growth",
    "debt_ebitda",
]

file_path = os.environ.get("FILE_PATH")


def remove_keys(company: dict):
    company.pop("id", None)
    company.pop("size_cohort", None)
    company.pop("inves_profile_name", None)
    company.pop("margin_group", None)
    return company


def write_file(file: TextIOWrapper, data: dict):
    writer = csv.DictWriter(file, fieldnames=header)
    writer.writeheader()
    writer.writerows(data)
    file.seek(0)


def process_data(data: dict) -> list:
    peers = data.get("peers_comparison_data")
    company = data.get("company_comparison_data")

    peers_data = []
    remove_keys(company)
    if company:
        peers_data = [company]

    peers = list(map(remove_keys, peers))
    peers_data.extend(peers)

    return peers_data


def get_file_data(data: dict, file_path: str) -> str:
    peers = process_data(data)

    f = open(file_path, "w+")
    write_file(f, peers)
    file_data = f.read()
    f.close()

    return file_data


def handler(event, _):
    try:
        comparison_peers = get_comparison_vs_peers(event)

        file_data = get_file_data(comparison_peers, file_path)

        return {
            "statusCode": 200,
            "body": file_data,
            "isBase64Encoded": False,
            "headers": headers.get_headers(),
        }

    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": headers.get_headers(),
        }
