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
        self.mock_policy_manager = Mock()
        self.users_service_instance = UserDetailsService(
            logger, self.mock_client, self.mock_response_user, self.mock_policy_manager
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

    def mock_list_users(self, response):
        attrs = {"list_users.return_value": response}
        self.mock_client.configure_mock(**attrs)

    def mock_process_user_roles(self, response):
        attrs = {"process_user_roles.return_value": response}
        self.mock_response_user.configure_mock(**attrs)

    def mock_process_user_info(self, response):
        attrs = {"process_user_info.return_value": response}
        self.mock_response_user.configure_mock(**attrs)

    def mock_get_permissions_by_type(self, response):
        attrs = {"get_permissions_by_type.return_value": response}
        self.mock_policy_manager.configure_mock(**attrs)

    def mock_add_permission(self, response):
        attrs = {"add_policy.return_value": response}
        self.mock_policy_manager.configure_mock(**attrs)

    def mock_remove_permission(self, response):
        attrs = {"remove_policy.return_value": response}
        self.mock_policy_manager.configure_mock(**attrs)

    def test_get_username_by_email_with_valid_args_should_return_username(self):
        self.mock_list_users({"Users": [self.user]})

        username_out = self.users_service_instance.get_username_by_email(
            "test@email.com", "pool_id"
        )

        self.assertEqual(username_out, self.user["Username"])

    def test_get_username_by_email_with_invalid_args_should_return_exception(self):
        self.mock_client.list_users.side_effect = Exception(
            "Parameter validation failed"
        )
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.users_service_instance.get_username_by_email("", None)
            )

            self.assertTrue("Parameter validation failed" in context.exception)
            self.assertEqual(exception, Exception)

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
        self.mock_list_users({"Users": [self.user]})
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
        self.mock_get_permissions_by_type([])
        self.mock_list_users({"Users": [self.user]})
        self.mock_process_user_roles(roles)
        self.mock_admin_list_groups_for_user({"Groups": [{"GroupName": "customer"}]})
        self.mock_process_user_info(user_info)
        self.mock_admin_get_user(self.user)

        user_out = self.users_service_instance.get_user_details(
            "pool_id", "test@email.com"
        )

        self.assertEqual(user_out, expected_user)

    def test_get_company_permissions_with_valid_username_should_return_valid_response(
        self,
    ):
        expected_out = [{"id": "company_id", "permission": "read"}]
        self.mock_get_permissions_by_type(expected_out)

        company_permissions_out = (
            self.users_service_instance.get_user_company_permissions("test@email.com")
        )

        self.assertEqual(company_permissions_out, expected_out)

    def test_get_company_permissions_with_invalid_username_should_raise_exception(self):
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.users_service_instance.get_user_company_permissions("")
            )
            self.assertTrue("No valid username provided" in context.exception)
            self.assertEqual(exception, Exception)

    def test_add_company_permissions_with_no_permissions_in_company_should_return_true_values(
        self,
    ):
        self.mock_add_permission(True)
        expected_result = {"1": True, "2": True}

        out = self.users_service_instance.add_company_permissions(
            "test@email.com", ["1", "2"]
        )

        self.assertEqual(out, expected_result)

    def test_add_company_permissions_with_no_company_ids_should_empty_dict(self):
        out = self.users_service_instance.add_company_permissions("test@email.com", [])

        self.assertEqual(out, dict())

    def test_remove_company_permissions_with_no_permissions_in_company_should_return_true_values(
        self,
    ):
        self.mock_remove_permission(True)
        expected_result = {"1": True, "2": True}

        out = self.users_service_instance.remove_company_permissions(
            "test@email.com", ["1", "2"]
        )

        self.assertEqual(out, expected_result)

    def test_remove_company_permissions_with_no_company_ids_should_empty_dict(self):
        out = self.users_service_instance.remove_company_permissions(
            "test@email.com", []
        )

        self.assertEqual(out, dict())

    def test_assign_companies_permissions_should_return_dict(self):
        self.mock_add_permission(True)
        self.mock_remove_permission(True)
        expected_out = {"1": True, "2": True, "3": True}

        out = self.users_service_instance.assign_company_permissions(
            "test@email.com", {"1": True, "2": True, "3": False}
        )

        self.assertEqual(out, expected_out)

    def test_assign_company_permissions_with_no_valid_email_should_raise_exception(
        self,
    ):
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.users_service_instance.assign_company_permissions("", dict())
            )
            self.assertTrue("No valid username or companies data" in context.exception)
            self.assertEqual(exception, Exception)
