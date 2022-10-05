import json
from src.tests.data.data_reader import read
from unittest import TestCase, mock
from src.handlers.tags.update_tags_handler import handler
import src.handlers.tags.update_tags_handler as update_handler


class TestGetAllTagsandler(TestCase):
    def setUp(self):
        self.event = read("sample_event_update_tag.json")

    @mock.patch("tags_service.TagsService.update_tags")
    @mock.patch.object(update_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_update_tags_handler_with_user_access_and_call_successful_should_return_200_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_update_tags,
    ):
        mock_verify_user_access.return_value = True
        mock_update_tags.return_value = True
        event = self.event.copy()
        event["body"] = json.dumps(event["body"])

        response = handler(event, {})

        mock_update_tags.assert_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 200)
        self.assertEqual(
            response.get("body"), json.dumps({"updated": True}, default=str)
        )

    @mock.patch("tags_service.TagsService.update_tags")
    @mock.patch.object(update_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_update_tags_handler_without_user_access_should_return_error_400_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_update_tags,
    ):
        error_message = "No permissions to update tags"
        mock_verify_user_access.return_value = False
        event = self.event.copy()
        event["body"] = json.dumps(event["body"])

        response = handler(event, {})

        mock_update_tags.assert_not_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))

    @mock.patch("tags_service.TagsService.update_tags")
    @mock.patch.object(update_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_update_tags_handler_without_valid_body_should_return_error_400_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_update_tags,
    ):
        error_message = "Invalid body"
        mock_verify_user_access.return_value = True

        response = handler(self.event, {})

        mock_update_tags.assert_not_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))
