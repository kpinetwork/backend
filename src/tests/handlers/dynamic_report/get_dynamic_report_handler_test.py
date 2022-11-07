import json
from unittest import TestCase, mock

from src.tests.data.data_reader import read
import src.handlers.dynamic_report.get_dynamic_report_handler as get_dynamic_report_handler
from src.handlers.dynamic_report.get_dynamic_report_handler import handler


class TestDynamicReportHandler(TestCase):
    def setUp(self):
        self.username = "user@email.com"
        self.dynamic_report = read("sample_dynamic.json")
        self.event = read("sample_event_dynamic_report.json")

    @mock.patch("dynamic_report.DynamicReport.get_dynamic_report")
    @mock.patch.object(get_dynamic_report_handler, "get_username_from_user_id")
    @mock.patch.object(get_dynamic_report_handler, "get_user_details_service_instance")
    @mock.patch.object(get_dynamic_report_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_dynamic_report_handler_when_is_successful_should_return_200_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_get_user_service_instance,
        mock_get_username_from_user_id,
        mock_dynamic_report,
    ):
        mock_get_user_service_instance.return_value = object()
        mock_verify_user_access.return_value = True
        mock_get_username_from_user_id.return_value = self.username
        mock_dynamic_report.return_value = self.dynamic_report

        response = handler(self.event, {})

        mock_dynamic_report.assert_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 200)
        self.assertEqual(
            response.get("body"), json.dumps(self.dynamic_report, default=str)
        )

    @mock.patch("dynamic_report.DynamicReport.get_dynamic_report")
    @mock.patch.object(get_dynamic_report_handler, "get_username_from_user_id")
    @mock.patch.object(get_dynamic_report_handler, "get_user_details_service_instance")
    @mock.patch.object(get_dynamic_report_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_dynamic_report_handler_when_fails_should_return_error_400_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_get_user_service_instance,
        mock_get_username_from_user_id,
        mock_dynamic_report,
    ):
        error_message = "Cannot get dynamic report"
        mock_dynamic_report.side_effect = Exception(error_message)
        mock_get_user_service_instance.return_value = object()
        mock_verify_user_access.return_value = True
        mock_get_username_from_user_id.return_value = self.username

        response = handler(self.event, {})

        mock_dynamic_report.assert_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))
