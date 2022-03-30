import json
from src.tests.data.data_reader import read
from unittest import TestCase, mock
import src.handlers.user_details.get_user_details_handler as get_user_handler
from src.handlers.user_details.get_user_details_handler import handler
from user_details_service import UserDetailsService


class TestGetUserDetailsHandler(TestCase):
    def setUp(self):
        self.user_details = read("sample_user.json")
        self.event = read("sample_event_user.json")
        self.users_service_instance = UserDetailsService(
            mock.Mock(),
            mock.Mock(),
            mock.Mock(),
            mock.Mock(),
            mock.Mock(),
            mock.Mock(),
            mock.Mock(),
        )

    @mock.patch("user_details_service.UserDetailsService.get_user_details")
    @mock.patch.object(get_user_handler, "get_user_details_service_instance")
    @mock.patch.object(get_user_handler, "verify_user_access")
    def test_get_user_details_handler_success_should_return_200_response(
        self,
        mock_verify_user_access,
        mock_get_user_service_instance,
        mock_get_user_details,
    ):
        mock_verify_user_access.return_value = True
        mock_get_user_service_instance.return_value = self.users_service_instance
        mock_get_user_details.return_value = self.user_details

        response = handler(self.event, {})

        mock_get_user_details.assert_called()
        self.assertEqual(response.get("statusCode"), 200)
        self.assertEqual(
            response.get("body"), json.dumps(self.user_details, default=str)
        )

    @mock.patch("user_details_service.UserDetailsService.get_user_details")
    @mock.patch.object(get_user_handler, "verify_user_access")
    def test_get_user_details_handler_fail_should_return_error_400_response(
        self, mock_verify_user_access, mock_get_user_details
    ):
        error_message = "No permissions to get user details"
        mock_verify_user_access.return_value = False
        mock_get_user_details.side_effect = Exception(error_message)

        response = handler(self.event, {})

        mock_get_user_details.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))
