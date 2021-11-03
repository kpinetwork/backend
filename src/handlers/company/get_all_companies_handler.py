import json
from company_service import CompanyService
from connection import create_db_engine, create_db_session
from query_sql import QuerySQL

engine = create_db_engine()
session = create_db_session(engine)
query_sql = QuerySQL()
company_service = CompanyService(session, query_sql)


def handler(event, context):
    try:
        offset = 0
        max_count = 20

        if event.get("queryStringParameters"):
            params = event.get("queryStringParameters")
            offset = params.get("offset", offset)
            max_count = params.get("limit", max_count)

        companies = company_service.get_all_companies(offset, max_count)

        return {
            "statusCode": 200,
            "body": json.dumps(companies, default=str),
            "headers": {"Content-Type": "application/json"},
        }

    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": {"Content-Type": "application/json"},
        }
