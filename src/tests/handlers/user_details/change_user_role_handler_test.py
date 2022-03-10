import json
from src.tests.data.data_reader import read
from unittest import TestCase, mock
from src.handlers.user_details.change_user_role_handler import handler
from user_details_service import UserDetailsService


class TestChangeUserRoleHandler(TestCase):
    def setUp(self):
        self.event = read("sample_event_user_role.json")
        self.users_service_instance = UserDetailsService(
            mock.Mock(),
            mock.Mock(),
            mock.Mock(),
            mock.Mock(),
            mock.Mock(),
            mock.Mock(),
            mock.Mock(),
        )

    @mock.patch("user_details_service.UserDetailsService.change_user_role")
    @mock.patch(
        "src.handlers.user_details.change_user_role_handler.get_user_details_service_instance"
    )
    def test_change_user_role_handler_success_should_return_200_response(
        self, mock_get_user_service_instance, mock_change_user_role
    ):
        mock_get_user_service_instance.return_value = self.users_service_instance
        mock_change_user_role.return_value = True

        response = handler(self.event, {})

        mock_change_user_role.assert_called()
        self.assertEqual(response.get("statusCode"), 200)
        self.assertEqual(
            response.get("body"), json.dumps({"modified": True}, default=str)
        )

    @mock.patch("user_details_service.UserDetailsService.change_user_role")
    @mock.patch(
        "src.handlers.user_details.change_user_role_handler.get_user_details_service_instance"
    )
    def test_change_user_role_handler_fail_should_return_error_400_response(
        self, mock_get_user_service_instance, mock_change_user_role
    ):
        error_message = "No roles data provided"
        mock_get_user_service_instance.return_value = self.users_service_instance

        response = handler({}, {})

        mock_change_user_role.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))
