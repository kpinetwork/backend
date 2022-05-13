import json
from src.tests.data.data_reader import read
from unittest import TestCase, mock
from src.handlers.users.get_roles_handler import handler


class TestGetRolesHandler(TestCase):
    def setUp(self):
        self.event = read("sample_event_users.json")
        self.mock_users_instance = mock.Mock()

    @mock.patch("src.handlers.users.get_roles_handler.get_users_service_instance")
    def test_get_roles_handler_success_should_return_200_response(
        self, mock_get_users_instance
    ):
        expected_out = [{"name": "admin"}, {"name": "customer"}]
        mock_get_users_instance.return_value = self.mock_users_instance
        self.mock_users_instance.get_roles.return_value = expected_out

        response = handler(self.event, {})

        mock_get_users_instance.assert_called()
        self.assertEqual(response.get("statusCode"), 200)
        self.assertEqual(response.get("body"), json.dumps(expected_out, default=str))

    @mock.patch("src.handlers.users.get_roles_handler.get_users_service_instance")
    def test_get_roles_handler_fail_should_return_error_400_response(
        self, mock_get_users_instance
    ):
        error_message = "Cannot get roles"
        mock_get_users_instance.return_value = self.mock_users_instance
        self.mock_users_instance.get_roles.side_effect = Exception(error_message)

        response = handler(self.event, {})

        mock_get_users_instance.assert_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))
