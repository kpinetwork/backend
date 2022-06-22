import json
from src.tests.data.data_reader import read
from unittest import TestCase, mock
from src.handlers.edit_modify.edit_data_handler import handler
import src.handlers.edit_modify.edit_data_handler as edit_handler


class TestEditModifyDataHandler(TestCase):
    def setUp(self):
        self.event = read("sample_event_edit_modify.json")
        self.data = read("sample_response_edit_modify.json")

    @mock.patch("edit_service.EditModifyService.edit_modify_data")
    @mock.patch.object(edit_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_add_scenario_handler_success_should_return_200_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_edit_modify_data,
    ):

        mock_verify_user_access.return_value = True
        mock_edit_modify_data.return_value = self.data
        event = self.event.copy()
        event["body"] = json.dumps(event["body"])

        response = handler(event, {})

        mock_edit_modify_data.assert_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 200)
        self.assertTrue(json.loads(response.get("body")), self.data)

    @mock.patch("edit_service.EditModifyService.edit_modify_data")
    @mock.patch.object(edit_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_add_scenario_handler_without_permission_should_return_400_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_edit_modify_data,
    ):

        mock_verify_user_access.return_value = False

        response = handler(self.event, {})

        mock_edit_modify_data.assert_not_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(
            json.loads(response.get("body")),
            {"error": "No permissions to edit company and scenarios information"},
        )

    @mock.patch("edit_service.EditModifyService.edit_modify_data")
    @mock.patch.object(edit_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_add_scenario_handler_without_body_should_return_400_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_edit_modify_data,
    ):

        mock_verify_user_access.return_value = True

        response = handler(self.event, {})

        mock_edit_modify_data.assert_not_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(json.loads(response.get("body")), {"error": "Invalid body"})
