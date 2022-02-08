import json
import logging
from src.service.company.company_service import CompanyService
from db.utils.connection import create_db_engine, create_db_session
from src.utils.query_builder import QuerySQLBuilder
from src.utils.response_sql import ResponseSQL

engine = create_db_engine()
session = create_db_session(engine)
query_builder = QuerySQLBuilder()
response_sql = ResponseSQL()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
company_service = CompanyService(session, query_builder, logger, response_sql)


def handler(event):
    try:
        companies_data = {
            "608d243a-c53b-44f7-9334-daca80f75846": True, 
            "edb99ce5-654d-49b4-b777-541d35fc8cd3": True,
            "510d7c0e-6541-4fc6-a3a0-35a303ff2221": False,
            "34ba631e-7190-4906-8b2b-31ac849b2a5b": False
        }

        if event.get("body"):
            companies_data = json.loads(event.get("body")["companies"])

        make_data_public = company_service.make_data_public(
            companies_data
        )

        return {
            "statusCode": 200,
            "body": json.dumps(make_data_public, default=str),
            "headers": {"Content-Type": "application/json"},
        }

    except Exception as error:
        print("in handler error")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": {"Content-Type": "application/json"},
        }

print(handler({}))
