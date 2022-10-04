import json
import logging
from connection import create_db_engine, create_db_session
from commons_functions import get_condition_params, get_list_param
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL
from company_anonymization import CompanyAnonymization
from investment_date_report import InvestmentDateReport
from by_metric_report import ByMetricReport
from investment_date_repository import InvestmentDateReportRepository
from metric_report_repository import MetricReportRepository
from calculator_service import CalculatorService
from profile_range import ProfileRange
from verify_user_permissions import (
    verify_user_access,
    get_user_id_from_event,
    get_username_from_user_id,
)
from get_user_details_service import get_user_details_service_instance
from app_http_headers import AppHttpHeaders


headers = AppHttpHeaders("application/json", "OPTIONS,GET")
engine = create_db_engine()
session = create_db_session(engine)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_investment_date_report_service():
    user_service = get_user_details_service_instance()
    company_anonymization = CompanyAnonymization(user_service)
    calculator = CalculatorService(logger)
    repository = InvestmentDateReportRepository(
        session, QuerySQLBuilder(), ResponseSQL(), logger
    )
    metric_repository = MetricReportRepository(
        session, QuerySQLBuilder(), ResponseSQL(), logger
    )
    profile_range = ProfileRange(session, QuerySQLBuilder(), logger, ResponseSQL())
    metric_report = ByMetricReport(
        logger, calculator, metric_repository, profile_range, company_anonymization
    )

    return InvestmentDateReport(
        logger,
        calculator,
        repository,
        metric_repository,
        metric_report,
        profile_range,
        company_anonymization,
    )


def get_metrics(param_metrics) -> str:
    if param_metrics != "" and param_metrics:
        return param_metrics
    return "growth,ebitda_margin"


def handler(event, _):
    try:
        report_service = get_investment_date_report_service()
        user_id = get_user_id_from_event(event)
        access = verify_user_access(user_id)
        company_id = None
        from_main = False
        conditions = dict()
        metrics = []
        if event.get("queryStringParameters"):
            params = event.get("queryStringParameters")
            params.pop("tag", None)
            conditions = get_condition_params(params)
            company_id = event.get("queryStringParameters").get("company_id")
            from_main = params.get("from_main", from_main)
            metrics = get_list_param(get_metrics(params.get("metrics")))

        username = get_username_from_user_id(user_id)
        report = report_service.get_peers_by_investment_date_report(
            company_id, username, metrics, from_main, access, **conditions
        )
        return {
            "statusCode": 200,
            "body": json.dumps(report),
            "headers": headers.get_headers(),
        }

    except Exception as error:

        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}),
            "headers": headers.get_headers(),
        }
