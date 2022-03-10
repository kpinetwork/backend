from unittest import TestCase, mock
import logging
from unittest.mock import Mock
import src.service.user_details.get_user_details_service as functions

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestGetUserDetailsServiceTest(TestCase):
    def setUp(self):
        self.username = "user_id"
        self.user = {"UserAttributes": [{"Name": "email", "Value": self.username}]}
        self.mock_client = Mock()

    def config_mock_admin_list_groups_for_user(self, response):
        attrs = {"admin_list_groups_for_user.return_value": response}
        self.mock_client.configure_mock(**attrs)

    @mock.patch.object(functions, "boto3")
    def test_get_cognito_resource(self, mock_boto3):
        client = functions.get_cognito_resource()

        self.assertTrue(client is not None)
        mock_boto3.asserrt_called()

    def test_get_logger(self):
        logger = functions.get_logger()

        self.assertTrue(isinstance(logger, logging.Logger))

    @mock.patch.object(functions, "create_db_engine")
    @mock.patch.object(functions, "create_db_session")
    def test_get_session(self, mock_db_session, mock_db_engine):
        session = functions.get_session()

        self.assertTrue(session is not None)
        mock_db_session.assert_called()
        mock_db_engine.assert_called()

    @mock.patch.object(functions, "get_cognito_resource")
    @mock.patch.object(functions, "get_session")
    @mock.patch.object(functions, "PolicyManager")
    def test_get_user_details_service_instance(
        self, mock_policy_manager, mock_get_session, mock_get_cognito_resource
    ):
        functions.get_user_details_service_instance()

        mock_policy_manager.assert_called()
        mock_get_session.assert_called()
        mock_get_cognito_resource.assert_called()
