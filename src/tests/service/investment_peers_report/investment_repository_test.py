from unittest import TestCase, mock
import logging
from unittest.mock import Mock
from src.service.investment_peers_report.investment_repository import (
    InvestmentRepository,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestInvestmentRepository(TestCase):
    def setUp(self):
        self.mock_session = Mock()
        self.mock_query_builder = Mock()
        self.mock_response_sql = Mock()
        self.mock_profile_range = Mock()
        self.repository = InvestmentRepository(
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
            "id": "0123456",
            "type": "Actuals",
            "scenario": "Actuals-2020",
            "metric": "Revenue",
            "value": 40,
        }

        self.metrics = {
            "actuals_revenue": 40,
            "actuals_ebitda": None,
            "prior_actuals_revenue": None,
            "prior_actuals_ebitda": None,
            "budget_revenue": None,
            "budget_ebitda": None,
        }
        self.investment = {"company_id": "0123456", "invest_year": 2020, "round": 1}

    def mock_response_query_sql(self, response):
        attrs = {"process_query_result.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def mock_response_list_query_sql(self, response):
        attrs = {"process_query_list_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def mock_base_metric_results(self, response):
        attrs = {"proccess_base_metrics_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def test_get_investments_success(self):
        expected_investments = {self.investment["company_id"]: self.investment}
        self.mock_response_list_query_sql([self.investment])

        investments = self.repository.get_investments()

        self.assertEqual(investments, expected_investments)

    def test_get_investments_should_fail(self):
        self.repository.session.execute.side_effect = Exception("error")

        investments = self.repository.get_investments()

        self.assertEqual(investments, dict())

    def test_get_scenarios_success(self):
        self.mock_response_list_query_sql([self.scenarios])

        scenarios = self.repository.get_scenarios(
            ["0123456"], [2020], {"size_cohort": ["$30-<50 million"]}
        )

        self.assertEqual(scenarios, [self.scenarios])

    def test_get_scenarios_should_fail(self):
        self.repository.session.execute.side_effect = Exception("error")

        with self.assertRaises(Exception) as context:
            self.repository.get_scenarios(
                ["0123456"], [2020], {"size_cohort": ["$30-<50 million"]}
            )

        self.assertEqual(str(context.exception), "error")

    def test_get_metric_with_no_valid_year(self):

        metric_data = self.repository.get_metric(self.scenarios, 2018)

        self.assertEqual(metric_data, dict())

    def test_get_metric_with_minor_year(self):
        expected_scenario = self.scenarios.copy()
        base_year = self.investment["invest_year"] + 1
        expected_scenario["prior_actuals_revenue"] = 40

        metric_data = self.repository.get_metric(self.scenarios, base_year)

        self.assertEqual(metric_data, expected_scenario)

    def test_get_metric_with_no_valid_name(self):
        scenario = self.scenarios.copy()
        scenario["metric"] = "Rule of 40"
        base_year = self.investment["invest_year"] + 1

        metric_data = self.repository.get_metric(scenario, base_year)

        self.assertEqual(metric_data, dict())

    @mock.patch.object(InvestmentRepository, "get_investments")
    def test_get_base_metrics_success(self, mock_get_investments):
        self.mock_response_list_query_sql([self.scenarios])
        invest = self.scenarios.copy()
        invest["actuals_revenue"] = self.scenarios["value"]
        mock_get_investments.return_value = {
            self.investment["company_id"]: self.investment
        }

        response = self.repository.get_base_metrics(0, sector=["Computer Hardware"])

        self.assertEqual(response, {invest["id"]: invest})
