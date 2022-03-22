from unittest import TestCase
from src.utils.response_user import ResponseUser
from parameterized import parameterized


class TestResponseBuilder(TestCase):
    def setUp(self):
        self.response_user_instance = ResponseUser()
        self.user = {
            "Username": "username",
            "Attributes": [
                {"Name": "email", "Value": "test@email.com"},
                {"Name": "sub", "Value": "username"},
            ],
            "UserCreateDate": "2022-01-06 13:15:54.212000-05:00",
            "Enabled": True,
        }

    @parameterized.expand(
        [["env_test_group", "test"], [None, ""], ["env_test", "env_test"]]
    )
    def test_get_role_name(self, group_name, expected_role):

        role = self.response_user_instance.get_role_name(group_name)

        self.assertEqual(role, expected_role)

    def test_process_user_info_with_not_valid_dict(self):
        user_info_out = self.response_user_instance.process_user_info(
            {}, "test@email.com"
        )

        self.assertEqual(user_info_out, dict())

    @parameterized.expand([[True, "Active"], [False, "Inactive"]])
    def test_process_user_info_with_different_enable_value(self, enabled, status):
        self.user["Enabled"] = enabled
        expected_user = {
            "id": "username",
            "email": "test@email.com",
            "status": status,
            "created_at": "2022-01-06 13:15:54.212000-05:00",
        }

        user_info_out = self.response_user_instance.process_user_info(
            self.user, "test@email.com"
        )

        self.assertEqual(user_info_out, expected_user)

    @parameterized.expand(
        [
            [None, []],
            [
                [{"GroupName": "customer", "Description": "Testing"}],
                [{"name": "customer", "description": "Testing"}],
            ],
            [
                [
                    {"GroupName": "customer", "Description": "Testing"},
                    {"GroupName": "Google_customer", "Description": ""},
                ],
                [{"name": "customer", "description": "Testing"}],
            ],
        ]
    )
    def test_process_role_results_with_no_valid_list_should_return_empty_list(
        self, groups, roles
    ):

        roles_out = self.response_user_instance.process_role_results(groups)

        self.assertEqual(roles_out, roles)

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

    def test_proccess_user(self):
        expected_user = {"username": "username", "email": "test@email.com", "roles": []}

        user = self.response_user_instance.proccess_user(self.user)

        self.assertEqual(user, expected_user)

    def test_proccess_users(self):
        expected_user = {"username": "username", "email": "test@email.com", "roles": []}

        users = self.response_user_instance.proccess_users([self.user])

        self.assertEqual(users, [expected_user])
