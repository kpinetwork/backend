import json
from unittest import TestCase, mock

from src.tests.data.data_reader import read
import src.handlers.ranges.modify_ranges_handler as update_handler
from src.handlers.ranges.modify_ranges_handler import handler


class TestModifyRangesHandler(TestCase):
    def setUp(self):
        self.event = read("sample_event_modify_ranges.json")

    @mock.patch("ranges_service.RangesService.modify_ranges")
    @mock.patch.object(update_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_modify_ranges_handler_with_user_access_and_call_successful_should_return_200_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_modify_ranges,
    ):
        mock_verify_user_access.return_value = True
        mock_modify_ranges.return_value = True
        event = self.event.copy()
        event["body"] = json.dumps(event["body"])

        ranges_response = handler(event, {})

        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(ranges_response.get("statusCode"), 200)
        self.assertEqual(
            ranges_response.get("body"), json.dumps({"updated": True}, default=str)
        )

    @mock.patch("ranges_service.RangesService.modify_ranges")
    @mock.patch.object(update_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_modify_ranges_handler_without_user_access_should_return_error_400_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_modify_ranges,
    ):
        error_message = "No permissions to modify ranges"
        mock_verify_user_access.return_value = False
        event = self.event.copy()
        event["body"] = json.dumps(event["body"])

        response = handler(self.event, {})

        mock_modify_ranges.assert_not_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))

    @mock.patch("ranges_service.RangesService.modify_ranges")
    @mock.patch.object(update_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_modify_ranges_handler_without_valid_body_should_return_error_400_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_modify_ranges,
    ):
        error_message = "Invalid body"
        mock_verify_user_access.return_value = True

        ranges_response = handler(self.event, {})

        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(ranges_response.get("statusCode"), 400)
        self.assertEqual(
            ranges_response.get("body"), json.dumps({"error": error_message})
        )
