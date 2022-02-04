from unittest import TestCase
from src.utils.response_user import ResponseUser


class TestResponseBuilder(TestCase):
    def setUp(self):
        self.response_user_instance = ResponseUser()
        self.user = {
            "Username": "username",
            "UserAttributes": [
                {"Name": "sub", "Value": "username"},
                {"Name": "email", "Value": "test@email.com"},
            ],
            "UserCreateDate": "2022-01-06 13:15:54.212000-05:00",
            "Enabled": True,
        }
        self.group = "env_test_group"

    def test_get_role_name_should_return_second_value(self):
        expected_role = "test"

        role = self.response_user_instance.get_role_name(self.group)

        self.assertEqual(role, expected_role)

    def test_get_role_name_none_should_return_empty_string(self):
        role = self.response_user_instance.get_role_name(None)

        self.assertEqual(role, "")

    def test_get_role_name_with_different_format_should_same_string(self):
        role = "env_test"
        role_out = self.response_user_instance.get_role_name(role)

        self.assertEqual(role_out, role)

    def test_process_user_info_with_not_valid_dict(self):
        user_info_out = self.response_user_instance.process_user_info(
            {}, "test@email.com"
        )

        self.assertEqual(user_info_out, dict())

    def test_process_user_info_with_enable_should_return_active_user(self):
        expected_user = {
            "id": "username",
            "email": "test@email.com",
            "status": "Active",
            "created_at": "2022-01-06 13:15:54.212000-05:00",
        }

        user_info_out = self.response_user_instance.process_user_info(
            self.user, "test@email.com"
        )

        self.assertEqual(user_info_out, expected_user)

    def test_process_user_info_without_enable_should_return_inactive_user(self):
        self.user["Enabled"] = False
        expected_user = {
            "id": "username",
            "email": "test@email.com",
            "status": "Inactive",
            "created_at": "2022-01-06 13:15:54.212000-05:00",
        }

        user_info_out = self.response_user_instance.process_user_info(
            self.user, "test@email.com"
        )

        self.assertEqual(user_info_out, expected_user)

    def test_process_role_results_with_no_valid_list_should_return_empty_list(self):

        roles_out = self.response_user_instance.process_role_results(None)

        self.assertEqual(roles_out, [])

    def test_process_role_results_with_no_google_groups_success(self):
        expected_out = [{"name": "customer", "description": "Testing"}]
        groups = [{"GroupName": "customer", "Description": "Testing"}]

        roles_out = self.response_user_instance.process_role_results(groups)

        self.assertEqual(roles_out, expected_out)

    def test_process_role_results_with_google_groups_should_return_less_records(self):
        expected_out = [{"name": "customer", "description": "Testing"}]
        groups = [
            {"GroupName": "customer", "Description": "Testing"},
            {"GroupName": "Google_customer", "Description": ""},
        ]

        roles_out = self.response_user_instance.process_role_results(groups)

        self.assertEqual(roles_out, expected_out)

    def test_process_user_roles_with_no_valid_list_should_return_empty_list(self):
        user_roles_out = self.response_user_instance.process_user_roles(None)

        self.assertEqual(user_roles_out, [])

    def test_process_user_roles_with_no_empty_list_should_return_not_empty_list(self):
        expected_out = ["customer"]
        groups = {
            "Groups": [{"GroupName": "customer"}, {"GroupName": "Google_customer"}]
        }

        user_roles_out = self.response_user_instance.process_user_roles(groups)

        self.assertEqual(user_roles_out, expected_out)
