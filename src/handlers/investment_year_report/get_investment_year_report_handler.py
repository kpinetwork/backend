import json
import logging
from investment_repository import InvestmentRepository
from investment_year_report import InvestmentYearReport
from commons_functions import get_condition_params
from connection import create_db_engine, create_db_session
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL
from company_anonymization import CompanyAnonymization
from calculator_service import CalculatorService
from calculator_report import CalculatorReport
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


def get_investment_year_report():
    user_service = get_user_details_service_instance()
    company_anonymization = CompanyAnonymization(user_service)
    calculator = CalculatorService(logger)
    repository = InvestmentRepository(session, QuerySQLBuilder(), ResponseSQL(), logger)
    profile_range = ProfileRange(session, QuerySQLBuilder(), logger, ResponseSQL())
    report = CalculatorReport(logger, calculator, profile_range, company_anonymization)

    return InvestmentYearReport(logger, report, repository)


def handler(event, _):
    try:
        investment_report_instance = get_investment_year_report()
        user_id = get_user_id_from_event(event)
        access = verify_user_access(user_id)
        company_id = event.get("pathParameters").get("company_id")
        invest_year = 0
        from_main = False
        conditions = dict()

        if event.get("queryStringParameters"):
            params = event.get("queryStringParameters")
            conditions = get_condition_params(params)
            from_main = params.get("from_main", from_main)
            invest_year = int(params.get("invest_year", invest_year))

        username = get_username_from_user_id(user_id)
        report = investment_report_instance.get_peers_by_investment_year(
            company_id, invest_year, username, from_main, access, **conditions
        )

        return {
            "statusCode": 200,
            "body": json.dumps(report),
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
