# test src.service.scenarios.delete_scenarios_service functions
import logging
from unittest import TestCase
from unittest.mock import Mock
from src.service.scenario.delete_scenarios_service import DeleteScenariosService

logger = logging.getLogger()
logger.setLevel(logging.INFO)

company_id = "123"
scenarios = [
    {"name": "Budget", "year": 2020, "metric": "Revenue", "value": 10},
    {"name": "Budget", "year": 2020, "metric": "Ebitda", "value": 11},
]
scenarios_from_details = [
    {
        "metric_id": "123",
        "scenario_id": "456",
    },
    {
        "metric_id": "123",
        "scenario_id": "789",
    },
]


class QueryFetchAll:
    def fetchall(self):
        return None


class QueryFetchAllHandleException:
    def fetchall(self):
        raise Exception("Error")


class DeleteScenariosServiceTest(TestCase):
    def setUp(self):
        self.mock_session = Mock()
        self.mock_query_builder = Mock()
        self.mock_logger = Mock()
        self.mock_response_sql = Mock()
        self.delete_scenarios_service = DeleteScenariosService(
            self.mock_session,
            self.mock_query_builder,
            self.mock_logger,
            self.mock_response_sql,
        )

    def test_delete_metric_of_scenario(self):
        expected_result = 2
        scenarios_deleted = self.delete_scenarios_service.delete_scenarios(
            company_id, scenarios_from_details, True
        )

        self.assertEqual(expected_result, scenarios_deleted)

    def test_delete_metric_when_from_details_is_False(self):
        expected_result = 2
        scenarios_deleted = self.delete_scenarios_service.delete_scenarios(
            company_id, scenarios, False
        )

        self.assertEqual(expected_result, scenarios_deleted)

    def test_delete_metric_handles_exception_return_False(self):
        self.mock_session.execute.side_effect = Exception("error")
        data = scenarios_from_details[0]
        result = self.delete_scenarios_service.delete_metric(
            data.get("scenario_id"), data.get("metric_id")
        )

        self.assertFalse(result)

    def test_delete_scenario_when_metric_deleted_is_True_and_is_in_scenario_metric_is_False(
        self,
    ):
        self.mock_session.execute.return_value = Mock(fetchall=Mock(return_value=[]))
        result = self.delete_scenarios_service.delete_scenario("123", "456")

        self.assertTrue(result)

    def test_delete_scenario_when_metric_is_deleted_handles_exception_return_False(
        self,
    ):
        mock_metric_is_deleted = True
        mock_scenario_has_metric = False
        self.delete_scenarios_service.delete_metric = Mock(
            return_value=mock_metric_is_deleted
        )
        self.delete_scenarios_service.scenario_is_in_scenario_metric = Mock(
            return_value=mock_scenario_has_metric
        )
        self.mock_session.execute.side_effect = Exception("error")
        result = self.delete_scenarios_service.delete_scenario("123", "456")

        self.assertFalse(result)

    def test_scenario_is_in_scenario_metric_returns_False_when_query_fetch_all_is_empty(
        self,
    ):
        self.mock_session.execute.return_value = Mock(fetchall=Mock(return_value=[]))
        result = self.delete_scenarios_service.scenario_is_in_scenario_metric("123")

        self.assertFalse(result)

    def test_scenario_is_in_scenario_metric_handle_exception_return_False(self):
        self.mock_session.execute.side_effect = Exception("error")
        result = self.delete_scenarios_service.scenario_is_in_scenario_metric("123")

        self.assertFalse(result)

    def test_get_metric_id_handles_exception_return_None(self):
        self.mock_session.execute.side_effect = Exception("error")
        period_id = "123"
        data = scenarios[0]
        result = self.delete_scenarios_service.get_metric_id(
            data.get("metric"), company_id, data.get("value"), period_id
        )

        self.assertIsNone(result)

    def test_get_scenario_id_handles_exception_return_None(self):
        self.mock_session.execute.side_effect = Exception("error")
        data = scenarios[0]
        result = self.delete_scenarios_service.get_scenario_id(
            data.get("name"), data.get("year"), company_id
        )

        self.assertIsNone(result)
