from unittest import TestCase, mock
import logging
from unittest.mock import Mock
from src.utils.app_names import COMPARISON_METRICS
from src.service.investment_peers_report.investment_year_report import (
    InvestmentYearReport,
)
from src.service.calculator.calculator_service import CalculatorService
from src.service.calculator.calculator_report import CalculatorReport
from src.utils.company_anonymization import CompanyAnonymization
from src.service.dynamic_report.dynamic_report import DynamicReport

from src.service.by_metric_report.by_metric_report import ByMetricReport

from src.service.comparison_vs_peers.comparison_vs_peers_service import (
    ComparisonvsPeersService,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
size_range = {"label": "$30-<50 million", "max_value": 50, "min_value": 30}


class TestInvestmentYearReport(TestCase):
    def setUp(self):
        self.mock_session = Mock()
        self.mock_query_builder = Mock()
        self.mock_response_sql = Mock()
        self.mock_repository = Mock()
        self.company_anonymization = CompanyAnonymization(Mock())
        self.user_service = self.company_anonymization.user_details_service
        self.mock_profile_range = Mock()
        self.calculator = CalculatorService(logger)
        self.calculator_report = CalculatorReport(
            logger, self.calculator, self.mock_profile_range, self.company_anonymization
        )
        self.metric_report = ByMetricReport(
            logger,
            self.calculator,
            self.mock_repository,
            self.mock_profile_range,
            self.company_anonymization,
        )
        self.investment_report = InvestmentYearReport(
            logger, self.calculator_report, self.mock_repository
        )
        self.calendar_report = ComparisonvsPeersService(
            logger, self.calculator_report, self.mock_repository
        )
        self.mock_by_year_repository = Mock()
        self.report_instance = DynamicReport(
            logger,
            self.metric_report,
            self.investment_report,
            self.calendar_report,
            self.mock_by_year_repository,
            self.mock_profile_range,
        )
        self.company = {
            "id": "0123456",
            "name": "Company Test",
            "sector": "Computer Hardware",
            "vertical": "Life Sciences",
        }

        self.metrics = {
            "revenue": 40,
            "growth": 7,
            "ebitda_margin": -38,
            "revenue_vs_budget": 114,
            "ebitda_vs_budget": 125,
            "rule_of_40": -31,
            "gross_profit": -80,
            "gross_margin": -200,
            "sales_and_marketing": 125,
            "general_and_admin": 150,
            "research_and_development": 175,
        }

        self.scenarios = {
            "actuals_revenue": 40,
            "actuals_ebitda": -15,
            "prior_actuals_revenue": 37.5,
            "budget_revenue": 35,
            "budget_ebitda": -12,
            "actuals_cost_of_goods": 120,
            "actuals_sales_marketing": 50,
            "actuals_general_admin": 60,
            "actuals_research_development": 70,
        }

        self.range = {"label": "$30-<50 million", "max_value": 50, "min_value": 30}

    def mock_base_metric_results(self, response):
        attrs = {"proccess_base_metrics_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def test_get_base_metrics_should_return_dict_with_values(self):
        company = self.company.copy()
        company.update(self.scenarios.copy())
        self.mock_by_year_repository.get_base_metrics_options.return_value = [
            {"scenario": "Actuals", "metric": "Revenue", "alias": "actuals_revenue"}
        ]
        self.mock_by_year_repository.get_metric_by_scenario.return_value = []
        self.mock_by_year_repository.process_base_data.return_value = company

        metrics = self.report_instance.get_base_metrics(
            2020, self.company["id"], sector=[]
        )

        self.assertEqual(metrics, company)

    def test_remove_fields_should_change_dict(self):
        company = self.company.copy()
        company["prior_actuals_revenue"] = 13
        headers = ["id", "name"]

        self.report_instance.remove_fields(company, headers)

        self.assertEqual(company, {"id": "0123456", "name": "Company Test"})

    def test_replace_base_input_values_should_round_values(self):
        data = {"actuals_revenue": 123.45, "prior_actuals_revenue": 34}

        self.report_instance.replace_base_input_values(data, ["id", "actuals_revenue"])

        self.assertEqual(data, {"actuals_revenue": 123})

    def test_get_dynamic_ranges_should_return_ranges_dict(self):
        metrics = ["actuals_ebitda"]
        data = {"1": {"actuals_ebitda": 13}, "2": {"actuals_ebitda": 20}}
        expected_ranges = [
            {"label": "< 13 million", "min_value": None, "max_value": 30},
            {"label": "13 - 30 million", "min_value": 13, "max_value": 30},
            {"label": "30 million+", "min_value": 30, "max_value": None},
        ]
        self.mock_profile_range.build_ranges_from_values.return_value = expected_ranges

        dynamic_ranges = self.report_instance.get_dynamic_ranges(metrics, data)

        self.assertEqual(dynamic_ranges, {"actuals_ebitda": expected_ranges})

    def test_anonymize_company_should_change_revenue_value(self):
        metrics = ["actuals_revenue", "gross_profit"]
        profiles = {"revenue": self.range}
        ranges = {"gross_profit": [self.range]}
        company_data = {
            "actuals_revenue": 34,
            "id": "1234",
            "name": "Test company",
            "gross_profit": 30,
        }
        self.mock_profile_range.get_range_from_value.return_value = self.range["label"]

        self.report_instance.anonymize_company(metrics, ranges, profiles, company_data)

        self.assertEqual(
            company_data,
            {
                "actuals_revenue": self.range.get("label"),
                "id": "1234",
                "name": "1234-xxxx",
                "gross_profit": self.range.get("label"),
            },
        )

    def test_anonymize_company_should_change_growth_value(self):
        metrics = ["growth"]
        profiles = {"growth": self.range}
        company_data = {"growth": 34, "id": "1234", "name": "Test company"}
        self.mock_profile_range.get_range_from_value.return_value = self.range["label"]

        self.report_instance.anonymize_company(metrics, {}, profiles, company_data)

        self.assertEqual(
            company_data,
            {"growth": self.range.get("label"), "id": "1234", "name": "1234-xxxx"},
        )

    @mock.patch(
        "src.service.dynamic_report.dynamic_report.DynamicReport.anonymize_company"
    )
    def test_anonymize_data(self, mock_anonymize_company):
        metrics = ["gross_profit"]
        data = {"1": {"revenue": 34}}
        self.company_anonymization.companies = ["2"]
        self.mock_profile_range.get_profile_ranges.return_value = [self.range]

        self.report_instance.anonymize_data(metrics, data, False)

        mock_anonymize_company.assert_called()

    def test_add_metrics(self):
        metrics = ["gross_profit", "id", "name"]
        data = {
            "1": {
                "revenue": 34,
                "name": "Test Company",
                "sector": "Something",
                "prior_actuals_revenue": 34,
            }
        }

        self.report_instance.add_metrics(data, metrics)

        self.assertEqual(data, {"1": {"name": "Test Company", "gross_profit": "NA"}})

    @mock.patch("src.service.dynamic_report.dynamic_report.DynamicReport.add_metrics")
    @mock.patch(
        "src.service.dynamic_report.dynamic_report.DynamicReport.anonymize_data"
    )
    def test_get_year_report_should_return_data(
        self, mock_anonymize_data, mock_add_metrics
    ):
        metrics = ["gross_profit", "id", "name"]
        data = {
            "1": {
                "name": "Test Company",
                "sector": "Something",
                "prior_actuals_revenue": 34,
                "gross_profit": 34,
            }
        }
        self.company_anonymization.companies = ["1"]
        self.user_service.get_user_company_permissions.return_value = [{"id": "1"}]

        peers = self.report_instance.get_year_report(
            "1",
            "user@test.com",
            data,
            False,
            True,
            metrics,
            sector=["Computer Hardware"],
        )

        mock_anonymize_data.assert_called()
        mock_add_metrics.assert_called()
        self.assertEqual(
            peers,
            {
                "headers": ["id", "name", "gross_profit", "id", "name"],
                "company_comparison_data": {
                    "name": "Test Company",
                    "sector": "Something",
                    "prior_actuals_revenue": 34,
                    "gross_profit": 34,
                },
                "peers_comparison_data": [],
            },
        )

    def test_get_year_report_without_metrics_should_return_empty_dict(self):
        self.user_service.get_user_company_permissions.return_value = [{"id": "1"}]
        headers = ["id", "name"]
        headers.extend(COMPARISON_METRICS)

        peers = self.report_instance.get_year_report(
            "1", "user@test.com", {}, False, True, []
        )

        self.assertEqual(
            peers,
            {
                "headers": headers,
                "company_comparison_data": {},
                "peers_comparison_data": [],
            },
        )

    def test_get_year_report_should_raise_exception(self):
        self.user_service.get_user_company_permissions.side_effect = Exception("error")
        headers = ["id", "name"]
        headers.extend(COMPARISON_METRICS)

        with self.assertRaises(Exception) as context:
            self.report_instance.get_year_report(
                "1", "user@test.com", {}, False, True, []
            )

        self.assertEqual(str(context.exception), "error")

    @mock.patch(
        "src.service.dynamic_report.dynamic_report.DynamicReport.get_year_report"
    )
    @mock.patch(
        "src.service.dynamic_report.dynamic_report.DynamicReport.get_base_metrics"
    )
    def test_get_dynamic_report_with_calendar_year(
        self, mock_get_base_metrics, mock_get_year_report
    ):
        expected_peers = {
            "headers": ["id", "name", "actuals_revenue"],
            "company_comparison_data": {},
            "peers_comparison_data": [
                {"id": "1", "name": "Test company", "actuals_revenue": 34}
            ],
        }
        mock_get_year_report.return_value = expected_peers

        report = self.report_instance.get_dynamic_report(
            "1", "user@test.com", ["actuals_revenue"], 2020, None, True, True
        )

        self.assertEqual(report, expected_peers)
        mock_get_base_metrics.assert_called()
        mock_get_year_report.assert_called()

    @mock.patch(
        "src.service.dynamic_report.dynamic_report.DynamicReport.get_year_report"
    )
    def test_get_dynamic_report_with_investment_year(self, mock_get_year_report):
        expected_peers = {
            "headers": ["id", "name", "actuals_revenue"],
            "company_comparison_data": {},
            "peers_comparison_data": [
                {"id": "1", "name": "Test company", "actuals_revenue": 34}
            ],
        }
        mock_get_year_report.return_value = expected_peers

        report = self.report_instance.get_dynamic_report(
            "1", "user@test.com", ["actuals_revenue"], None, 1, True, True
        )

        self.assertEqual(report, expected_peers)
        mock_get_year_report.assert_called()

    def test_get_dynamic_report_without_year(self):
        expected_peers = {
            "headers": [],
            "company_comparison_data": {},
            "peers_comparison_data": [],
        }

        report = self.report_instance.get_dynamic_report(
            "1", "user@test.com", ["actuals_revenue"], None, None, True, True
        )

        self.assertEqual(report, expected_peers)

    @mock.patch(
        "src.service.dynamic_report.dynamic_report.DynamicReport.get_dynamic_calendar_year_report"
    )
    def test_get_dynamic_report_should_raise_error_when_report_fails(
        self, mock_get_dynamic_calendar_year_report
    ):
        mock_get_dynamic_calendar_year_report.side_effect = Exception("error")

        with self.assertRaises(Exception) as context:
            self.report_instance.get_dynamic_report(
                "1", "user@test.com", ["actuals_revenue"], 2020, None, True, True
            )

        self.assertEqual(str(context.exception), "error")
