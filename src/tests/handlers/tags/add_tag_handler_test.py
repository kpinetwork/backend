import json
from unittest import TestCase, mock

from src.tests.data.data_reader import read
from src.handlers.tags.add_tag_handler import handler
import src.handlers.tags.add_tag_handler as add_tag_handler


class TestAddTagHandler(TestCase):
    def setUp(self):
        self.tag = read("sample_response_add_tag.json")
        self.event = read("sample_event_tags.json")

    @mock.patch("tags_service.TagsService.add_tag")
    @mock.patch.object(add_tag_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_add_tag_handler_with_user_access_and_successfull_call_return_201_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_add_tag,
    ):
        mock_verify_user_access.return_value = True
        mock_add_tag.return_value = self.tag

        response = handler(self.event, {})

        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 201)
        self.assertEqual(
            response["body"], json.dumps({"tag": self.tag, "added": True}, default=str)
        )

    @mock.patch("tags_service.TagsService.add_tag")
    @mock.patch.object(add_tag_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_add_tag_handler_without_user_access_return_error_400_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_add_tag,
    ):
        mock_verify_user_access.return_value = False

        response = handler(self.event, {})

        mock_add_tag.assert_not_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(
            response.get("body"), json.dumps({"error": "No permissions to add tags"})
        )

    @mock.patch("tags_service.TagsService.add_tag")
    @mock.patch.object(add_tag_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_add_tag_handler_without_valid_body_should_should_return_error_400_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_add_tag,
    ):
        mock_verify_user_access.return_value = True
        event = self.event.copy()
        event.pop("body")

        response = handler(event, {})

        mock_add_tag.assert_not_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(
            response.get("body"), json.dumps({"error": "No data provided"})
        )
