import logging
from unittest import TestCase
from unittest.mock import Mock
from src.service.users.users_service import (
    UsersService,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestUsersService(TestCase):
    def setUp(self):
        self.users = {
            "Users": [
                {
                    "Username": "01",
                    "Attributes": [{"Name": "email", "Value": "user@email.com"}],
                    "UserCreateDate": "",
                    "UserLastModifiedDate": "",
                    "Enabled": True,
                    "UserStatus": "CONFIRMED",
                }
            ]
        }

        self.admin_groups = {
            "Groups": [
                {
                    "GroupName": "Google",
                    "UserPoolId": "UserPoolId",
                    "Description": "Google group",
                    "RoleArn": "Arn",
                    "Precedence": 123,
                    "LastModifiedDate": "",
                    "CreationDate": "",
                },
                {
                    "GroupName": "env_customer_group",
                    "UserPoolId": "UserPoolId",
                    "Description": "Test group",
                    "RoleArn": "Arn",
                    "Precedence": 123,
                    "LastModifiedDate": "",
                    "CreationDate": "",
                },
            ],
            "NextToken": None,
        }
        self.groups = {
            "Groups": [
                {
                    "GroupName": "default_Google",
                    "Description": "Group for google users",
                },
                {"GroupName": "env_customer_group", "Description": "Test group"},
            ]
        }
        self.mock_client = Mock()
        self.mock_response_user = Mock()
        self.users_service_instance = UsersService(
            logger, self.mock_client, self.mock_response_user
        )

    def mock_list_users(self, response):
        attrs = {"list_users.return_value": response}
        self.mock_client.configure_mock(**attrs)

    def mock_admin_list_groups_for_user(self, response):
        attrs = {"admin_list_groups_for_user.return_value": response}
        self.mock_client.configure_mock(**attrs)

    def mock_list_groups(self, response):
        attrs = {"list_groups.return_value": response}
        self.mock_client.configure_mock(**attrs)

    def mock_process_role_results(self, response):
        attrs = {"process_role_results.return_value": response}
        self.mock_response_user.configure_mock(**attrs)

    def mock_process_user_roles(self, response):
        attrs = {"process_user_roles.return_value": response}
        self.mock_response_user.configure_mock(**attrs)

    def test_set_users_groups(self):
        user = {"username": "01", "email": "user@email.com", "roles": []}
        roles = ["customer"]
        self.mock_admin_list_groups_for_user(self.admin_groups)
        self.mock_process_user_roles(roles)

        self.users_service_instance.set_users_groups([user], "userPoolId")

        self.assertEqual(user.get("roles"), roles)

    def test_get_users_success(self):
        user_result = [
            {"username": "01", "email": "user@email.com", "roles": ["customer"]}
        ]
        self.mock_list_users(self.users)
        self.mock_admin_list_groups_for_user(self.admin_groups)
        self.mock_process_user_roles(["customer"])
        self.mock_response_user.proccess_users.return_value = user_result
        expected_result = {"users": user_result, "token": None}

        get_users_out = self.users_service_instance.get_users("userPoolId", token="end")

        self.assertEqual(get_users_out, expected_result)

    def test_get_users_without_groups_should_return_empty_list(self):
        self.mock_list_users({"Users": []})
        self.mock_admin_list_groups_for_user({"Groups": []})
        self.mock_response_user.proccess_users.return_value = []

        get_roles_out = self.users_service_instance.get_users("userPoolId")

        self.assertEqual(get_roles_out, {"users": [], "token": None})

    def test_get_roles_success(self):
        self.mock_list_groups(self.groups)
        expected_result = [{"name": "customer", "description": "Test group"}]
        self.mock_process_role_results(expected_result)

        get_roles_out = self.users_service_instance.get_roles("userPoolId")

        self.assertEqual(get_roles_out, expected_result)

    def test_get_roles_without_groups_should_return_empty_list(self):
        self.mock_list_groups({"Groups": []})
        self.mock_process_role_results([])

        get_roles_out = self.users_service_instance.get_roles("userPoolId")

        self.assertEqual(get_roles_out, [])
