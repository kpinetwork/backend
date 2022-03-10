import json
from src.tests.data.data_reader import read
from unittest import TestCase, mock
from src.handlers.user_details.get_company_permissions_handler import handler
from user_details_service import UserDetailsService


class TestGetUserCompanyPermissionsHandler(TestCase):
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

    @mock.patch("user_details_service.UserDetailsService.get_user_company_permissions")
    @mock.patch(
        "user_details.get_company_permissions_handler.get_user_details_service_instance"
    )
    def test_get_user_company_permissions_handler_success_should_return_200_response(
        self, mock_get_user_service_instance, mock_get_user_company_permissions
    ):
        permissions = self.user_details.get("permissions")
        mock_get_user_service_instance.return_value = self.users_service_instance
        mock_get_user_company_permissions.return_value = permissions

        response = handler(self.event, {})

        mock_get_user_company_permissions.assert_called()
        self.assertEqual(response.get("statusCode"), 200)
        self.assertEqual(response.get("body"), json.dumps(permissions, default=str))

    @mock.patch("user_details_service.UserDetailsService.get_user_company_permissions")
    @mock.patch(
        "user_details.get_company_permissions_handler.get_user_details_service_instance"
    )
    def test_get_user_company_permissions_handler_fail_should_return_no_username_error_400_response(
        self, mock_get_user_service_instance, mock_get_user_company_permissions
    ):
        error_message = "No username provided"
        mock_get_user_service_instance.return_value = self.users_service_instance

        response = handler({"pathParameters": {}}, {})

        mock_get_user_company_permissions.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))

    @mock.patch("user_details_service.UserDetailsService.get_user_company_permissions")
    @mock.patch(
        "user_details.get_company_permissions_handler.get_user_details_service_instance"
    )
    def test_get_user_company_permissions_handler_fail_should_return_error_400_response(
        self, mock_get_user_service_instance, mock_get_user_company_permissions
    ):
        error_message = "Cannot get user permissions"
        mock_get_user_service_instance.return_value = self.users_service_instance
        mock_get_user_company_permissions.side_effect = Exception(error_message)

        response = handler(self.event, {})

        mock_get_user_company_permissions.assert_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))
