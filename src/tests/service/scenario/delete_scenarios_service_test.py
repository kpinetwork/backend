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

    def test_delete_metric_handles_exception_return_False(self):
        self.mock_session.execute.side_effect = Exception("error")
        data = scenarios_from_details[0]
        result = self.delete_scenarios_service.delete_metric(
            data.get("scenario_id"), data.get("metric_id")
        )

        self.assertFalse(result)

    def test_delete_scenario_when_metric_was_deleted_and_scenario_does_not_have_metrics(
        self,
    ):
        self.mock_session.execute.return_value = Mock(fetchall=Mock(return_value=[]))
        result = self.delete_scenarios_service.delete_scenario("123", "456")

        self.assertTrue(result)

    def test_delete_scenario_success_when_metric_was_deleted_and_scenario_has_metrics(
        self,
    ):
        self.mock_session.execute.return_value = Mock(
            fetchall=Mock(return_value=[{"id": "2"}])
        )
        result = self.delete_scenarios_service.delete_scenario("123", "456")

        self.assertTrue(result)

    def test_delete_scenario_when_metric_was_deleted_and_fails_should_return_false(
        self,
    ):
        mock_metric_is_deleted = True
        mock_scenario_has_metric = False
        self.delete_scenarios_service.delete_metric = Mock(
            return_value=mock_metric_is_deleted
        )
        self.delete_scenarios_service.scenario_has_metrics = Mock(
            return_value=mock_scenario_has_metric
        )
        self.mock_session.execute.side_effect = Exception("error")
        result = self.delete_scenarios_service.delete_scenario("123", "456")

        self.assertFalse(result)

    def test_scenario_has_metrics_should_returns_false_query_result_is_empty(
        self,
    ):
        self.mock_session.execute.return_value = Mock(fetchall=Mock(return_value=[]))
        result = self.delete_scenarios_service.scenario_has_metrics("123")

        self.assertFalse(result)

    def test_scenario_has_metrics_fails_should_raise_exception(self):
        self.mock_session.execute.side_effect = Exception("error")
        result = self.delete_scenarios_service.scenario_has_metrics("123")

        self.assertFalse(result)

    def test_delete_scenarios_success_should_return_the_same_len(self):
        scenarios = [
            {"scenario_id": "1", "metric_id": "1"},
            {"scenario_id": "1", "metric_id": "2"},
        ]

        self.delete_scenarios_service.delete_scenario = Mock(return_value=True)

        deleted = self.delete_scenarios_service.delete_scenarios(scenarios)

        self.assertEqual(deleted, len(scenarios))
