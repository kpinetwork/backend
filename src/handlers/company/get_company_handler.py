import json
from company_service import CompanyService
from connection import create_db_engine, create_db_session
from query_builder import QuerySQLBuilder

engine = create_db_engine()
session = create_db_session(engine)
query_builder = QuerySQLBuilder()
company_service = CompanyService(session, query_builder)


def handler(event, context):
    try:
        id = event.get("pathParameters").get("id")
        company = company_service.get_company(id)

        return {
            "statusCode": 200,
            "body": json.dumps(company, default=str),
            "headers": {"Content-Type": "application/json"},
        }

    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": {"Content-Type": "application/json"},
        }
