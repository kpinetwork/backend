import json
import logging
from scenario_service import ScenarioService
from metric_type_service import MetricTypesService
from connection import create_db_engine, create_db_session
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL
from verify_user_permissions import verify_user_access, get_user_id_from_event
from base_exception import AppError
from app_http_headers import AppHttpHeaders

headers = AppHttpHeaders("application/json", "OPTIONS,POST")
engine = create_db_engine()
session = create_db_session(engine)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_body(event: dict) -> dict:
    try:
        return json.loads(event.get("body"))
    except Exception as error:
        logger.info(error)
        raise AppError("Invalid body")


def get_arguments(event: dict) -> dict:
    body = get_body(event)
    args = ["scenario", "year", "metric", "value"]
    return {field: body[field] for field in body if field in args}


def get_service() -> object:
    metric_service = MetricTypesService(
        session, QuerySQLBuilder(), ResponseSQL(), logger
    )
    return ScenarioService(session, QuerySQLBuilder(), metric_service, logger)


def handler(event, _):
    try:
        service = get_service()
        user_id = get_user_id_from_event(event)
        access = verify_user_access(user_id)

        if not access:
            raise AppError("No permissions to add scenarios")

        company_id = event.get("pathParameters").get("id")
        args = get_arguments(event)
        scenario = service.add_company_scenario(company_id=company_id, **args)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {"company_id": company_id, "scenario": scenario, "added": True}
            ),
            "headers": headers.get_headers(),
        }

    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": headers.get_headers(),
        }
