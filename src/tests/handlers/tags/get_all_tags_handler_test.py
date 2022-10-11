import json
from unittest import TestCase, mock

from src.tests.data.data_reader import read
import src.handlers.tags.get_all_tags_handler as service_handler
from src.handlers.tags.get_all_tags_handler import handler, get_max_count


class TestGetAllTagsHandler(TestCase):
    def setUp(self):
        self.tags = read("sample_response_tags.json")
        self.event = read("sample_event_tags.json")

    def test_get_max_count_when_limit_is_valid_string_number_return_string_value_as_int(
        self,
    ):

        max_count_result = get_max_count("10")

        self.assertEqual(max_count_result, 10)

    def test_get_max_count_when_limit_is_not_valid_string_number_return_none(self):

        max_count_result = get_max_count("test")

        self.assertIsNone(max_count_result)

    @mock.patch("tags_service.TagsService.get_all_tags")
    @mock.patch.object(service_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_all_tags_handler_success_should_return_200_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_get_all_tags,
    ):
        mock_verify_user_access.return_value = True
        mock_get_all_tags.return_value = self.tags

        tags_response = handler(self.event, {})

        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(tags_response.get("statusCode"), 200)
        self.assertEqual(tags_response.get("body"), json.dumps(self.tags))

    @mock.patch("tags_service.TagsService.get_all_tags")
    @mock.patch.object(service_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_all_tags_handler_fail_should_return_error_400_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_get_all_tags,
    ):
        error_message = "Cannot get tags"
        mock_verify_user_access.return_value = True
        mock_get_all_tags.side_effect = Exception(error_message)

        tags_response = handler(self.event, {})

        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(tags_response.get("statusCode"), 400)
        self.assertEqual(
            tags_response.get("body"), json.dumps({"error": error_message})
        )
