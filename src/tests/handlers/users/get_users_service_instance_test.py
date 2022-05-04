import logging
from src.tests.data.data_reader import read
from unittest import TestCase, mock
from src.handlers.users.get_users_service_instance import get_users_service_instance
import src.handlers.users.get_users_service_instance as users_service_instance

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestGetUser(TestCase):
    def setUp(self):
        self.event = read("sample_event_users.json")

    @mock.patch.object(users_service_instance, "get_user_id_from_event")
    @mock.patch.object(users_service_instance, "verify_user_access")
    def test_get_users_service_instance_should_raise_an_exception(
        self, mock_verify_access, mock_get_user_id_from_event
    ):
        mock_get_user_id_from_event.return_value = "user_id"
        mock_verify_access.return_value = False

        with self.assertRaises(Exception) as context:
            get_users_service_instance(self.event, logger)

        self.assertEqual(str(context.exception), "No permissions to get data")

    @mock.patch.object(users_service_instance, "get_user_id_from_event")
    @mock.patch.object(users_service_instance, "verify_user_access")
    @mock.patch.object(users_service_instance, "boto3")
    def test_get_users_service_instance_should_return_a_valid_object(
        self, mock_boto3, mock_verify_access, mock_get_user_id_from_event
    ):
        mock_get_user_id_from_event.return_value = "user_id"
        mock_verify_access.return_value = True

        user_instance = get_users_service_instance(self.event, logger)

        mock_boto3.assert_not_called()
        self.assertTrue(isinstance(user_instance, users_service_instance.UsersService))
