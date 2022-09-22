import json
import logging
import datetime
from commons_functions import get_condition_params
from connection import create_db_engine, create_db_session
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL
from calculator_service import CalculatorService
from profile_range import ProfileRange
from universe_overview_service import UniverseOverviewService
from base_metrics_repository import BaseMetricsRepository

engine = create_db_engine()
session = create_db_session(engine)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_overview_instance():
    calculator = CalculatorService(logger)
    repository = BaseMetricsRepository(
        logger, session, QuerySQLBuilder(), ResponseSQL()
    )
    profile_range = ProfileRange(session, QuerySQLBuilder(), logger, ResponseSQL())

    return UniverseOverviewService(logger, calculator, repository, profile_range)


def handler(event, _):
    try:
        overview_service = get_overview_instance()
        year = datetime.datetime.today().year
        conditions = dict()
        if event.get("queryStringParameters"):
            params = event.get("queryStringParameters")
            conditions = get_condition_params(params)
            year = int(params.get("year", year))

        overview = overview_service.get_universe_overview(year, **conditions)

        return {
            "statusCode": 200,
            "body": json.dumps(overview, default=str),
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
