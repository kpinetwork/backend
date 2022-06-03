import json
import logging
from update_data_service import UpdateDataService
from connection import create_db_engine, create_db_session
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL
from base_exception import AppError

engine = create_db_engine()
session = create_db_session(engine)
query_builder = QuerySQLBuilder()
response_sql = ResponseSQL()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
update_data_service = UpdateDataService(session, query_builder, logger, response_sql)


def handler(event, _):
    try:

        if not event.get("body"):
            raise AppError("No data provided")

        data = json.loads(event.get("body"))
        companies = data.get("companies", [])
        metrics = data.get("metrics", [])

        if len(companies) == 0 and len(metrics) == 0:
            raise AppError("No data provided")

        update_data_service.update_data(companies, metrics)

        return {"statusCode": 200, "body": json.dumps({"updated": True})}

    except Exception as error:
        logger.info(error)
        return {"statusCode": 400, "body": json.dumps({"error": str(error)})}
