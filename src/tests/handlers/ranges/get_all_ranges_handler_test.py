import json
from unittest import TestCase, mock

from src.tests.data.data_reader import read
import src.handlers.ranges.get_all_ranges_handler as service_handler
from src.handlers.ranges.get_all_ranges_handler import handler, get_max_count


class TestGetAllRangesHandler(TestCase):
    def setUp(self):
        self.ranges = read("sample_response_ranges.json")
        self.event = read("sample_event_ranges.json")

    def test_get_max_count_when_limit_is_valid_string_number_return_string_value_as_int(
        self,
    ):

        max_count_result = get_max_count("10")

        self.assertEqual(max_count_result, 10)

    def test_get_max_count_when_limit_is_not_valid_string_number_return_none(self):

        max_count_result = get_max_count("test")

        self.assertIsNone(max_count_result)

    @mock.patch("ranges_service.RangesService.get_all_ranges")
    @mock.patch.object(service_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_all_ranges_handler_when_it_success_should_return_200_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_get_all_ranges,
    ):
        mock_verify_user_access.return_value = True
        mock_get_all_ranges.return_value = self.ranges

        ranges_response = handler(self.event, {})

        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(ranges_response.get("statusCode"), 200)
        self.assertEqual(ranges_response.get("body"), json.dumps(self.ranges))

    @mock.patch("ranges_service.RangesService.get_all_ranges")
    @mock.patch.object(service_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_all_ranges_handler_without_permissions_should_return_error_400_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_get_all_ranges,
    ):
        mock_verify_user_access.return_value = False

        response = handler(self.event, {})

        mock_get_all_ranges.assert_not_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(
            response.get("body"), json.dumps({"error": "No permissions to load ranges"})
        )

    @mock.patch("ranges_service.RangesService.get_all_ranges")
    @mock.patch.object(service_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_all_ranges_handler_fail_service_function_should_return_error_400_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_get_all_ranges,
    ):
        error_message = "Cannot get ranges"
        mock_verify_user_access.return_value = True
        mock_get_all_ranges.side_effect = Exception(error_message)

        ranges_response = handler(self.event, {})

        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(ranges_response.get("statusCode"), 400)
        self.assertEqual(
            ranges_response.get("body"), json.dumps({"error": error_message})
        )
