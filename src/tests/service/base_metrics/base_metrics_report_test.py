from unittest import TestCase
import logging
from unittest.mock import Mock
from parameterized import parameterized
from src.service.base_metrics.base_metrics_repository import BaseMetricsRepository
from src.service.base_metrics.base_metrics_report import BaseMetricsReport
from src.service.calculator.calculator_service import CalculatorService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestBaseMetricsReport(TestCase):
    def setUp(self):
        self.mock_session = Mock()
        self.mock_query_builder = Mock()
        self.mock_response_sql = Mock()
        self.mock_profile_range = Mock()
        self.calculator = CalculatorService(logger)
        self.mock_company_anonymization = Mock()
        self.repository = BaseMetricsRepository(
            logger, self.mock_session, self.mock_query_builder, self.mock_response_sql
        )
        self.report_instance = BaseMetricsReport(
            logger,
            self.calculator,
            self.mock_profile_range,
            self.mock_company_anonymization,
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
            "revenue": [self.range],
            "growth": [self.range],
            "revenue_per_employee": [self.range],
        }

    @parameterized.expand(
        [
            [
                {
                    "size_cohort": [],
                    "margin_group": [],
                },
                {
                    "0123456": {
                        "size_cohort": "NA",
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

    def test_get_allowed_companies_should_return_company_user_permissions_ids_class(
        self,
    ):
        companies = [self.company["id"]]
        self.mock_company_anonymization.companies = companies

        allowed_companies = self.report_instance.get_allowed_companies()

        self.assertEqual(allowed_companies, companies)

    def test_set_company_permissions_should_call_company_anonym_function(self):
        self.report_instance.set_company_permissions("user@test.com")

        self.mock_company_anonymization.set_company_permissions.assert_called_once()

    def test_get_peers_sorted_should_order_by_name(self):
        companies = {"1": {"name": "Company X"}, "2": {"name": "Company B"}}
        expected_companies = [{"name": "Company B"}, {"name": "Company X"}]

        companies_ordered = self.report_instance.get_peers_sorted(companies)

        self.assertEqual(companies_ordered, expected_companies)

    def test_get_profiles_ranges_should_return_dict_with_profiles(self):
        expected_fields = ["growth", "revenue", "revenue_per_employee"]

        profile_ranges = self.report_instance.get_profiles_ranges()

        self.assertEqual([*profile_ranges], expected_fields)

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
    def test_replace_metric_by_defined_ranges(self, revenue, ranges, label):
        company = self.company.copy()
        company["revenue"] = revenue
        self.mock_profile_range.get_profile_ranges.return_value = [ranges]
        self.mock_profile_range.get_range_from_value.return_value = label

        self.report_instance.replace_metric_by_defined_ranges(
            company, "revenue", "size profile", ranges
        )

        self.assertEqual(company.get("revenue"), label)

    def test_anonymize_name_should_replace_name(self):
        company = {"id": "01234", "name": "Test A"}
        self.mock_company_anonymization.anonymize_company_name.return_value = (
            "0123-xxxx"
        )

        self.report_instance.anonymize_name(company)

        self.assertEqual(company, {"id": company["id"], "name": "0123-xxxx"})

    def test_anonymized_companies_metrics_should_change_metric_values(self):
        label = self.range["label"]
        company = self.company.copy()
        company.update({"revenue": 31, "growth": 40, "gross_profit": 32})
        self.mock_profile_range.get_profile_ranges.return_value = [self.range]
        self.mock_profile_range.get_range_from_value.return_value = label
        expected_company = company.copy()
        expected_company.update(
            {
                "revenue": label,
                "growth": 40,
                "gross_profit": label,
                "revenue_per_employee": label,
            }
        )

        self.report_instance.anonymized_companies_metrics(
            False, {company["id"]: company}, [], self.profile_ranges
        )

        self.assertEqual(company, expected_company)

    def test_get_rule_of_40_should_return_dict_with_specific_metrics(self):
        company = self.company.copy()
        company.update(self.metrics)

        rule_of_40 = self.report_instance.get_rule_of_40(
            company, self.metrics["revenue"]
        )

        self.assertEqual(rule_of_40, self.rule_of_40)

    def test_calculate_metrics_should_add_calculated_metrics(self):
        company = self.scenarios.copy()
        expected_company = self.scenarios.copy()
        expected_company.update(self.metrics)
        expected_company.update({"size_cohort": "NA", "margin_group": "NA"})
        self.mock_profile_range.get_range_from_value.return_value = "NA"

        self.report_instance.calculate_metrics(company, self.profile_ranges)

        self.assertEqual(company, expected_company)
