import json
from src.tests.data.data_reader import read
from unittest import TestCase, mock
from src.handlers.scenario.add_scenario_handler import handler
import src.handlers.scenario.add_scenario_handler as add_scenario_handler


class TestAddCompanyScenarioHandler(TestCase):
    def setUp(self):
        self.event = read("sample_event_add_scenario.json")
        self.scenario = read("sample_response_add_scenario.json")

    @mock.patch("scenario_service.ScenarioService.add_company_scenario")
    @mock.patch.object(add_scenario_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_add_scenario_handler_success_should_return_200_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_add_company_scenario,
    ):

        mock_verify_user_access.return_value = True
        mock_add_company_scenario.return_value = self.scenario

        response = handler(self.event, {})

        mock_add_company_scenario.assert_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 200)
        self.assertTrue(json.loads(response.get("body")), self.scenario)

    @mock.patch("scenario_service.ScenarioService.add_company_scenario")
    @mock.patch.object(add_scenario_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_add_scenario_handler_without_permission_should_return_400_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_add_company_scenario,
    ):

        mock_verify_user_access.return_value = False

        response = handler(self.event, {})

        mock_add_company_scenario.assert_not_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(
            json.loads(response.get("body")),
            {"error": "No permissions to add scenarios"},
        )

    @mock.patch("scenario_service.ScenarioService.add_company_scenario")
    @mock.patch.object(add_scenario_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_add_scenario_handler_without_body_should_return_400_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_add_company_scenario,
    ):
        event = self.event.copy()
        event["body"] = ""
        mock_verify_user_access.return_value = True

        response = handler(event, {})

        mock_add_company_scenario.assert_not_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(json.loads(response.get("body")), {"error": "Invalid body"})
