import json
import src.tests.config_imports  # noqa
from src.tests.data.data_reader import read
from unittest import TestCase, mock
import src.handlers.by_metric_report.get_by_metric_report_handler as report_handler
from src.handlers.by_metric_report.get_by_metric_report_handler import (
    handler,
)


class TestGetByMetricReportHandler(TestCase):
    def setUp(self):
        self.username = "user@email.com"
        self.by_metric_report = read("sample_by_metric_report.json")
        self.event = read("sample_event_by_metric_report.json")

    @mock.patch("by_metric_report.ByMetricReport.get_by_metric_peers")
    @mock.patch.object(report_handler, "get_username_from_user_id")
    @mock.patch.object(report_handler, "get_user_details_service_instance")
    @mock.patch.object(report_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_by_metric_report_handler_success_should_return_200_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_get_user_service_instance,
        mock_get_username_from_user_id,
        mock_get_by_metric_peers,
    ):
        mock_get_user_service_instance.return_value = object()
        mock_verify_user_access.return_value = True
        mock_get_username_from_user_id.return_value = self.username
        mock_get_by_metric_peers.return_value = self.by_metric_report

        response = handler(self.event, {})

        mock_get_by_metric_peers.assert_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 200)
        self.assertEqual(
            response.get("body"), json.dumps(self.by_metric_report, default=str)
        )

    @mock.patch("by_metric_report.ByMetricReport.get_by_metric_peers")
    @mock.patch.object(report_handler, "get_username_from_user_id")
    @mock.patch.object(report_handler, "get_user_details_service_instance")
    @mock.patch.object(report_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_by_metric_report_handler_fail_should_return_error_400_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_get_user_service_instance,
        mock_get_username_from_user_id,
        mock_get_by_metric_peers,
    ):
        error_message = "Cannot get by metric report"
        mock_get_by_metric_peers.side_effect = Exception(error_message)
        mock_get_user_service_instance.return_value = object()
        mock_verify_user_access.return_value = True
        mock_get_username_from_user_id.return_value = self.username

        response = handler(self.event, {})

        mock_get_by_metric_peers.assert_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))
