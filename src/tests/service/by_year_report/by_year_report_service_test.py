from unittest import TestCase
import logging
from unittest.mock import Mock, patch
from src.service.by_year_report.by_year_report_service import ByYearReportService
from src.service.calculator.calculator_service import CalculatorService
from src.utils.company_anonymization import CompanyAnonymization

logger = logging.getLogger()
logger.setLevel(logging.INFO)
size_range = {"label": "$30-<50 million", "max_value": 50, "min_value": 30}

service_path = "src.service.by_year_report.by_year_report_service.ByYearReportService"


class TestByYearReport(TestCase):
    def setUp(self):
        self.calculator = CalculatorService(logger)
        self.company_anonymization = CompanyAnonymization(object)
        self.mock_base_metrics_reports = Mock()
        self.mock_repository = Mock()
        self.mock_profile_range = Mock()
        self.report_instance = ByYearReportService(
            logger,
            self.mock_base_metrics_reports,
            self.mock_repository,
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
            "clv_cac_ratio": "0.9x",
            "cac_ratio": "1.38x",
            "opex_of_revenue": 620,
            "revenue_per_employee": 981132,
            "gross_retention": -569,
            "net_retention": -500,
            "new_bookings_growth": 11,
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
            "actuals_customer_lifetime_value": 82,
            "actuals_customer_acquition_costs": 87,
            "actuals_customer_annual_value": 63,
            "actuals_other_operating_expenses": 68,
            "actuals_headcount": 53,
            "actuals_run_rate_revenue": 52,
            "actuals_losses_and_downgrades": 87,
            "actuals_upsells": 9,
            "actuals_new_bookings": 8,
            "prior_actuals_new_bookings": 76,
            "prior_actuals_run_rate_revenue": 13,
        }

        self.rule_of_40 = {
            "id": self.company["id"],
            "name": self.company["name"],
            "revenue_growth_rate": self.metrics["growth"],
            "ebitda_margin": self.metrics["ebitda_margin"],
            "revenue": self.metrics["revenue"],
        }
        self.range = {"label": "$30-<50 million", "max_value": 50, "min_value": 30}
        self.profile_ranges = {
            "revenue": [size_range],
            "growth": [size_range],
            "revenue_per_employee": [size_range],
            "gross_profit": [size_range],
        }

    def test_remove_base_metrics_should_remove_all_input_metrics(self):
        data = self.scenarios.copy()
        data.update(self.metrics)

        self.report_instance.remove_base_metrics(data)

        self.assertEqual(data, self.metrics)

    def test_get_comparison_vs_data_should_return_data_number_when_user_has_permissions(
        self,
    ):
        data = self.scenarios.copy()
        data.update(self.metrics)
        data.update(self.company)
        self.mock_base_metrics_reports.get_rule_of_40.return_value = self.rule_of_40

        rule_of_40 = self.report_instance.get_comparison_vs_data(
            True, {self.company["id"]: data}, [], self.profile_ranges
        )

        self.assertEqual(rule_of_40, [self.rule_of_40])
        self.mock_base_metrics_reports.get_rule_of_40.assert_called_once()

    def test_get_comparison_vs_data_whithout_user_permissions_should_return_data_anonymized(
        self,
    ):
        data = self.scenarios.copy()
        data.update(self.company)
        expected_rule_of_40 = self.rule_of_40.copy()
        expected_rule_of_40["name"] = "0123-xxxx"
        self.mock_base_metrics_reports.get_rule_of_40.return_value = expected_rule_of_40

        rule_of_40 = self.report_instance.get_comparison_vs_data(
            False, {self.company["id"]: data}, [], self.profile_ranges
        )

        self.assertEqual(rule_of_40, [expected_rule_of_40])
        self.mock_base_metrics_reports.get_rule_of_40.assert_called_once()
        self.mock_base_metrics_reports.anonymize_name.called_once()

    def test_get_report_base_data_when_success_should_return_merged_dict(self):
        self.mock_repository.get_actuals_values.return_value = {
            self.company["id"]: {"actuals_revenue": 20}
        }
        self.mock_repository.get_budget_values.return_value = {
            self.company["id"]: {"budget_revenue": 22}
        }
        self.mock_repository.get_prior_year_revenue_values.return_value = {
            "012245": {"prior_actuals_revenue": 12}
        }
        expected_base_data = {
            self.company["id"]: {"actuals_revenue": 20, "budget_revenue": 22}
        }

        base_data = self.report_instance.get_report_base_data(2020)

        self.assertEqual(base_data, expected_base_data)

    @patch(f"{service_path}.get_report_base_data")
    @patch(f"{service_path}.get_comparison_vs_data")
    def test_get_by_year_report_when_comes_from_main_should_return_only_peers(
        self, mock_get_comparison_vs_data, mock_get_report_base_data
    ):
        data = self.company.copy()
        data.update(self.metrics)
        peer_data = {self.company["id"]: data}
        mock_get_report_base_data.return_value = peer_data
        self.mock_base_metrics_reports.get_profiles_ranges.return_value = (
            self.profile_ranges
        )
        mock_get_comparison_vs_data.return_value = []
        self.mock_base_metrics_reports.filter_by_conditions.return_value = peer_data
        self.mock_base_metrics_reports.get_peers_sorted.side_effect = lambda x: list(
            x.values()
        )

        report_data = self.report_instance.get_by_year_report(
            None, "user@test.com", 2020, True, True, sector=[]
        )

        self.assertEqual(
            report_data,
            {
                "company_comparison_data": {},
                "peers_comparison_data": [data],
                "rule_of_40": [],
            },
        )

    @patch(f"{service_path}.get_report_base_data")
    @patch(f"{service_path}.get_comparison_vs_data")
    def test_get_by_year_report_when_comes_from_company_should_return_only_company(
        self, mock_get_comparison_vs_data, mock_get_report_base_data
    ):
        data = self.company.copy()
        label = self.range["label"]
        data.update(self.metrics)
        peer_data = {self.company["id"]: data}
        mock_get_report_base_data.return_value = peer_data
        self.mock_base_metrics_reports.get_profiles_ranges.return_value = (
            self.profile_ranges
        )
        self.mock_base_metrics_reports.get_allowed_companies.return_value = []
        mock_get_comparison_vs_data.return_value = []
        self.mock_profile_range.get_profile_ranges.return_value = [self.range]
        self.mock_profile_range.get_range_from_value.return_value = label
        self.mock_base_metrics_reports.filter_by_conditions.return_value = peer_data
        self.mock_base_metrics_reports.get_peers_sorted.side_effect = lambda x: list(
            x.values()
        )

        report_data = self.report_instance.get_by_year_report(
            self.company["id"], "user@test.com", 2020, False, False, sector=[]
        )

        self.assertEqual(
            report_data,
            {
                "company_comparison_data": data,
                "peers_comparison_data": [],
                "rule_of_40": [],
            },
        )

    @patch(f"{service_path}.get_report_base_data")
    @patch(f"{service_path}.get_comparison_vs_data")
    def test_get_by_year_report_when_user_does_not_have_access_should_return_anonymized_data(
        self, mock_get_comparison_vs_data, mock_get_report_base_data
    ):
        data = self.company.copy()
        data.update(self.metrics)
        peer_data = {self.company["id"]: data}
        mock_get_report_base_data.return_value = peer_data
        self.mock_base_metrics_reports.get_profiles_ranges.return_value = (
            self.profile_ranges
        )
        mock_get_comparison_vs_data.return_value = []
        self.mock_base_metrics_reports.filter_by_conditions.return_value = peer_data
        self.mock_base_metrics_reports.get_peers_sorted.side_effect = lambda x: list(
            x.values()
        )

        report_data = self.report_instance.get_by_year_report(
            self.company["id"], "user@test.com", 2020, False, True, sector=[]
        )

        self.assertEqual(
            report_data,
            {
                "company_comparison_data": data,
                "peers_comparison_data": [],
                "rule_of_40": [],
            },
        )

    def test_get_by_year_report_when_fails_should_raise_exception(self):
        error_message = "Cannot get permissions"
        self.mock_base_metrics_reports.set_company_permissions.side_effect = Exception(
            error_message
        )

        with self.assertRaises(Exception) as context:
            self.report_instance.get_by_year_report(
                None, "user@test.com", 2020, True, False, sector=[]
            )

        self.assertEqual(str(context.exception), error_message)
