import json
from unittest import TestCase, mock

from src.tests.data.data_reader import read
from src.handlers.tags.delete_tags_handler import handler
import src.handlers.tags.delete_tags_handler as update_handler


class TestDeleteTagsHandler(TestCase):
    def setUp(self):
        self.event = read("sample_event_delete_tags.json")

    @mock.patch("tags_service.TagsService.delete_tags")
    @mock.patch.object(update_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_delete_tags_handler_with_user_access_and_call_successful_should_return_200_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_delete_tags,
    ):
        mock_verify_user_access.return_value = True
        mock_delete_tags.return_value = True
        event = self.event.copy()
        event["body"] = json.dumps(event["body"])

        response = handler(event, {})

        mock_delete_tags.assert_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 200)
        self.assertEqual(response.get("body"), json.dumps({"deleted": True}))

    @mock.patch("tags_service.TagsService.delete_tags")
    @mock.patch.object(update_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_delete_tags_handler_without_user_access_should_return_error_400_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_delete_tags,
    ):
        error_message = "No permissions to delete tags"
        mock_verify_user_access.return_value = False
        event = self.event.copy()
        event["body"] = json.dumps(event["body"])

        response = handler(event, {})

        mock_delete_tags.assert_not_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))

    @mock.patch("tags_service.TagsService.delete_tags")
    @mock.patch.object(update_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_delete_tags_handler_without_valid_body_should_return_error_400_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_delete_tags,
    ):
        error_message = "Invalid body"
        mock_verify_user_access.return_value = True

        response = handler(self.event, {})

        mock_delete_tags.assert_not_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))
