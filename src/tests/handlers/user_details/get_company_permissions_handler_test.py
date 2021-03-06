import json
from src.tests.data.data_reader import read
from unittest import TestCase, mock
import src.handlers.user_details.get_company_permissions_handler as get_permissions_handler
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
    @mock.patch.object(get_permissions_handler, "get_user_details_service_instance")
    @mock.patch.object(get_permissions_handler, "verify_user_access")
    def test_get_user_company_permissions_handler_success_should_return_200_response(
        self,
        mock_verify_user_access,
        mock_get_user_service_instance,
        mock_get_user_company_permissions,
    ):
        permissions = self.user_details.get("permissions")
        mock_verify_user_access.return_value = True
        mock_get_user_service_instance.return_value = self.users_service_instance
        mock_get_user_company_permissions.return_value = permissions

        response = handler(self.event, {})

        mock_get_user_company_permissions.assert_called()
        self.assertEqual(response.get("statusCode"), 200)
        self.assertEqual(response.get("body"), json.dumps(permissions, default=str))

    @mock.patch("user_details_service.UserDetailsService.get_user_company_permissions")
    @mock.patch.object(get_permissions_handler, "get_user_details_service_instance")
    @mock.patch.object(get_permissions_handler, "verify_user_access")
    def test_get_user_company_permissions_handler_fail_should_return_no_username_error_400_response(
        self,
        mock_verify_user_access,
        mock_get_user_service_instance,
        mock_get_user_company_permissions,
    ):
        error_message = "No username provided"
        mock_verify_user_access.return_value = True
        mock_get_user_service_instance.return_value = self.users_service_instance

        response = handler(
            {"pathParameters": {}, "requestContext": self.event["requestContext"]}, {}
        )

        mock_get_user_company_permissions.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))

    @mock.patch("user_details_service.UserDetailsService.get_user_company_permissions")
    @mock.patch.object(get_permissions_handler, "verify_user_access")
    def test_get_user_company_permissions_handler_fail_should_return_error_400_response(
        self, mock_verify_user_access, mock_get_user_company_permissions
    ):
        error_message = "No permissions to get user comany permissions"
        mock_verify_user_access.return_value = False

        response = handler(self.event, {})

        mock_get_user_company_permissions.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))
