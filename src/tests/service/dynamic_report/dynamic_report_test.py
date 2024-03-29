from unittest import TestCase
import logging
from unittest.mock import Mock, patch

from src.utils.app_names import COMPARISON_METRICS
from src.service.calculator.calculator_service import CalculatorService
from src.utils.company_anonymization import CompanyAnonymization
from src.service.dynamic_report.dynamic_report import DynamicReport
from src.service.by_metric_report.by_metric_report import ByMetricReport
from src.service.by_year_report.by_year_report_service import ByYearReportService
from src.service.base_metrics.base_metrics_report import BaseMetricsReport
from src.service.base_metrics.base_metrics_repository import BaseMetricsRepository
from src.utils.query_builder import QuerySQLBuilder

logger = logging.getLogger()
logger.setLevel(logging.INFO)
size_range = {"label": "$30-<50 million", "max_value": 50, "min_value": 30}


class TestDynamicReport(TestCase):
    def setUp(self):
        self.mock_session = Mock()
        self.mock_query_builder = QuerySQLBuilder()
        self.mock_response_sql = Mock()
        self.mock_repository = Mock()
        self.company_anonymization = CompanyAnonymization(Mock())
        self.user_service = self.company_anonymization.user_details_service
        self.mock_profile_range = Mock()
        self.calculator = CalculatorService(logger)
        self.base_metrics_report = BaseMetricsReport(
            logger, self.calculator, self.mock_profile_range, self.company_anonymization
        )
        self.base_metrics_repository = BaseMetricsRepository(
            logger, self.mock_session, self.mock_query_builder, self.mock_response_sql
        )
        self.metric_report = ByMetricReport(
            logger,
            self.calculator,
            self.mock_repository,
            self.mock_profile_range,
            self.company_anonymization,
        )
        self.calendar_report = ByYearReportService(
            logger,
            self.base_metrics_report,
            self.base_metrics_repository,
            self.mock_profile_range,
        )
        self.report_instance = DynamicReport(
            logger,
            self.metric_report,
            self.calendar_report,
            self.base_metrics_repository,
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
            "actuals_customer_lifetime_value": 0.4,
            "actuals_customer_acquition_costs": 3,
            "actuals_customer_annual_value": 9.7,
            "actuals_other_operating_expenses": 3,
            "actuals_headcount": 0.9,
            "actuals_run_rate_revenue": 3,
            "actuals_losses_and_downgrades": 4,
            "actuals_upsells": 6,
            "actuals_new_bookings": 4,
            "prior_actuals_new_bookings": 5,
            "prior_actuals_run_rate_revenue": 3,
        }

        self.range = {"label": "$30-<50 million", "max_value": 50, "min_value": 30}
        self.profile_ranges = {
            "revenue": [self.range],
            "growth": [self.range],
            "revenue_per_employee": [self.range],
        }

    def mock_base_metric_results(self, response):
        attrs = {"proccess_base_metrics_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    @patch.object(BaseMetricsRepository, "process_scenario_values")
    def test_get_base_metrics_should_return_dict_with_values(
        self, mock_process_scenario_values
    ):
        company = self.company.copy()
        company.update(self.scenarios.copy())
        mock_process_scenario_values.return_value = {self.company["id"]: company}

        metrics = self.report_instance.get_base_metrics(2020, sector=[])

        self.assertEqual(metrics, {self.company["id"]: company})

    def test_remove_fields_should_change_dict(self):
        company = self.company.copy()
        company["prior_actuals_revenue"] = 13
        headers = ["name"]

        self.report_instance.remove_fields(company, headers)

        self.assertEqual(company, {"id": "0123456", "name": "Company Test"})

    def test_replace_base_input_values_should_round_values(self):
        data = {"actuals_revenue": 123.45, "prior_actuals_revenue": 34}

        self.report_instance.replace_base_input_values(data, ["id", "actuals_revenue"])

        self.assertEqual(data, {"actuals_revenue": 123})

    def test_anonymize_company_should_anonymize_company_name_and_metrics(self):
        metrics = ["actuals_revenue", "gross_profit", "actuals_headcount"]
        profiles = {"revenue": self.range}
        company_data = {
            "actuals_revenue": 34,
            "id": "1234",
            "name": "Test company",
            "gross_profit": 30,
            "actuals_headcount": 2,
        }
        self.mock_profile_range.get_range_from_value.return_value = self.range["label"]

        self.report_instance.anonymize_company(
            metrics, ["revenue", "gross_profit"], profiles, company_data
        )

        self.assertEqual(
            company_data,
            {
                "actuals_revenue": self.range.get("label"),
                "id": "1234",
                "name": "1234-xxxx",
                "gross_profit": self.range.get("label"),
                "actuals_headcount": 2,
            },
        )

    @patch("src.service.dynamic_report.dynamic_report.DynamicReport.anonymize_company")
    def test_anonymize_data_if_company_is_not_allowed_should_anonymize_company(
        self, mock_anonymize_company
    ):
        metrics = ["gross_profit"]
        data = {"1": {"revenue": 34}}
        self.company_anonymization.companies = ["2"]
        self.mock_profile_range.get_profile_ranges.return_value = [self.range]

        self.report_instance.anonymize_data(metrics, data, self.profile_ranges)

        mock_anonymize_company.assert_called()

    def test_add_metrics_when_is_successful_should_overwrite_data_dict_with_metrics(
        self,
    ):
        metrics = ["gross_profit", "id", "name"]
        data = {
            "1": {
                "revenue": 34,
                "name": "Test Company",
                "sector": "Something",
                "prior_actuals_revenue": 34,
            }
        }
        expected_data = {
            "1": {
                "name": "Test Company",
                "gross_profit": "NA",
                "margin_group": "$30-<50 million",
                "size_cohort": "$30-<50 million",
            }
        }
        self.mock_profile_range.get_range_from_value.return_value = self.range["label"]

        self.report_instance.add_metrics(data, metrics, self.profile_ranges)

        self.assertEqual(data, expected_data)

    @patch("src.service.dynamic_report.dynamic_report.DynamicReport.add_metrics")
    @patch("src.service.dynamic_report.dynamic_report.DynamicReport.anonymize_data")
    def test_get_year_report_when_user_has_access_should_return_unrestricted_data(
        self, mock_anonymize_data, mock_add_metrics
    ):
        metrics = ["gross_profit"]
        data = {
            "1": {
                "name": "Test Company",
                "sector": "Something",
                "prior_actuals_revenue": 34,
                "gross_profit": 34,
            }
        }
        average = 34
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

        mock_anonymize_data.assert_not_called()
        mock_add_metrics.assert_called()
        self.assertEqual(
            peers,
            {
                "headers": ["name", "gross_profit"],
                "company_comparison_data": {
                    "name": "Test Company",
                    "sector": "Something",
                    "prior_actuals_revenue": 34,
                    "gross_profit": 34,
                },
                "peers_comparison_data": [],
                "averages": {"gross_profit": average},
            },
        )

    @patch("src.service.dynamic_report.dynamic_report.DynamicReport.add_metrics")
    @patch("src.service.dynamic_report.dynamic_report.DynamicReport.anonymize_data")
    def test_get_year_report_when_user_has_not_access_should_return_anonymized_data(
        self, mock_anonymize_data, mock_add_metrics
    ):
        metrics = ["gross_profit"]
        data = {
            "1": {
                "name": "Test Company",
                "sector": "Something",
                "prior_actuals_revenue": 34,
                "gross_profit": size_range.get("label"),
            }
        }
        average = 30
        self.company_anonymization.companies = ["1"]
        self.user_service.get_user_company_permissions.return_value = []

        peers = self.report_instance.get_year_report(
            "1",
            "user@test.com",
            data,
            False,
            False,
            metrics,
            sector=["Computer Hardware"],
        )

        mock_anonymize_data.assert_called()
        mock_add_metrics.assert_called()
        self.assertEqual(
            peers,
            {
                "headers": ["name", "gross_profit"],
                "company_comparison_data": {
                    "name": "Test Company",
                    "sector": "Something",
                    "prior_actuals_revenue": 34,
                    "gross_profit": size_range.get("label"),
                },
                "peers_comparison_data": [],
                "averages": {"gross_profit": average},
            },
        )

    def test_get_year_report_without_metrics_should_return_empty_dict(self):
        self.user_service.get_user_company_permissions.return_value = [{"id": "1"}]
        headers = ["name"]
        headers.extend(COMPARISON_METRICS)
        averages = dict()
        for metric in COMPARISON_METRICS:
            averages.update({metric: "NA"})

        peers = self.report_instance.get_year_report(
            "1", "user@test.com", {}, False, True, []
        )

        self.assertEqual(
            peers,
            {
                "headers": headers,
                "company_comparison_data": {},
                "peers_comparison_data": [],
                "averages": averages,
            },
        )

    def test_get_year_report_should_raise_exception(self):
        self.user_service.get_user_company_permissions.side_effect = Exception("error")
        headers = ["name"]
        headers.extend(COMPARISON_METRICS)

        with self.assertRaises(Exception) as context:
            self.report_instance.get_year_report(
                "1", "user@test.com", {}, False, True, []
            )

        self.assertEqual(str(context.exception), "error")

    @patch("src.service.dynamic_report.dynamic_report.DynamicReport.get_year_report")
    @patch("src.service.dynamic_report.dynamic_report.DynamicReport.get_base_metrics")
    def test_get_dynamic_report_with_calendar_year_should_return_report(
        self, mock_get_base_metrics, mock_get_year_report
    ):
        expected_peers = {
            "headers": ["name", "actuals_revenue"],
            "company_comparison_data": {},
            "peers_comparison_data": [
                {"id": "1", "name": "Test company", "actuals_revenue": 34}
            ],
        }
        mock_get_year_report.return_value = expected_peers

        report = self.report_instance.get_dynamic_report(
            "1", "user@test.com", ["actuals_revenue"], 2020, True, True
        )

        self.assertEqual(report, expected_peers)
        mock_get_base_metrics.assert_called()
        mock_get_year_report.assert_called()

    def test_get_dynamic_report_without_year_should_return_empty_values(self):
        expected_peers = {
            "headers": [],
            "company_comparison_data": {},
            "peers_comparison_data": [],
            "averages": {},
        }

        report = self.report_instance.get_dynamic_report(
            "1", "user@test.com", ["actuals_revenue"], None, True, True
        )

        self.assertEqual(report, expected_peers)

    @patch(
        "src.service.dynamic_report.dynamic_report.DynamicReport.get_dynamic_calendar_year_report"
    )
    def test_get_dynamic_report_when_report_fails_should_raise_error(
        self, mock_get_dynamic_calendar_year_report
    ):
        mock_get_dynamic_calendar_year_report.side_effect = Exception("error")

        with self.assertRaises(Exception) as context:
            self.report_instance.get_dynamic_report(
                "1", "user@test.com", ["actuals_revenue"], 2020, True, True
            )

        self.assertEqual(str(context.exception), "error")
