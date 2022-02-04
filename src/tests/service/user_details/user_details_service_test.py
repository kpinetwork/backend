import logging
from unittest import TestCase
from unittest.mock import Mock
from src.service.user_details.user_details_service import (
    UserDetailsService,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestUsersService(TestCase):
    def setUp(self):
        self.mock_client = Mock()
        self.mock_response_user = Mock()
        self.users_service_instance = UserDetailsService(
            logger, self.mock_client, self.mock_response_user
        )
        self.user = {
            "Username": "000_test@email.com",
            "Attributes": [{"Name": "email", "Value": "test@email.com"}],
            "UserCreateDate": "",
            "Enabled": True,
            "UserStatus": "CONFIRMED",
        }

    def mock_admin_get_user(self, response):
        attrs = {"admin_get_user.return_value": response}
        self.mock_client.configure_mock(**attrs)

    def mock_admin_list_groups_for_user(self, response):
        attrs = {"admin_list_groups_for_user.return_value": response}
        self.mock_client.configure_mock(**attrs)

    def mock_process_user_roles(self, response):
        attrs = {"process_user_roles.return_value": response}
        self.mock_response_user.configure_mock(**attrs)

    def mock_process_user_info(self, response):
        attrs = {"process_user_info.return_value": response}
        self.mock_response_user.configure_mock(**attrs)

    def test_get_user_roles_with_valid_args_should_return_complete_info(self):
        expected_out = ["customer"]
        self.mock_process_user_roles(expected_out)
        self.mock_admin_list_groups_for_user({"Groups": [{"GroupName": "customer"}]})

        user_roles_out = self.users_service_instance.get_user_roles(
            "test@email.com", "pool_id"
        )

        self.assertEqual(user_roles_out, expected_out)

    def test_get_user_roles_with_invalid_args_should_return_exception(self):
        self.mock_client.admin_list_groups_for_user.side_effect = Exception(
            "Parameter validation failed"
        )
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.users_service_instance.get_user_roles("", None)
            )

            self.assertTrue("Parameter validation failed" in context.exception)
            self.assertEqual(exception, Exception)

    def test_get_user_with_valid_args_should_return_complete_info(self):
        roles = ["customer"]
        user_info = {
            "id": self.user["Username"],
            "email": "test@email.com",
            "status": "Active",
            "created_at": self.user.get("UserCreateDate"),
        }
        self.mock_process_user_roles(roles)
        self.mock_admin_list_groups_for_user({"Groups": [{"GroupName": "customer"}]})
        self.mock_process_user_info(user_info)
        self.mock_admin_get_user(self.user)

        user_out = self.users_service_instance.get_user("pool_id", "test@email.com")
        user_info["roles"] = roles

        self.assertEqual(user_out, user_info)

    def test_get_user_with_invalid_args_should_return_exception(self):
        self.mock_client.admin_get_user.side_effect = Exception(
            "Parameter validation failed"
        )
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.users_service_instance.get_user("pool_id", None)
            )

            self.assertTrue("Parameter validation failed" in context.exception)
            self.assertEqual(exception, Exception)

    def test_get_user_details_with_valid_args_should_return_not_empty_data(self):
        roles = ["customer"]
        user_info = {
            "id": self.user["Username"],
            "email": "test@email.com",
            "status": "Active",
            "created_at": self.user.get("UserCreateDate"),
            "roles": roles,
        }
        expected_user = {"user": user_info, "permissions": []}
        self.mock_process_user_roles(roles)
        self.mock_admin_list_groups_for_user({"Groups": [{"GroupName": "customer"}]})
        self.mock_process_user_info(user_info)
        self.mock_admin_get_user(self.user)

        user_out = self.users_service_instance.get_user_details(
            "pool_id", "test@email.com"
        )

        self.assertEqual(user_out, expected_user)
