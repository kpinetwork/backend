# test src.service.scenarios.delete_scenarios_service functions
import logging
from unittest import TestCase
from unittest.mock import Mock
from src.service.scenarios.delete_scenarios_service import DeleteScenariosService

logger = logging.getLogger()
logger.setLevel(logging.INFO)

company_id = "123"
scenarios = [
    {"name": "Budget", "year": "2020", "metric": "Revenue", "value": 10},
    {"name": "Budget", "year": "2020", "metric": "Ebitda", "value": 11},
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

    def test_delete_scenarios_from_details(self):
        expected_result = 2
        scenarios_deleted = self.delete_scenarios_service.delete_scenarios(
            company_id, scenarios, False
        )

        self.assertEqual(expected_result, scenarios_deleted)

    def test_delete_scenarios(self):
        expected_result = 2
        scenarios_deleted = self.delete_scenarios_service.delete_scenarios(
            company_id, scenarios_from_details, True
        )

        self.assertEqual(expected_result, scenarios_deleted)

    def test_delete_currency_handle_exception(self):
        self.mock_session.execute.side_effect = Exception("Error")
        result = self.delete_scenarios_service.delete_currency("123")

        self.assertFalse(result)

    def test_delete_scenario_metric_handle_exception_when_currency_is_no_deleted(self):
        self.mock_session.execute.side_effect = Exception("Error")
        result = self.delete_scenarios_service.delete_scenario_metric("123", "456")

        self.assertFalse(result)

    def test_delete_scenario_metric_handle_exception_when_currency_is_deleted(self):
        self.mock_session.execute.side_effect = Exception("Error")
        mock_currency_is_deleted = True
        self.delete_scenarios_service.delete_currency = Mock(
            return_value=mock_currency_is_deleted
        )

        result = self.delete_scenarios_service.delete_scenario_metric("123", "456")

        self.assertFalse(result)

    def test_delete_metric_handle_exception_when_scenario_metric_is_not_deleted(self):
        self.mock_session.execute.side_effect = Exception("Error")
        mock_scenario_metric_is_deleted = False
        self.delete_scenarios_service.delete_scenario_metric = Mock(
            return_value=mock_scenario_metric_is_deleted
        )
        result = self.delete_scenarios_service.delete_metric("123", "456")

        self.assertFalse(result)

    def test_delete_metric_handle_exception_when_scenario_metric_is_deleted(self):
        self.mock_session.execute.side_effect = Exception("Error")
        mock_scenario_metric_is_deleted = True
        self.delete_scenarios_service.delete_scenario_metric = Mock(
            return_value=mock_scenario_metric_is_deleted
        )
        result = self.delete_scenarios_service.delete_metric("123", "456")

        self.assertFalse(result)

    def test_delete_scenario_handle_exception(self):
        self.mock_session.execute.side_effect = Exception("Error")
        data = scenarios[0]
        result = self.delete_scenarios_service.delete_scenario(
            data.get("name"),
            data.get("year"),
            company_id,
            data.get("metric"),
            data.get("value"),
        )

        self.assertFalse(result)

    def test_delete_scenario_from_details_handle_exception(self):
        self.mock_session.execute.side_effect = Exception("Error")
        data = scenarios_from_details[0]
        result = self.delete_scenarios_service.delete_scenario_from_details(
            data.get("scenario_id"), data.get("metric_id")
        )

        self.assertFalse(result)

    def test_scenario_is_in_scenario_metric_returns_false(self):
        self.mock_session.execute.side_effect = Exception("Error")
        result = self.delete_scenarios_service.scenario_is_in_scenario_metric("123")

        self.assertFalse(result)

    def test_delete_scenario_if_it_is_not_in_scenario_metric_and_handle_exception(self):
        self.mock_session.execute.side_effect = Exception("Error")
        mock_metric_is_deleted = True
        mock_is_scenario = False
        self.delete_scenarios_service.delete_metric = Mock(
            return_value=mock_metric_is_deleted
        )
        self.delete_scenarios_service.scenario_is_in_scenario_metric = Mock(
            return_value=mock_is_scenario
        )
        data = scenarios[0]
        result = self.delete_scenarios_service.delete_scenario(
            data.get("name"),
            data.get("year"),
            company_id,
            data.get("metric"),
            data.get("value"),
        )

        self.assertFalse(result)

    def test_delete_scenario_from_details_if_it_is_not_in_scenario_metric_and_handle_exception(
        self,
    ):
        self.mock_session.execute.side_effect = Exception("Error")
        mock_metric_is_deleted = True
        mock_is_scenario = False
        self.delete_scenarios_service.delete_metric = Mock(
            return_value=mock_metric_is_deleted
        )
        self.delete_scenarios_service.scenario_is_in_scenario_metric = Mock(
            return_value=mock_is_scenario
        )
        data = scenarios_from_details[0]
        result = self.delete_scenarios_service.delete_scenario_from_details(
            data.get("scenario_id"), data.get("metric_id")
        )

        self.assertFalse(result)

    def test_delete_scenario_when_it_can_be_deleted_return_true(
        self,
    ):
        mock_metric_is_deleted = True
        mock_is_scenario = False
        self.delete_scenarios_service.delete_metric = Mock(
            return_value=mock_metric_is_deleted
        )
        self.delete_scenarios_service.scenario_is_in_scenario_metric = Mock(
            return_value=mock_is_scenario
        )
        data = scenarios[0]
        result = self.delete_scenarios_service.delete_scenario(
            data.get("name"),
            data.get("year"),
            company_id,
            data.get("metric"),
            data.get("value"),
        )

        self.assertTrue(result)

    def test_delete_scenario_from_details_when_it_can_be_deleted_return_true(
        self,
    ):
        mock_metric_is_deleted = True
        mock_is_scenario = False
        self.delete_scenarios_service.delete_metric = Mock(
            return_value=mock_metric_is_deleted
        )
        self.delete_scenarios_service.scenario_is_in_scenario_metric = Mock(
            return_value=mock_is_scenario
        )
        data = scenarios_from_details[0]
        result = self.delete_scenarios_service.delete_scenario_from_details(
            data.get("scenario_id"), data.get("metric_id")
        )

        self.assertTrue(result)

    def test_scenario_is_in_scenario_metric_returns_False_when_query_fetch_all_is_empty(
        self,
    ):
        self.mock_session.execute.return_value = Mock(fetchall=Mock(return_value=[]))
        result = self.delete_scenarios_service.scenario_is_in_scenario_metric("123")

        self.assertFalse(result)
