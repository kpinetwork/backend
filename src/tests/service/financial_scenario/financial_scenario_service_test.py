from unittest import TestCase
import logging
from unittest.mock import Mock
from src.service.financial_scenario.financial_scenario_service import (
    FinancialScenarioService,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestFinancialScenarioService(TestCase):
    def setUp(self):
        self.list_scenario = {"id": "1ad345fg", "name": "Test scenario"}
        self.scenario = {
            "id": "1ad345fg",
            "name": "Test scenario",
            "currency": "USD",
            "type": "Budget",
            "start_at": "2020-01-31",
            "end_at": "2020-12-31",
            "metric_name": "revenue",
            "metric_value": "20",
            "metric_type": "standard",
            "metric_data_type": "integer",
            "metric_start_at": "2020-01-31",
            "metric_end_at": "2020-12-31",
        }
        self.mock_session = Mock()
        self.mock_query_builder = Mock()
        self.mock_response_sql = Mock()
        self.financial_scenario_service_instance = FinancialScenarioService(
            self.mock_session, self.mock_query_builder, logger, self.mock_response_sql
        )
        return

    def mock_response_list_query_sql(self, response):
        attrs = {"process_query_list_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def mock_response_scenario_list_query_sql(self, response):
        attrs = {"process_scenarios_list_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def test_get_scenarios_success(self):
        self.mock_response_scenario_list_query_sql([self.scenario])

        get_scenarios_out = self.financial_scenario_service_instance.get_scenarios()

        self.assertEqual(get_scenarios_out, [self.scenario])
        self.financial_scenario_service_instance.session.execute.assert_called_once()

    def test_get_scenarios_failed(self):
        self.financial_scenario_service_instance.session.execute.side_effect = (
            Exception("error")
        )
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.financial_scenario_service_instance.get_scenarios()
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.financial_scenario_service_instance.session.execute.assert_called_once()

    def test_get_scenarios_return_empty_response(self):
        self.mock_response_scenario_list_query_sql([])

        get_scenarios_out = self.financial_scenario_service_instance.get_scenarios()

        self.assertEqual(get_scenarios_out, [])
        self.financial_scenario_service_instance.session.execute.assert_called_once()

    def test_get_company_scenarios_success_with_company_id_and_scenario_type(self):
        self.mock_response_list_query_sql([self.scenario])

        get_scenarios_out = (
            self.financial_scenario_service_instance.get_company_scenarios(
                "id", "Budget"
            )
        )

        self.assertEqual(get_scenarios_out, [self.scenario])
        self.financial_scenario_service_instance.session.execute.assert_called_once()

    def test_get_company_scenarios_failed(self):
        self.financial_scenario_service_instance.session.execute.side_effect = (
            Exception("error")
        )
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.financial_scenario_service_instance.get_company_scenarios(
                    self.scenario.get("id"), ""
                )
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.financial_scenario_service_instance.session.execute.assert_called_once()

    def test_get_company_scenarios_with_empty_id_return_empty_response(self):
        get_scenarios_out = (
            self.financial_scenario_service_instance.get_company_scenarios("", "type")
        )

        self.assertEqual(get_scenarios_out, [])
        self.financial_scenario_service_instance.session.execute.assert_not_called()

    def test_get_company_scenarios_with_empty_type_return_empty_response(self):
        self.mock_response_list_query_sql([self.scenario])

        get_scenarios_out = (
            self.financial_scenario_service_instance.get_company_scenarios("id", "")
        )

        self.assertEqual(get_scenarios_out, [self.scenario])
        self.financial_scenario_service_instance.session.execute.assert_called_once()

    def test_get_company_scenarios_with_empty_response_success(self):
        self.mock_response_list_query_sql([])

        get_scenarios_out = (
            self.financial_scenario_service_instance.get_company_scenarios(
                "id", "Budget"
            )
        )

        self.assertEqual(get_scenarios_out, [])
        self.financial_scenario_service_instance.session.execute.assert_called_once()

    def test_list_scenarios_with_empty_response_success(self):
        self.mock_response_list_query_sql([])

        scenarios_out = self.financial_scenario_service_instance.list_scenarios("1234")

        self.assertEqual(scenarios_out, [])
        self.financial_scenario_service_instance.session.execute.assert_called_once()

    def test_list_scenarios_success_with_company_id(self):
        self.mock_response_list_query_sql([self.scenario])

        scenarios_out = self.financial_scenario_service_instance.list_scenarios("1234")

        self.assertEqual(scenarios_out, [self.scenario])
        self.assertEqual(len(scenarios_out), len([self.scenario]))
        self.financial_scenario_service_instance.session.execute.assert_called_once()

    def test_list_scenario_with_empty_id(self):
        self.mock_response_list_query_sql([self.scenario])

        scenarios_out = self.financial_scenario_service_instance.list_scenarios("")

        self.assertEqual(scenarios_out, [self.scenario])
        self.assertEqual(len(scenarios_out), len([self.scenario]))
        self.financial_scenario_service_instance.session.execute.assert_called_once()

    def test_list_scenarios_failed(self):
        self.financial_scenario_service_instance.session.execute.side_effect = (
            Exception("error")
        )
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.financial_scenario_service_instance.list_scenarios("1234")
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.financial_scenario_service_instance.session.execute.assert_called_once()
