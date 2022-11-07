import json
from unittest import TestCase, mock

from src.tests.data.data_reader import read
import src.handlers.ranges.get_ranges_by_metric_handler as ranges_handler
from src.handlers.ranges.get_ranges_by_metric_handler import handler


class TestGetRangesByMetricHandler(TestCase):
    def setUp(self):
        self.ranges = read("sample_response_ranges_by_metric.json")
        self.event = read("sample_event_ranges_by_metric.json")

    @mock.patch("ranges_service.RangesService.get_ranges_by_metric")
    @mock.patch.object(ranges_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_ranges_by_metric_handler_when_successful_should_return_200_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_get_ranges_by_metric,
    ):
        mock_verify_user_access.return_value = True
        mock_get_ranges_by_metric.return_value = self.ranges

        ranges_response = handler(self.event, {})

        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(ranges_response.get("statusCode"), 200)
        self.assertEqual(ranges_response.get("body"), json.dumps(self.ranges))

    @mock.patch("ranges_service.RangesService.get_ranges_by_metric")
    @mock.patch.object(ranges_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_ranges_by_metric_handler_without_permissions_should_return_error_400_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_get_ranges_by_metric,
    ):
        mock_verify_user_access.return_value = False

        response = handler(self.event, {})

        mock_get_ranges_by_metric.assert_not_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(
            response.get("body"), json.dumps({"error": "No permissions to load ranges"})
        )

    @mock.patch("ranges_service.RangesService.get_ranges_by_metric")
    @mock.patch.object(ranges_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_ranges_by_metric_handler_when_no_metric_provided_should_return_error_400_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_get_ranges_by_metric,
    ):
        error_message = "No metric provided"
        mock_verify_user_access.return_value = True

        event = self.event.copy()
        event["pathParameters"].pop("metric")
        ranges_response = handler(event, {})

        mock_get_ranges_by_metric.assert_not_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(ranges_response.get("statusCode"), 400)
        self.assertEqual(
            ranges_response.get("body"), json.dumps({"error": error_message})
        )
