from unittest import TestCase
import logging
from unittest.mock import Mock
from parameterized import parameterized
from src.service.universe_overview.universe_overview_service import (
    UniverseOverviewService,
)
from src.service.calculator.calculator_service import CalculatorService

logger = logging.getLogger()
logger.setLevel(logging.INFO)
size_range = {"label": "$30-<50 million", "max_value": 50, "min_value": 30}


class TestUniverseOverview(TestCase):
    def setUp(self):
        self.mock_profile_range = Mock()
        self.calculator = CalculatorService(logger)
        self.mock_repository = Mock()
        self.overview_instance = UniverseOverviewService(
            logger, self.calculator, self.mock_repository, self.mock_profile_range
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
            "growth": 60,
            "ebitda_margin": -37.5,
            "rule_of_40": 22.50,
            "size_cohort": "$30-<50 million",
            "budget_growth": 16.67,
            "budget_ebitda_margin": -34.29,
            "revenue_vs_budget": 114.29,
            "ebitda_vs_budget": 125,
        }

        self.scenarios = {
            "actuals_revenue": 40,
            "actuals_ebitda": -15,
            "prior_actuals_revenue": 25,
            "budget_revenue": 35,
            "budget_ebitda": -12,
            "next_budget_revenue": 40,
            "next_budget_ebitda": -6,
            "prior_budget_revenue": 30,
            "prior_budget_ebitda": -13,
        }

        self.data = [
            {"growth": 30, "ebitda_margin": 30.5, "rule_of_40": 60.5},
            {"growth": 25, "ebitda_margin": 20, "rule_of_40": 45},
            {"growth": "NA", "ebitda_margin": 40.5, "rule_of_40": "NA"},
        ]

    def test_get_revenue_range_with_no_valid_number(self):
        metric = "NA"

        range = self.overview_instance.get_revenue_range(30)

        self.assertEqual(range, metric)

    def test_get_revenue_range_with_error_should_return_NA(self):
        metric = "NA"
        self.mock_profile_range.get_profile_ranges.side_effect = Exception("Error")

        range = self.overview_instance.get_revenue_range(metric)

        self.assertEqual(range, metric)

    def test_add_calculated_metrics_to_companies(self):
        self.mock_profile_range.get_profile_ranges.return_value = [size_range]
        scenarios = self.scenarios.copy()
        company = self.scenarios.copy()
        company.update(self.metrics)

        self.overview_instance.add_calculated_metrics_to_companies([scenarios])

        for key, value in scenarios.items():
            if self.calculator.is_valid_number(value):
                scenarios[key] = round(value, 2)
        self.assertEqual([scenarios], [company])

    @parameterized.expand([["growth", 27.5], ["ebitda_margin", 30.33]])
    def test_get_kpi_average_should_return_mean(self, metric, metric_average):

        average = self.overview_instance.get_kpi_average(metric, self.data)

        self.assertEqual(average, metric_average)

    def test_get_kpi_average_should_return_zero_when_fails(self):
        data = [
            {"growth": "NA", "ebitda_margin": 30.5},
            {"growth": "NA", "ebitda_margin": 20},
            {"growth": "NA", "ebitda_margin": 40.5},
        ]

        average = self.overview_instance.get_kpi_average("growth", data)

        self.assertEqual(average, 0)

    def test_get_kpi_averages(self):
        expected_averages = [
            {"growth": 27.5},
            {"ebitda_margin": 30.33},
            {"rule_of_40": 52.75},
        ]

        kpi_averages = self.overview_instance.get_kpi_averages(self.data)

        self.assertEqual(kpi_averages, expected_averages)

    def test_get_companies_by_size_cohort(self):
        company = self.scenarios.copy()
        company.update(self.metrics)
        secondary_company = company.copy()

        expected_company_by_size = {
            company["size_cohort"]: [company.copy(), secondary_company]
        }

        companies_by_size = self.overview_instance.get_companies_by_size_cohort(
            [company, secondary_company]
        )

        self.assertEqual(companies_by_size, expected_company_by_size)

    def get_companies_by_size(self):
        company = self.scenarios.copy()
        company.update(self.metrics)
        return {company["size_cohort"]: [company.copy()]}

    def test_get_count_by_size(self):
        company_by_size = self.get_companies_by_size()
        expected_count_by_size = [
            {"size_cohort": self.metrics["size_cohort"], "count": 1}
        ]

        count_by_size = self.overview_instance.get_count_by_size(company_by_size)

        self.assertEqual(count_by_size, expected_count_by_size)

    def test_get_metric_by_size(self):
        size_cohort = self.metrics["size_cohort"]
        company_by_size = {
            size_cohort: [
                {"growth": 20, "ebitda_margin": 10},
                {"growth": 10, "ebitda_margin": 4},
            ]
        }
        expected_metric_by_size = {
            size_cohort: {"size_cohort": size_cohort, "margin": 7}
        }

        metric_by_size = self.overview_instance.get_metric_by_size(
            company_by_size, "ebitda_margin", "margin"
        )

        self.assertEqual(metric_by_size, expected_metric_by_size)

    def test_merge_metric_dicts(self):
        metric = {"1": {"growth": 30}}
        pair_metric = {"1": {"margin": 40}}
        expected_metric = {"1": {"growth": 30, "margin": 40}}

        self.overview_instance.merge_metric_dicts(metric, pair_metric)

        self.assertEqual(metric, expected_metric)

    @parameterized.expand(
        [
            [False, 15, 7],
            [True, 18, 9.5],
        ]
    )
    def test_get_growth_and_margin_by_size(self, budgeted, growth, margin):
        size_cohort = self.metrics["size_cohort"]
        company_by_size = {
            size_cohort: [
                {
                    "growth": 20,
                    "ebitda_margin": 10,
                    "budget_ebitda_margin": 13,
                    "budget_growth": 25,
                },
                {
                    "growth": 10,
                    "ebitda_margin": 4,
                    "budget_ebitda_margin": 6,
                    "budget_growth": 11,
                },
            ]
        }
        expected_growth_margin = {
            size_cohort: {
                "size_cohort": size_cohort,
                "growth": growth,
                "margin": margin,
            }
        }

        growth_margin = self.overview_instance.get_growth_and_margin_by_size(
            company_by_size, budgeted
        )

        self.assertEqual(growth_margin, expected_growth_margin)

    def test_get_revenue_and_ebitda_by_size(self):
        size_cohort = self.metrics["size_cohort"]
        company_by_size = {
            size_cohort: [
                {"revenue_vs_budget": 6, "ebitda_vs_budget": 3.5},
                {"revenue_vs_budget": 4.3, "ebitda_vs_budget": 8},
            ]
        }
        expected_revenue_ebitda = {
            size_cohort: {"size_cohort": size_cohort, "revenue": 5.15, "ebitda": 5.75}
        }

        revenue_ebitda = self.overview_instance.get_revenue_and_ebitda_by_size(
            company_by_size
        )

        self.assertEqual(revenue_ebitda, expected_revenue_ebitda)

    def test_get_universe_overview_success(self):
        company = self.scenarios.copy()
        data = {self.company["id"]: company}
        self.mock_profile_range.get_profile_ranges.return_value = [size_range]
        self.mock_repository.get_base_metrics.return_value = data
        expected_overview = {
            "kpi_average": [
                {"growth": 60.0},
                {"ebitda_margin": -37.5},
                {"rule_of_40": 22.5},
            ],
            "count_by_size": [{"size_cohort": "$30-<50 million", "count": 1}],
            "growth_and_margin": {
                "$30-<50 million": {
                    "size_cohort": "$30-<50 million",
                    "growth": 60.0,
                    "margin": -37.5,
                }
            },
            "expected_growth_and_margin": {
                "$30-<50 million": {
                    "size_cohort": "$30-<50 million",
                    "growth": 16.67,
                    "margin": -34.29,
                }
            },
            "revenue_and_ebitda": {
                "$30-<50 million": {
                    "size_cohort": "$30-<50 million",
                    "revenue": 114.29,
                    "ebitda": 125.0,
                }
            },
        }

        universe_overview = self.overview_instance.get_universe_overview("2020")

        self.assertEqual(universe_overview, expected_overview)

    def test_get_universe_overview_fail(self):
        self.mock_repository.get_base_metrics.side_effect = Exception("error")

        with self.assertRaises(Exception) as context:
            self.overview_instance.get_universe_overview("2020")

        self.assertEqual(str(context.exception), "error")
