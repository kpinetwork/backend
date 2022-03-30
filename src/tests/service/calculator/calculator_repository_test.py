from unittest import TestCase
import logging
from unittest.mock import Mock
from src.service.calculator.calculator_repository import CalculatorRepository

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestCalculatorRepository(TestCase):
    def setUp(self):
        self.mock_session = Mock()
        self.mock_query_builder = Mock()
        self.mock_response_sql = Mock()
        self.mock_profile_range = Mock()
        self.repository = CalculatorRepository(
            self.mock_session, self.mock_query_builder, self.mock_response_sql, logger
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

        self.scenarios = {
            "actuals_revenue": 40,
            "actuals_ebitda": -15,
            "prior_actuals_revenue": 37.5,
            "budget_revenue": 35,
            "budget_ebitda": -12,
            "next_budget_revenue": 40,
            "next_budget_ebitda": -6,
        }

    def mock_response_query_sql(self, response):
        attrs = {"process_query_result.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def mock_response_list_query_sql(self, response):
        attrs = {"process_query_list_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def mock_base_metric_results(self, response):
        attrs = {"proccess_base_metrics_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def test_get_company_description_success(self):
        self.mock_response_query_sql(self.company)

        company = self.repository.get_company_description("0123456")

        self.assertEqual(company, self.company)

    def test_get_company_description_with_invalid_id(self):
        self.mock_response_query_sql(dict())

        company = self.repository.get_company_description("")

        self.assertEqual(company, dict())

    def test_get_most_recents_revenue_success(self):
        expected_revenues = [{"value": 40}, {"value": 37.5}]
        self.mock_response_list_query_sql(expected_revenues)

        revenues = self.repository.get_most_recents_revenue("012345")

        self.assertEqual(revenues, expected_revenues)

    def test_get_most_recents_revenue_with_no_valid_id(self):

        revenues = self.repository.get_most_recents_revenue("")

        self.assertEqual(revenues, [])

    def test_get_most_recents_revenue_fail(self):
        self.repository.session.execute.side_effect = Exception("error")

        revenues = self.repository.get_most_recents_revenue("0123456")

        self.assertEqual(revenues, [])

    def test_get_company_description_fail(self):
        self.repository.session.execute.side_effect = Exception("error")

        with self.assertRaises(Exception) as context:
            self.repository.get_company_description("0123456")

        self.assertEqual(str(context.exception), "error")

    def test_get_metric_by_scenario_without_filters(self):
        alias = "revenue"
        company = self.company.copy()
        company[alias] = self.scenarios["actuals_revenue"]
        self.mock_response_list_query_sql([company])

        response = self.repository.get_metric_by_scenario(
            "Actuals", "Revenue", alias, "0123456", need_all=True
        )

        self.assertEqual(response, [company])

    def test_get_metric_by_scenario_with_filters(self):
        alias = "revenue"
        filters = {"sector": "Computer Hardware"}
        company = self.company.copy()
        company[alias] = self.scenarios["actuals_revenue"]
        self.mock_response_list_query_sql([company])

        response = self.repository.get_metric_by_scenario(
            "Actuals", "Revenue", alias, "0123456", need_all=True, filters=filters
        )

        self.assertEqual(response, [company])

    def test_get_metric_by_scenario_should_fail(self):
        self.repository.session.execute.side_effect = Exception("error")

        with self.assertRaises(Exception) as context:
            self.repository.get_metric_by_scenario(
                "Actuals", "Revenue", "revenue", "0123456", need_all=True
            )

        self.assertEqual(str(context.exception), "error")

    def test_get_base_metrics(self):
        company = self.company.copy()
        company.update(self.scenarios)
        data = {company["id"]: company}
        self.mock_response_list_query_sql([company])
        self.mock_base_metric_results(data)

        response = self.repository.get_base_metrics(
            2020, True, "0123456", True, True, inves_profile_name=[]
        )

        self.assertEqual(response, data)
