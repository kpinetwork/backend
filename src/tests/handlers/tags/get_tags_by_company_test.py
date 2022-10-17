import json

from src.tests.data.data_reader import read
from unittest import TestCase, mock
from src.handlers.tags.get_tags_by_company_handler import handler
import src.handlers.tags.get_tags_by_company_handler as get_tags_by_company_handler


class TestGetTagsByCompanyHandler(TestCase):
    def setUp(self):
        self.tags = read("sample_response_tags.json")
        self.event = read("sample_event_tags.json")

    @mock.patch("tags_service.TagsService.get_tags_by_company")
    @mock.patch.object(get_tags_by_company_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_tags_by_company_handler_success_should_return_200_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_get_tags_by_company,
    ):
        mock_verify_user_access.return_value = True
        mock_get_tags_by_company.return_value = self.tags.get("tags")

        response = handler(self.event, {})

        mock_get_tags_by_company.assert_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 200)
        self.assertEqual(
            response.get("body"), json.dumps(self.tags.get("tags"), default=str)
        )

    @mock.patch("tags_service.TagsService.get_tags_by_company")
    @mock.patch.object(get_tags_by_company_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_tags_by_company_handler_fail_without_permissions_should_return_error_400_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_get_tags_by_company,
    ):
        mock_verify_user_access.return_value = False

        response = handler(self.event, {})

        mock_get_tags_by_company.assert_not_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(
            response.get("body"), json.dumps({"error": "No permissions to load tags"})
        )

    @mock.patch("tags_service.TagsService.get_tags_by_company")
    @mock.patch.object(get_tags_by_company_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_tags_by_company_handler_fail_without_company_id_should_return_error_400_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_get_tags_by_company,
    ):
        mock_verify_user_access.return_value = True
        event = self.event.copy()
        event.update({"pathParameters": {}})

        response = handler(event, {})

        mock_get_tags_by_company.assert_not_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(
            response.get("body"), json.dumps({"error": "No data provided"})
        )
