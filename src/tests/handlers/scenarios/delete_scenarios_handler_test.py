# test delete scenarios handler test
import json
from src.tests.data.data_reader import read
from unittest import TestCase, mock
from src.handlers.scenarios.delete_scenarios_handler import handler
import src.handlers.scenarios.delete_scenarios_handler as delete_scenario_handler


class TestDeleteScenariosHandler(TestCase):
    def setUp(self):
        self.event = read("sample_event_delete_scenarios_from_details.json")
        self.scenarios = read("sample_event_delete_scenarios.json")

    @mock.patch("delete_scenarios_service.DeleteScenariosService.delete_scenarios")
    @mock.patch.object(delete_scenario_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_delete_scenario_handler_success_should_return_200(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_delete_scenarios,
    ):
        mock_verify_user_access.return_value = True
        mock_delete_scenarios.return_value = 1

        response = handler(self.event, {})
        print(response)

        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["body"], json.dumps({"scenarios deleted": 1}))

    @mock.patch("delete_scenarios_service.DeleteScenariosService.delete_scenarios")
    @mock.patch.object(delete_scenario_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_delete_scenario_handler_without_permission_should_return_400(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_delete_scenarios,
    ):
        mock_verify_user_access.return_value = False

        response = handler(self.event, {})

        mock_delete_scenarios.assert_not_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(
            response["body"],
            json.dumps({"error": "No permissions to delete scenarios"}),
        )

    @mock.patch("delete_scenarios_service.DeleteScenariosService.delete_scenarios")
    @mock.patch.object(delete_scenario_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_delete_scenario_handler_without_body_should_return_400(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_delete_scenarios,
    ):
        event = self.event.copy()
        event["body"] = ""
        mock_verify_user_access.return_value = True

        response = handler(event, {})

        mock_delete_scenarios.assert_not_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(
            response["body"], json.dumps({"error": "No scenarios data provided"})
        )
