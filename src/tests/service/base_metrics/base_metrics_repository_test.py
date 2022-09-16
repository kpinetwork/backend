from unittest import TestCase
import logging
from unittest.mock import Mock
from parameterized import parameterized
from src.service.base_metrics.base_metrics_repository import BaseMetricsRepository

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestBaseMetricsRepository(TestCase):
    def setUp(self):
        self.mock_session = Mock()
        self.mock_query_builder = Mock()
        self.mock_response_sql = Mock()
        self.mock_profile_range = Mock()
        self.repository = BaseMetricsRepository(
            logger, self.mock_session, self.mock_query_builder, self.mock_response_sql
        )
        self.company = {
            "id": "0123456",
            "name": "Company Test",
            "sector": "Computer Hardware",
            "vertical": "Life Sciences",
            "inves_profile_name": "Early stage VC",
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

    def mock_response_list_query_sql(self, response):
        attrs = {"process_query_list_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def test_add_company_filters_with_data(self):
        expected_out = {"company.sector": ["'Application'"]}

        filters_out = self.repository.add_company_filters(sector=["Application"])

        self.assertEqual(filters_out, expected_out)

    @parameterized.expand(
        [
            [0, "Revenue", "Actuals", "actuals_revenue"],
            [1, "Ebitda", "Budget", "next_budget_ebitda"],
            [-1, "Cost of goods", "Actuals", "prior_actuals_cost_of_goods"],
        ]
    )
    def test_get_metric_name_year_should_return_dict_key_as_name(
        self, year, metric, scenario, expected_name
    ):

        metric_name = self.repository._BaseMetricsRepository__get_metric_name_year(
            metric, scenario, year
        )

        self.assertEqual(metric_name, expected_name)

    def test_get_actuals_values_should_return_data_with_descriptive_company_info(self):
        company = self.company.copy()
        company.update(
            {
                "metric": "Revenue",
                "scenario": "Actuals",
                "year": 2020,
                "value": self.scenarios["actuals_revenue"],
            }
        )
        expected_actuals = self.company.copy()
        expected_actuals.update({"actuals_revenue": 40})
        self.mock_response_list_query_sql([company])

        actuals_values = self.repository.get_actuals_values(
            2020, {"sector": [self.company["sector"]]}
        )

        self.assertEqual(actuals_values, {company["id"]: expected_actuals})

    def test_get_budget_values_should_return_only_metric_pair_value(self):
        company = self.company.copy()
        company.update(
            {
                "metric": "Revenue",
                "scenario": "Budget",
                "year": 2020,
                "value": self.scenarios["actuals_revenue"],
            }
        )
        expected_budget = {"budget_revenue": 40}
        expected_budget.update(self.company)
        self.mock_response_list_query_sql([company])

        budget_values = self.repository.get_budget_values(2020, [2020], {}, ["Revenue"])

        self.assertEqual(budget_values, {company["id"]: expected_budget})

    def test_get_budget_values_should_raise_exception_when_db_call_fails(self):
        error_message = "No valid query"
        self.mock_session.execute.side_effect = Exception(error_message)

        with self.assertRaises(Exception) as context:
            self.repository.get_budget_values(2020, [2020], {}, ["Revenue"])

        self.assertEqual(str(context.exception), error_message)

    def test_get_prior_year_revenue_values_should_return_only_values(self):
        company = self.company.copy()
        company.update(
            {
                "metric": "Revenue",
                "scenario": "Actuals",
                "year": 2020,
                "value": self.scenarios["prior_actuals_revenue"],
            }
        )
        expected_prior_values = {"prior_actuals_revenue": 37.5}
        self.mock_response_list_query_sql([company])

        prior_values = self.repository.get_prior_year_revenue_values(2021, {})

        self.assertEqual(prior_values, {company["id"]: expected_prior_values})
