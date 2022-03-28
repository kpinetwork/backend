from unittest import TestCase, mock
import logging
from unittest.mock import Mock
from parameterized import parameterized
from src.service.company_report_vs_peers.company_report_vs_peers_service import (
    CompanyReportvsPeersService,
)
from src.service.calculator.calculator_repository import CalculatorRepository
from src.service.calculator.calculator_service import CalculatorService
from src.utils.company_anonymization import CompanyAnonymization

logger = logging.getLogger()
logger.setLevel(logging.INFO)
size_range = {"label": "$30-<50 million", "max_value": 50, "min_value": 30}
growth_range = {"label": "Low growth", "max_value": 0, "min_value": 10}


def get_range_response(*args, **kwargs):
    profile_type = args[0]
    if profile_type == "size profile":
        return [size_range]
    elif profile_type == "growth profile":
        return [growth_range]


class TestCompanyReportvsPeers(TestCase):
    def setUp(self):
        self.mock_session = Mock()
        self.mock_query_builder = Mock()
        self.mock_response_sql = Mock()
        self.company_anonymization = CompanyAnonymization(object)
        self.mock_profile_range = Mock()
        self.calculator = CalculatorService(logger)
        self.repository = CalculatorRepository(
            self.mock_session, self.mock_query_builder, self.mock_response_sql, logger
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

    @parameterized.expand(
        [
            [
                31,
                "size profile",
                {"label": "$30-<50 million", "max_value": 50, "min_value": 30},
            ],
            [None, "size profile", {}],
            [
                5,
                "growth profile",
                {"label": "Low growth", "max_value": 0, "min_value": 10},
            ],
        ]
    )
    def test_get_metric_range(self, value, type, ranges):
        self.mock_profile_range.get_profile_ranges.return_value = [ranges]

        range = self.report_service_instance.get_metric_range(value, type)

        self.assertEqual(range, ranges.get("label", "NA"))

    def test_get_metric_range_fail(self):
        self.mock_profile_range.get_profile_ranges.side_effect = Exception("error")

        range = self.report_service_instance.get_metric_range(34, "size profile")

        self.assertEqual(range, "NA")

    @mock.patch(
        "src.service.calculator.calculator_repository.CalculatorRepository.get_most_recents_revenue"
    )
    def test_get_profiles(self, mock_get_most_recents_revenue):
        expected_profile = {
            "size_cohort": self.company["size_cohort"],
            "margin_group": self.company["margin_group"],
        }
        revenues = [{"value": 40}, {"value": 37.5}]
        mock_get_most_recents_revenue.return_value = revenues
        self.mock_profile_range.get_profile_ranges.side_effect = get_range_response

        profile = self.report_service_instance.get_profiles(self.scenarios)

        self.assertEqual(profile, expected_profile)

    @mock.patch(
        "src.service.calculator.calculator_repository.CalculatorRepository.get_most_recents_revenue"
    )
    def test_get_description(self, mock_get_most_recents_revenue):
        company = self.company.copy()
        company.update(self.scenarios)
        revenues = [{"value": 40}, {"value": 37.5}]
        mock_get_most_recents_revenue.return_value = revenues
        self.mock_profile_range.get_profile_ranges.side_effect = get_range_response

        description = self.report_service_instance.get_description(company)

        self.assertEqual(description, self.company)

    def test_get_description_with_empty_company(self):
        company = dict()

        description = self.report_service_instance.get_description(company)

        self.assertEqual(description, company)
        self.mock_profile_range.get_profile_ranges.assert_not_called()

    def test_get_financial_profile(self):
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

    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    @mock.patch(
        "src.service.calculator.calculator_repository.CalculatorRepository.get_metric_by_scenario"
    )
    @mock.patch(
        "src.service.calculator.calculator_repository.CalculatorRepository.get_most_recents_revenue"
    )
    def test_get_company_report(
        self,
        mock_get_most_recents_revenue,
        mock_get_metric_by_scenario,
        mock_set_company_permissions,
    ):
        company = self.company.copy()
        company.update(self.scenarios)
        revenues = [{"value": 40}, {"value": 37.5}]
        mock_get_most_recents_revenue.return_value = revenues
        self.mock_base_metric_results({company["id"]: company})
        self.mock_profile_range.get_profile_ranges.side_effect = get_range_response

        report = self.report_service_instance.get_company_report(
            "0123456", "user@email.com", 2020, True
        )

        self.assertEqual(
            report, {"description": self.company, "financial_profile": self.metrics}
        )
        mock_get_metric_by_scenario.assert_called()
        mock_set_company_permissions.assert_called()

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
    @mock.patch(
        "src.service.calculator.calculator_repository.CalculatorRepository.get_metric_by_scenario"
    )
    def test_get_company_report_fail(
        self, mock_get_metric_by_scenario, mock_set_company_permissions
    ):
        mock_get_metric_by_scenario.side_effect = Exception("error")

        with self.assertRaises(Exception) as context:
            self.report_service_instance.get_company_report(
                "0123456", "user@email.com", 2020, True
            )

        self.assertEqual(str(context.exception), "error")
        mock_get_metric_by_scenario.assert_called()
        mock_set_company_permissions.assert_called()
