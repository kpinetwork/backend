import json
from src.tests.data.data_reader import read
from unittest import TestCase, mock
from src.handlers.tags.get_all_tags_handler import handler


class TestGetAllTagsandler(TestCase):
    def setUp(self):
        self.tags = read("sample_tags.json")
        self.event = read("sample_event.json")

    @mock.patch("tags_service.TagsService.get_all_tags")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_all_tags_handler_success_should_return_200_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_get_all_tags,
    ):
        mock_get_all_tags.return_value = self.tags

        response = handler(self.event, {})

        mock_get_all_tags.assert_called_with(1, 1)
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 200)
        self.assertEqual(response.get("body"), json.dumps(self.tags, default=str))

    @mock.patch("tags_service.TagsService.get_all_tags")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_all_tags_handler_fail_should_return_error_400_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_get_all_tags,
    ):
        error_message = "Cannot get tags"
        mock_get_all_tags.side_effect = Exception(error_message)

        response = handler(self.event, {})

        mock_get_all_tags.assert_called_with(1, 1)
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))
