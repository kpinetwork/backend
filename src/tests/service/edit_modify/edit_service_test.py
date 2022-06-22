from collections import defaultdict
import logging
from src.utils.query_builder import QuerySQLBuilder
from unittest import TestCase, mock
from unittest.mock import Mock
from src.service.edit_modify.edit_service import EditModifyService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestEditModifyService(TestCase):
    def setUp(self):

        self.mock_session = Mock()
        self.query_builder = QuerySQLBuilder()
        self.mock_response_sql = Mock()
        self.mock_scenario_service = Mock()
        self.edit_service = EditModifyService(
            self.mock_session, self.query_builder, self.mock_scenario_service, logger
        )
        self.company = {
            "id": "9c5d17a4-186c-461e-955b-dcafd6b45fa7",
            "description": {"name": "Test Company"},
            "scenarios": [
                {
                    "scenario_id": "073b57d5-d809-449e-8c6d-148a4f96bfb6",
                    "scenario": "Actuals",
                    "year": 2021,
                    "metric": "Revenue",
                    "metric_id": "1842fe06-0ece-4038-ab6a-00eb8260b524",
                    "value": 36.15,
                }
            ],
        }

        self.scenario = {
            "company_id": "9c5d17a4-186c-461e-955b-dcafd6b45fa7",
            "scenario": "Actuals",
            "year": 2018,
            "metric": "Revenue",
            "value": 45.6,
        }

    def get_scenario_added(
        self, scenario: dict, added: bool, error: str = None
    ) -> dict:
        scenario_added = defaultdict(list)
        response = {
            "scenario": f"{scenario['scenario']}-{scenario['year']}",
            "metric": f"{scenario['metric']}",
            "added": added,
        }
        if error:
            response["error"] = error

        scenario_added[scenario["company_id"]] = [response]
        return scenario_added

    def test_edit_data_success_should_return_true(self):
        company = self.company.copy()

        edited = self.edit_service.edit_data([company])

        self.assertTrue(edited)

    @mock.patch.object(EditModifyService, "_EditModifyService__get_companies_query")
    def test_edit_data_fail_should_return_false(self, mock_get_companies_query):
        company = self.company.copy()
        mock_get_companies_query.side_effect = Exception("error")

        edited = self.edit_service.edit_data([company])

        self.assertFalse(edited)

    @mock.patch.object(EditModifyService, "_EditModifyService__add_scenarios")
    def test_add_scenarios_fail_should_raise_exception(self, mock_add_scenarios):
        mock_add_scenarios.side_effect = Exception("error")

        scenarios = self.edit_service.add_data([])

        self.assertEqual(scenarios, dict())

    def test_add_scenario_success_should_return_added_true(self):
        scenario = self.scenario.copy()
        expected_scenario = self.get_scenario_added(scenario, True)

        scenarios = self.edit_service.add_data([scenario])

        self.assertEqual(scenarios, expected_scenario)

    def test_add_scenario_fail_should_return_added_false(self):
        scenario = self.scenario.copy()
        scenario["scenario"] = "Custom"
        message = "Invalid scenario name"
        expected_scenario = self.get_scenario_added(scenario, False, message)
        self.mock_scenario_service.add_company_scenario.side_effect = Exception(message)

        scenarios = self.edit_service.add_data([scenario])

        self.assertEqual(scenarios, expected_scenario)

    def test_edit_modify_data(self):
        scenario = self.scenario.copy()
        company = self.company.copy()
        expected_result = {
            "edited": True,
            "added": self.get_scenario_added(scenario, True),
        }

        response = self.edit_service.edit_modify_data(
            {"edit": [company], "add": [scenario]}
        )

        self.assertEqual(response, expected_result)
