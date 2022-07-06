import json
import logging
from connection import create_db_engine, create_db_session
from commons_functions import get_condition_params
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL
from company_anonymization import CompanyAnonymization
from comparison_vs_peers_service import ComparisonvsPeersService
from dynamic_report import DynamicReport
from by_metric_report import ByMetricReport
from metric_report_repository import MetricReportRepository
from investment_repository import InvestmentRepository
from investment_year_report import InvestmentYearReport
from calculator_service import CalculatorService
from calculator_report import CalculatorReport
from calculator_repository import CalculatorRepository
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


def get_metric_report_service(calculator, profile_range, company_anonymization):
    metric_report_repository = MetricReportRepository(
        session, QuerySQLBuilder(), ResponseSQL(), logger
    )

    return ByMetricReport(
        logger,
        calculator,
        metric_report_repository,
        profile_range,
        company_anonymization,
    )


def get_investment_year_report_service(report):
    repository = InvestmentRepository(session, QuerySQLBuilder(), ResponseSQL(), logger)

    return InvestmentYearReport(logger, report, repository)


def get_calendar_year_report_service(report):
    repository = CalculatorRepository(session, QuerySQLBuilder(), ResponseSQL(), logger)

    return ComparisonvsPeersService(logger, report, repository)


def get_dynamic_report_service():
    user_service = get_user_details_service_instance()
    company_anonymization = CompanyAnonymization(user_service)
    calculator = CalculatorService(logger)
    profile_range = ProfileRange(session, QuerySQLBuilder(), logger, ResponseSQL())
    report = CalculatorReport(logger, calculator, profile_range, company_anonymization)

    metric_report = get_metric_report_service(
        calculator, profile_range, company_anonymization
    )
    investment_report = get_investment_year_report_service(report)
    calendar_report = get_calendar_year_report_service(report)

    return DynamicReport(logger, metric_report, investment_report, calendar_report)


def get_value(params, value, default_value):
    return int(params.get(value, default_value)) if params.get(value) else None


def get_header() -> dict:
    return {
        "Content-Type": "application/json",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
    }


def handler(event, _):
    try:
        report_service = get_dynamic_report_service()
        user_id = get_user_id_from_event(event)
        access = verify_user_access(user_id)
        company_id = event.get("pathParameters").get("company_id")
        metric = None
        calendar_year = None
        investment_year = None
        from_main = False
        conditions = dict()

        if event.get("queryStringParameters"):
            params = event.get("queryStringParameters")
            conditions = get_condition_params(params)
            from_main = params.get("from_main", from_main)
            metric = params.get("metric", metric)
            calendar_year = get_value(params, "calendar_year", calendar_year)
            investment_year = get_value(params, "investment_year", investment_year)
            username = get_username_from_user_id(user_id)

            report = report_service.get_dynamic_report(
                company_id,
                username,
                metric,
                calendar_year,
                investment_year,
                from_main,
                access,
                **conditions
            )
        return {
            "statusCode": 200,
            "body": json.dumps(report),
            "headers": get_header(),
        }

    except Exception as error:

        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": get_header(),
        }
