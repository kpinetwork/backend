import json
from unittest import TestCase, mock

from src.tests.data.data_reader import read
import src.handlers.quarters_report.get_quarters_report_handler as get_quarters_report_handler
from src.handlers.quarters_report.get_quarters_report_handler import handler


class TestQuartersReportHandler(TestCase):
    def setUp(self):
        self.username = "user@email.com"
        self.quarters_report = read("sample_quarters_report.json")
        self.event = read("sample_event_quarters_report.json")

    @mock.patch("quarters_report.QuartersReport.get_quarters_peers")
    @mock.patch.object(get_quarters_report_handler, "get_username_from_user_id")
    @mock.patch.object(get_quarters_report_handler, "get_user_details_service_instance")
    @mock.patch.object(get_quarters_report_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_quarters_report_handler_when_is_successful_should_return_200_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_get_user_service_instance,
        mock_get_username_from_user_id,
        mock_quarters_report,
    ):
        mock_get_user_service_instance.return_value = object()
        mock_verify_user_access.return_value = True
        mock_get_username_from_user_id.return_value = self.username
        mock_quarters_report.return_value = self.quarters_report

        response = handler(self.event, {})

        mock_quarters_report.assert_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 200)
        self.assertEqual(
            response.get("body"), json.dumps(self.quarters_report, default=str)
        )

    @mock.patch("quarters_report.QuartersReport.get_quarters_peers")
    @mock.patch.object(get_quarters_report_handler, "get_username_from_user_id")
    @mock.patch.object(get_quarters_report_handler, "get_user_details_service_instance")
    @mock.patch.object(get_quarters_report_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_quarters_report_handler_when_fails_should_return_error_400_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_get_user_service_instance,
        mock_get_username_from_user_id,
        mock_quarters_report,
    ):
        error_message = "Cannot get dynamic report"
        mock_quarters_report.side_effect = Exception(error_message)
        mock_get_user_service_instance.return_value = object()
        mock_verify_user_access.return_value = True
        mock_get_username_from_user_id.return_value = self.username

        response = handler(self.event, {})

        mock_quarters_report.assert_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))
