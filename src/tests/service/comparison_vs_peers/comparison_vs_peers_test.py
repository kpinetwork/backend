from unittest import TestCase, mock
import logging
from unittest.mock import Mock
from parameterized import parameterized
from src.service.comparison_vs_peers.comparison_vs_peers_service import (
    ComparisonvsPeersService,
)
from src.service.calculator.calculator_repository import CalculatorRepository
from src.service.calculator.calculator_service import CalculatorService
from src.utils.company_anonymization import CompanyAnonymization

logger = logging.getLogger()
logger.setLevel(logging.INFO)
size_range = {"label": "$30-<50 million", "max_value": 50, "min_value": 30}


class TestComparisonvsPeers(TestCase):
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
        self.comparison_service_instance = ComparisonvsPeersService(
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
        }

        self.metrics = {
            "revenue": 40,
            "growth": 7,
            "ebitda_margin": -38,
            "revenue_vs_budget": 114,
            "ebitda_vs_budget": 125,
            "rule_of_40": -31,
        }

        self.scenarios = {
            "actuals_revenue": 40,
            "actuals_ebitda": -15,
            "prior_actuals_revenue": 37.5,
            "budget_revenue": 35,
            "budget_ebitda": -12,
        }

        self.rule_of_40 = {
            "id": self.company["id"],
            "name": self.company["name"],
            "revenue_growth_rate": self.metrics["growth"],
            "ebitda_margin": self.metrics["ebitda_margin"],
            "revenue": self.metrics["revenue"],
        }

        self.range = {"label": "$30-<50 million", "max_value": 50, "min_value": 30}

    def mock_base_metric_results(self, response):
        attrs = {"proccess_base_metrics_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    @parameterized.expand(
        [
            [
                31,
                {"label": "$30-<50 million", "max_value": 50, "min_value": 30},
                "$30-<50 million",
            ],
            [None, {"label": "100+", "max_value": None, "min_value": 100}, "NA"],
            [50, {}, "NA"],
        ]
    )
    def test_remove_revenue(self, revenue, ranges, label):
        company = self.company.copy()
        company["revenue"] = revenue
        self.mock_profile_range.get_profile_ranges.return_value = [ranges]

        self.comparison_service_instance.remove_revenue(company)

        self.assertEqual(company.get("revenue"), label)
        self.mock_profile_range.get_profile_ranges.assert_called()

    def test_remove_base_metrics(self):
        company = self.company.copy()
        company["actuals_revenue"] = 30

        self.comparison_service_instance.remove_base_metrics(company)

        self.assertEqual(company, self.company)

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

        range = self.comparison_service_instance.get_metric_range(value, type)

        self.assertEqual(range, ranges.get("label", "NA"))

    def test_get_metric_range_fail(self):
        self.mock_profile_range.get_profile_ranges.side_effect = Exception("error")

        range = self.comparison_service_instance.get_metric_range(34, "size profile")

        self.assertEqual(range, "NA")

    def test_calculate_metrics(self):
        company = self.scenarios.copy()
        expected_company = self.scenarios.copy()
        expected_company.update({"size_cohort": "NA", "margin_group": "NA"})
        for key in self.metrics:
            expected_company[key] = self.metrics[key]

        self.comparison_service_instance.calculate_metrics(company)

        self.assertEqual(company, expected_company)

    @parameterized.expand(
        [[[], "0123-xxxx", "$30-<50 million"], [["0123456"], "Company Test", 40]]
    )
    def test_anonymized_company(self, allowed_companies, name, revenue):
        company = self.company.copy()
        self.mock_profile_range.get_profile_ranges.return_value = [self.range]

        self.comparison_service_instance.anonymized_company(company, allowed_companies)

        self.assertEqual(company.get("name"), name)

    def test_get_rule_of_40(self):
        company = self.company.copy()
        company.update(self.metrics)

        rule_of_40 = self.comparison_service_instance.get_rule_of_40(
            company, self.metrics["revenue"]
        )

        self.assertEqual(rule_of_40, self.rule_of_40)

    def test_get_comparison_vs_data_with_access(self):
        data = dict()
        company = self.company.copy()
        expected_company = self.company.copy()
        company.update(self.scenarios)
        metrics = self.metrics.copy()
        metrics.update({"size_cohort": "NA", "margin_group": "NA"})
        expected_company.update(metrics)
        data[company["id"]] = company

        rule_of_40 = self.comparison_service_instance.get_comparison_vs_data(data, True)

        self.assertEqual(rule_of_40, [self.rule_of_40])
        self.assertEqual(data[company["id"]], expected_company)

    def test_get_comparison_vs_data_without_access(self):
        company = self.company.copy()
        company.update(self.scenarios)
        data = {company["id"]: company}
        expected_company = self.company.copy()
        metrics = self.metrics.copy()
        metrics.update(
            {"size_cohort": "$30-<50 million", "margin_group": "$30-<50 million"}
        )
        expected_company.update(metrics)
        expected_company["revenue"] = self.range["label"]
        expected_company["name"] = "0123-xxxx"
        expected_rule_of_40 = self.rule_of_40.copy()
        expected_rule_of_40["name"] = "0123-xxxx"
        self.mock_profile_range.get_profile_ranges.return_value = [self.range]

        rule_of_40 = self.comparison_service_instance.get_comparison_vs_data(
            data, False
        )

        self.assertEqual(rule_of_40, [expected_rule_of_40])
        self.assertEqual(data[company["id"]], expected_company)

    @parameterized.expand(
        [
            [
                {
                    "size_cohort": "$30-<$50 million",
                    "margin_group": "Negative growth (<0%)",
                },
                {
                    "0123456": {
                        "size_cohort": "$30-<$50 million",
                        "margin_group": "Negative growth (<0%)",
                    }
                },
            ],
            [
                {"size_cohort": "$50-$100 million"},
                {
                    "0123456": {
                        "size_cohort": "$50-$100 million",
                        "margin_group": "Low growth (0-<10%)",
                    }
                },
            ],
            [
                {"margin_group": "Medium growth (10%-<30%)"},
                {
                    "0123456": {
                        "size_cohort": "100 million+",
                        "margin_group": "Medium growth (10%-<30%)",
                    }
                },
            ],
        ]
    )
    def test_filter_by_conditions(self, conditions, data):

        filters_by_conditions = self.comparison_service_instance.filter_by_conditions(
            data, **conditions
        )

        self.assertEqual(filters_by_conditions, data)

    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    @mock.patch(
        "src.service.calculator.calculator_repository.CalculatorRepository.get_metric_by_scenario"
    )
    def test_get_peers_comparison_from_main(
        self, mock_get_metric_by_scenario, mock_set_company_permissions
    ):
        company = self.company.copy()
        expected_company = self.company.copy()
        metrics = self.metrics.copy()
        metrics.update({"size_cohort": "NA", "margin_group": "NA"})
        expected_company.update(metrics)
        company.update(self.scenarios)
        self.mock_base_metric_results({company["id"]: company})

        comparison = self.comparison_service_instance.get_peers_comparison(
            None, "user@email.com", 2020, True, True
        )

        self.assertEqual(
            comparison,
            {
                "company_comparison_data": {},
                "peers_comparison_data": [expected_company],
                "rule_of_40": [self.rule_of_40],
            },
        )
        mock_get_metric_by_scenario.assert_called()
        mock_set_company_permissions.assert_called()

    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    @mock.patch(
        "src.service.calculator.calculator_repository.CalculatorRepository.get_metric_by_scenario"
    )
    def test_get_peers_comparison(
        self, mock_get_metric_by_scenario, mock_set_company_permissions
    ):
        company = self.company.copy()
        expected_company = self.company.copy()
        metrics = self.metrics.copy()
        metrics.update({"size_cohort": "NA", "margin_group": "NA"})
        expected_company.update(metrics)
        company.update(self.scenarios)
        self.mock_base_metric_results({company["id"]: company})

        comparison = self.comparison_service_instance.get_peers_comparison(
            company["id"], "user@email.com", 2020, False, True
        )

        self.assertEqual(
            comparison,
            {
                "company_comparison_data": expected_company,
                "peers_comparison_data": [],
                "rule_of_40": [self.rule_of_40],
            },
        )
        mock_get_metric_by_scenario.assert_called()
        mock_set_company_permissions.assert_called()

    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    @mock.patch(
        "src.service.calculator.calculator_repository.CalculatorRepository.get_metric_by_scenario"
    )
    def test_get_peers_comparison_fail(
        self, mock_get_metric_by_scenario, mock_set_company_permissions
    ):
        mock_get_metric_by_scenario.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            self.comparison_service_instance.get_peers_comparison(
                "123", "user@email.com", 2020, True, True
            )

        self.assertEqual(str(context.exception), "error")
        mock_get_metric_by_scenario.assert_called()
        mock_set_company_permissions.assert_called()
