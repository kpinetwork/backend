import json
import logging
import datetime
from universe_overview_service import UniverseOverviewService
from commons_functions import get_list_param
from connection import create_db_engine, create_db_session
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL
from company_anonymization import CompanyAnonymization
from verify_user_permissions import (
    verify_user_access,
    get_user_id_from_event,
    get_username_from_user_id,
)
from get_user_details_service import get_user_details_service

engine = create_db_engine()
session = create_db_session(engine)
query_builder = QuerySQLBuilder()
response_sql = ResponseSQL()
user_service = get_user_details_service()
company_anonymization = CompanyAnonymization(user_service)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
overview_service = UniverseOverviewService(
    session, query_builder, logger, response_sql, company_anonymization
)


def handler(event, context):
    try:
        user_id = get_user_id_from_event(event)
        access = verify_user_access(user_id)
        sectors = []
        verticals = []
        investor_profile = []
        growth_profile = []
        size = []
        year = datetime.datetime.today().year
        if event.get("queryStringParameters"):
            params = event.get("queryStringParameters")
            sectors = get_list_param(params.get("sector"))
            verticals = get_list_param(params.get("vertical"))
            investor_profile = get_list_param(params.get("investor_profile"))
            growth_profile = get_list_param(params.get("growth_profile"))
            size = get_list_param(params.get("size"))
            year = params.get("year", year)

        username = get_username_from_user_id(user_id)
        company_anonymization.set_company_permissions(username)
        overview = overview_service.get_universe_overview(
            sectors, verticals, investor_profile, growth_profile, size, year, access
        )

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
