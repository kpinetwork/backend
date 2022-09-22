from unittest import TestCase, mock
import logging
from unittest.mock import Mock
from parameterized import parameterized
from src.service.company_report_vs_peers.company_report_vs_peers_service import (
    CompanyReportvsPeersService,
)
from src.service.calculator.calculator_service import CalculatorService
from src.utils.company_anonymization import CompanyAnonymization
from src.service.base_metrics.base_metrics_repository import BaseMetricsRepository

logger = logging.getLogger()
logger.setLevel(logging.INFO)
size_range = {"label": "$30-<50 million", "max_value": 50, "min_value": 30}
growth_range = {"label": "Low growth", "max_value": 0, "min_value": 10}
repository_path = (
    "src.service.base_metrics.base_metrics_repository.BaseMetricsRepository"
)


def get_range_response(*args, **kwargs):
    profile_type = args[0]
    if profile_type == "size profile":
        return [size_range]
    elif profile_type == "growth profile":
        return [growth_range]


def get_range_value(*args, **kwargs):
    profile_type = args[1]
    if profile_type == "size profile":
        return size_range.get("label")
    elif profile_type == "growth profile":
        return growth_range.get("label")


class TestCompanyReportvsPeers(TestCase):
    def setUp(self):
        self.mock_session = Mock()
        self.mock_query_builder = Mock()
        self.mock_response_sql = Mock()
        self.company_anonymization = CompanyAnonymization(object)
        self.mock_profile_range = Mock()
        self.calculator = CalculatorService(logger)
        self.repository = BaseMetricsRepository(
            logger, self.mock_session, self.mock_query_builder, self.mock_response_sql
        )
        self.report_service_instance = CompanyReportvsPeersService(
            logger,
            self.calculator,
            self.repository,
            self.mock_profile_range,
            self.company_anonymization,
        )
        self.company = {
            "id": "0123456",
            "name": "Company Test",
            "sector": "Computer Hardware",
            "vertical": "Life Sciences",
            "inves_profile_name": "Early stage VC",
            "size_cohort": "$30-<50 million",
            "margin_group": "Low growth",
        }

        self.metrics = {
            "annual_revenue": 40,
            "annual_ebitda": -15,
            "annual_rule_of_40": -31,
            "forward_revenue_growth": 14,
            "forward_ebitda_growth": -50,
            "forward_rule_of_40": -1,
        }

        self.scenarios = {
            "actuals_revenue": 40,
            "actuals_ebitda": -15,
            "prior_actuals_revenue": 37.5,
            "budget_revenue": 35,
            "budget_ebitda": -12,
            "next_budget_revenue": 40,
            "next_budget_ebitda": -6,
        }

    def mock_base_metric_results(self, response):
        attrs = {"proccess_base_metrics_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def mock_process_query_list_results(self, response):
        attrs = {"process_query_list_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def test_get_profiles_should_return_vallid_range(self):
        expected_profile = {
            "size_cohort": self.company["size_cohort"],
            "margin_group": self.company["margin_group"],
        }
        self.mock_profile_range.get_profile_ranges.side_effect = get_range_response
        self.mock_profile_range.get_range_from_value.side_effect = get_range_value

        profile = self.report_service_instance.get_profiles(self.scenarios)

        self.assertEqual(profile, expected_profile)

    def test_get_description_should_return_metrics_with_no_empty_company(self):
        company = self.company.copy()
        company.update(self.scenarios)
        self.mock_profile_range.get_profile_ranges.side_effect = get_range_response
        self.mock_profile_range.get_range_from_value.side_effect = get_range_value

        description = self.report_service_instance.get_description(company)

        self.assertEqual(description, self.company)

    def test_get_description_should_return_empty_dict_with_empty_company(self):
        company = dict()

        description = self.report_service_instance.get_description(company)

        self.assertEqual(description, company)
        self.mock_profile_range.get_profile_ranges.assert_not_called()

    def test_get_financial_profile_should_return_dict_with_metrics(self):
        company = self.company.copy()
        company.update(self.scenarios)
        self.mock_profile_range.get_profile_ranges.side_effect = get_range_response

        financial_profile = self.report_service_instance.get_financial_profile(company)

        self.assertEqual(financial_profile, self.metrics)

    def test_get_financial_profile_with_empty_company(self):
        company = dict()

        financial_profile = self.report_service_instance.get_financial_profile(company)

        self.assertEqual(financial_profile, company)
        self.mock_profile_range.get_profile_ranges.assert_not_called()

    @parameterized.expand(
        [
            [["0123456"], "0123456", True],
            [[], "0123456", False],
            [["1234"], "01234", False],
        ]
    )
    def test_has_permissions(self, companies, id, permitted):
        self.company_anonymization.companies = companies

        uses_has_permissions = self.report_service_instance.has_permissions(id)

        self.assertEqual(uses_has_permissions, permitted)

    @mock.patch(f"{repository_path}.get_actuals_values")
    @mock.patch(f"{repository_path}.get_budget_values")
    @mock.patch(f"{repository_path}.get_prior_year_revenue_values")
    def test_get_company_data_should_return_data(
        self,
        mock_get_prior_year_revenue_values,
        mock_get_budget_values,
        mock_get_actuals_values,
    ):
        company = self.company.copy()
        company.update(self.scenarios)
        mock_get_actuals_values.return_value = {
            self.company["id"]: {"actuals_revenue": 10}
        }
        mock_get_budget_values.return_value = {
            self.company["id"]: {"budget_revenue": 15}
        }
        mock_get_prior_year_revenue_values.return_value = {
            "01223-test": {"prior_actuals_revenue": 12}
        }

        report = self.report_service_instance.get_company_data(self.company["id"], 2020)

        self.assertEqual(
            report, {self.company["id"]: {"actuals_revenue": 10, "budget_revenue": 15}}
        )
        mock_get_actuals_values.assert_called()

    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    @mock.patch(
        "src.service.calculator.calculator_repository.CalculatorRepository.get_metric_by_scenario"
    )
    def test_get_company_report_without_permissions(
        self, mock_get_metric_by_scenario, mock_set_company_permissions
    ):
        company = self.company.copy()
        company.update(self.scenarios)
        self.mock_base_metric_results({company["id"]: company})
        self.mock_profile_range.get_profile_ranges.side_effect = get_range_response

        report = self.report_service_instance.get_company_report(
            "0123456", "user@email.com", 2020, False
        )

        self.assertEqual(report, dict())
        mock_get_metric_by_scenario.assert_not_called()
        mock_set_company_permissions.assert_called()

    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    @mock.patch.object(CompanyReportvsPeersService, "get_company_data")
    def test_get_company_report_raise_exception_when_fails_getting_data(
        self, mock_get_company_data, mock_set_company_permissions
    ):
        mock_get_company_data.side_effect = Exception("error")

        with self.assertRaises(Exception) as context:
            self.report_service_instance.get_company_report(
                "0123456", "user@email.com", 2020, True
            )

        self.assertEqual(str(context.exception), "error")
        mock_get_company_data.assert_called()
        mock_set_company_permissions.assert_called()

    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    @mock.patch.object(CompanyReportvsPeersService, "get_company_data")
    @mock.patch.object(CompanyReportvsPeersService, "get_profiles")
    def test_get_company_report_with_empty_metric_data(
        self,
        mock_get_profiles,
        mock_get_company_data,
        mock_set_company_permissions,
    ):
        self.company_anonymization.companies = ["0123456"]
        company = self.company.copy()
        company.update(self.scenarios)
        mock_get_company_data.return_value = {self.company["id"]: company}
        mock_get_profiles.return_value = dict()
        expected_company_description = {
            param: value
            for param, value in self.company.items()
            if param not in ["size_cohort", "margin_group"]
        }

        report = self.report_service_instance.get_company_report(
            "0123456", "user@email.com", 2020, False
        )

        self.assertEqual(report.get("description"), expected_company_description)
        mock_get_company_data.assert_called()
        mock_set_company_permissions.assert_called()
