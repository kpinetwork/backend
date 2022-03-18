from unittest import TestCase, mock
import logging
from unittest.mock import Mock
import src.utils.verify_user_permissions as functions
from src.tests.data.data_reader import read

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestVerifyUserPermissionsFunctions(TestCase):
    def setUp(self):
        self.username = "user_id"
        self.user = {"UserAttributes": [{"Name": "email", "Value": self.username}]}
        self.mock_client = Mock()

    def config_mock_admin_list_groups_for_user(self, response):
        attrs = {"admin_list_groups_for_user.return_value": response}
        self.mock_client.configure_mock(**attrs)

    @mock.patch("src.utils.verify_user_permissions.boto3")
    def test_get_cognito_client(self, mock_boto3):

        client = functions.get_cognito_client()

        self.assertTrue(client is not None)
        mock_boto3.asserrt_called()

    def test_get_user_id_from_event(self):
        event = read("sample_event_user.json")
        expected_user = "user_id"

        user = functions.get_user_id_from_event(event)

        self.assertEqual(user, expected_user)

    def test_get_user_id_from_event_should_raise_exception(self):
        error_message = "No user found"

        with self.assertRaises(Exception) as context:
            functions.get_user_id_from_event(dict())

        self.assertEqual(str(context.exception), error_message)

    def test_get_email_from_user(self):
        result = functions.get_email_from_user(self.user)

        self.assertEqual(result, {"Name": "email", "Value": self.username})

    @mock.patch("src.utils.verify_user_permissions.get_email_from_user")
    @mock.patch("src.utils.verify_user_permissions.get_cognito_client")
    def test_get_username_from_user_id(
        self, mock_cognito_client, mock_get_email_from_user
    ):
        mock_get_email_from_user.return_value = {
            "Name": "email",
            "Value": self.username,
        }

        email = functions.get_username_from_user_id(self.username)

        self.assertEqual(email, self.username)
        mock_cognito_client.assert_called()
        mock_get_email_from_user.assert_called()

    def test_get_roles(self):
        groups = {"Groups": [{"GroupName": "customer"}]}
        self.config_mock_admin_list_groups_for_user(groups)

        response = functions.get_roles("id", "", self.mock_client)

        self.assertEqual(response, ["customer"])

    @mock.patch("src.utils.verify_user_permissions.get_cognito_client")
    @mock.patch("src.utils.verify_user_permissions.get_roles")
    def test_verify_user_access(self, mock_get_roles, mock_get_cognito_client):
        expected = False
        mock_get_roles.return_value = ["customer"]

        has_access = functions.verify_user_access(self.username)

        self.assertEqual(has_access, expected)
        mock_get_cognito_client.assert_called()
        mock_get_roles.assert_called()

    def test_verify_user_access_should_raise_exception(self):
        error_message = "Cannot verified permissions"

        with self.assertRaises(Exception) as context:
            functions.verify_user_access(None)

        self.assertEqual(str(context.exception), error_message)
