import json
from src.tests.data.data_reader import read
from unittest import TestCase, mock
import src.handlers.company_report_vs_peers.get_company_report_vs_peers_handler as report_handler
from src.handlers.company_report_vs_peers.get_company_report_vs_peers_handler import (
    handler,
)


class TestCompanyReportVsPeersHandler(TestCase):
    def setUp(self):
        self.username = "user@email.com"
        self.company_report = read("sample_company_report.json")
        self.event = read("sample_event_company.json")

    @mock.patch(
        "company_report_vs_peers_service.CompanyReportvsPeersService.get_company_report_vs_peers"
    )
    @mock.patch.object(report_handler, "get_username_from_user_id")
    @mock.patch("company_anonymization.CompanyAnonymization.set_company_permissions")
    @mock.patch.object(report_handler, "get_user_details_service_instance")
    @mock.patch.object(report_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_company_report_handler_success_should_return_200_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_get_user_service_instance,
        mock_set_company_permissions,
        mock_get_username_from_user_id,
        mock_get_company_report,
    ):
        mock_get_user_service_instance.return_value = object()
        mock_verify_user_access.return_value = True
        mock_get_username_from_user_id.return_value = self.username
        mock_get_company_report.return_value = self.company_report

        response = handler(self.event, {})

        mock_get_company_report.assert_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        mock_set_company_permissions.assert_called_with(self.username)
        self.assertEqual(response.get("statusCode"), 200)
        self.assertEqual(
            response.get("body"), json.dumps(self.company_report, default=str)
        )

    @mock.patch(
        "company_report_vs_peers_service.CompanyReportvsPeersService.get_company_report_vs_peers"
    )
    @mock.patch.object(report_handler, "get_username_from_user_id")
    @mock.patch("company_anonymization.CompanyAnonymization.set_company_permissions")
    @mock.patch.object(report_handler, "get_user_details_service_instance")
    @mock.patch.object(report_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_company_report_handler_fail_should_return_error_400_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_get_user_service_instance,
        mock_set_company_permissions,
        mock_get_username_from_user_id,
        mock_get_company_report,
    ):
        error_message = "Cannot get company report"
        mock_get_company_report.side_effect = Exception(error_message)
        mock_get_user_service_instance.return_value = object()
        mock_verify_user_access.return_value = True
        mock_get_username_from_user_id.return_value = self.username

        response = handler(self.event, {})

        mock_get_company_report.assert_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        mock_set_company_permissions.assert_called_with(self.username)
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))
