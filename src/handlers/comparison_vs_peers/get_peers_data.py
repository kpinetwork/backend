import logging
import datetime
from comparison_vs_peers_service import ComparisonvsPeersService
from commons_functions import get_condition_params
from connection import create_db_engine, create_db_session
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL
from company_anonymization import CompanyAnonymization
from calculator_repository import CalculatorRepository
from calculator_service import CalculatorService
from profile_range import ProfileRange
from verify_user_permissions import (
    verify_user_access,
    get_user_id_from_event,
    get_username_from_user_id,
)
from get_user_details_service import get_user_details_service_instance

engine = create_db_engine()
session = create_db_session(engine)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_comparison_vs_peers_service():
    user_service = get_user_details_service_instance()
    company_anonymization = CompanyAnonymization(user_service)
    calculator = CalculatorService(logger)
    repository = CalculatorRepository(session, QuerySQLBuilder(), ResponseSQL(), logger)
    profile_range = ProfileRange(session, QuerySQLBuilder(), logger, ResponseSQL())

    return ComparisonvsPeersService(
        logger, calculator, repository, profile_range, company_anonymization
    )


def get_comparison_vs_peers(event: dict) -> dict:
    comparison_vs_peers_service = get_comparison_vs_peers_service()
    user_id = get_user_id_from_event(event)
    access = verify_user_access(user_id)
    company_id = event.get("pathParameters").get("company_id")
    year = datetime.datetime.today().year
    conditions = dict()
    from_main = False

    if event.get("queryStringParameters"):
        params = event.get("queryStringParameters")
        conditions = get_condition_params(params)
        year = int(params.get("year", year))
        from_main = params.get("from_main", from_main)

    username = get_username_from_user_id(user_id)
    comparison_peers = comparison_vs_peers_service.get_peers_comparison(
        company_id, username, year, from_main, access, **conditions
    )

    return comparison_peers
