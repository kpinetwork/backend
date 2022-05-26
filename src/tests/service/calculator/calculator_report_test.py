from unittest import TestCase
import logging
from unittest.mock import Mock
from parameterized import parameterized
from src.service.calculator.calculator_report import CalculatorReport
from src.service.calculator.calculator_service import CalculatorService
from src.utils.company_anonymization import CompanyAnonymization

logger = logging.getLogger()
logger.setLevel(logging.INFO)
size_range = {"label": "$30-<50 million", "max_value": 50, "min_value": 30}


class TestCalculatorReport(TestCase):
    def setUp(self):
        self.calculator = CalculatorService(logger)
        self.company_anonymization = CompanyAnonymization(object)
        self.mock_profile_range = Mock()
        self.report_instance = CalculatorReport(
            logger, self.calculator, self.mock_profile_range, self.company_anonymization
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
    def test_replace_revenue(self, revenue, ranges, label):
        company = self.company.copy()
        company["revenue"] = revenue
        self.mock_profile_range.get_profile_ranges.return_value = [ranges]

        self.report_instance.replace_revenue(company)

        self.assertEqual(company.get("revenue"), label)
        self.mock_profile_range.get_profile_ranges.assert_called()

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

        range = self.report_instance.get_metric_range(value, type)

        self.assertEqual(range, ranges.get("label", "NA"))

    def test_get_metric_range_fail(self):
        self.mock_profile_range.get_profile_ranges.side_effect = Exception("error")

        range = self.report_instance.get_metric_range(34, "size profile")

        self.assertEqual(range, "NA")

    def test_calculate_metrics(self):
        company = self.scenarios.copy()
        expected_company = self.scenarios.copy()
        expected_company.update({"size_cohort": "NA", "margin_group": "NA"})
        for key in self.metrics:
            expected_company[key] = self.metrics[key]

        self.report_instance.calculate_metrics(company)

        self.assertEqual(company, expected_company)

    @parameterized.expand(
        [[[], "0123-xxxx", "$30-<50 million"], [["0123456"], "Company Test", 40]]
    )
    def test_anonymized_company(self, allowed_companies, name, revenue):
        company = self.company.copy()
        self.mock_profile_range.get_profile_ranges.return_value = [self.range]

        self.report_instance.anonymized_company(company, allowed_companies)

        self.assertEqual(company.get("name"), name)

    def test_get_rule_of_40(self):
        company = self.company.copy()
        company.update(self.metrics)

        rule_of_40 = self.report_instance.get_rule_of_40(
            company, self.metrics["revenue"]
        )

        self.assertEqual(rule_of_40, self.rule_of_40)

    @parameterized.expand(
        [
            [
                {
                    "size_cohort": ["$30-<$50 million"],
                    "margin_group": ["Negative growth (<0%)"],
                },
                {
                    "0123456": {
                        "size_cohort": "$30-<$50 million",
                        "margin_group": "Negative growth (<0%)",
                    }
                },
            ],
            [
                {
                    "size_cohort": ["$50-$100 million"],
                    "margin_group": [],
                },
                {
                    "0123456": {
                        "size_cohort": "$50-$100 million",
                        "margin_group": "Low growth (0-<10%)",
                    }
                },
            ],
            [
                {"margin_group": ["Medium growth (10%-<30%)"], "size_cohort": []},
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

        filters_by_conditions = self.report_instance.filter_by_conditions(
            data, **conditions
        )

        self.assertEqual(filters_by_conditions, data)
