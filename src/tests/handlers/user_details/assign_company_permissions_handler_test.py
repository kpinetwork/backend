import json
from src.tests.data.data_reader import read
from unittest import TestCase, mock
import src.handlers.user_details.assign_company_permissions_handler as assign_permissions_handler
from src.handlers.user_details.assign_company_permissions_handler import handler
from user_details_service import UserDetailsService


class TestAssignUserCompanyPermissionsHandler(TestCase):
    def setUp(self):
        self.event = read("sample_event_company_permissions.json")
        self.users_service_instance = UserDetailsService(
            mock.Mock(),
            mock.Mock(),
            mock.Mock(),
            mock.Mock(),
            mock.Mock(),
            mock.Mock(),
            mock.Mock(),
        )

    @mock.patch("user_details_service.UserDetailsService.assign_company_permissions")
    @mock.patch.object(assign_permissions_handler, "get_user_details_service_instance")
    def test_assign_user_company_permissions_handler_success_should_return_200_response(
        self, mock_get_user_service_instance, mock_assign_company_permissions
    ):
        data = json.loads(self.event.get("body"))
        expected_out = [data.get("companies")]
        mock_get_user_service_instance.return_value = self.users_service_instance
        mock_assign_company_permissions.return_value = expected_out

        response = handler(self.event, {})

        mock_assign_company_permissions.assert_called()
        self.assertEqual(response.get("statusCode"), 200)
        self.assertEqual(
            response.get("body"), json.dumps({"modified": expected_out}, default=str)
        )

    @mock.patch("user_details_service.UserDetailsService.assign_company_permissions")
    @mock.patch.object(assign_permissions_handler, "get_user_details_service_instance")
    def test_assign_company_permissions_handler_fail_should_return_no_username_error_400_response(
        self, mock_get_user_service_instance, mock_assign_company_permissions
    ):
        error_message = "No company data provided"
        mock_get_user_service_instance.return_value = self.users_service_instance

        response = handler({"pathParameters": {}}, {})

        mock_assign_company_permissions.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))

    @mock.patch("user_details_service.UserDetailsService.assign_company_permissions")
    @mock.patch.object(assign_permissions_handler, "get_user_details_service_instance")
    def test_assign_user_company_permissions_handler_fail_should_return_error_400_response(
        self, mock_get_user_service_instance, mock_assign_company_permissions
    ):
        error_message = "Cannot get user permissions"
        mock_get_user_service_instance.return_value = self.users_service_instance
        mock_assign_company_permissions.side_effect = Exception(error_message)

        response = handler(self.event, {})

        mock_assign_company_permissions.assert_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))
