import json
from src.tests.data.data_reader import read
from unittest import TestCase, mock
import src.handlers.investment_date_report.get_investment_date_report_handler as report_handler
from src.handlers.investment_date_report.get_investment_date_report_handler import (
    handler,
)


class TestInvestmentDateReportHanlder(TestCase):
    def setUp(self):
        self.username = "user@email.com"
        self.investment_date_report = read("sample_investment_date_report.json")
        self.event = read("sample_event_investment_date_report.json")

    @mock.patch(
        "investment_date_report.InvestmentDateReport.get_peers_by_investment_date_report"
    )
    @mock.patch.object(report_handler, "get_username_from_user_id")
    @mock.patch.object(report_handler, "get_user_details_service_instance")
    @mock.patch.object(report_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_investment_date_report_handler_success_should_return_200_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_get_user_service_instance,
        mock_get_username_from_user_id,
        mock_investmemt_date_report,
    ):
        mock_get_user_service_instance.return_value = object()
        mock_verify_user_access.return_value = True
        mock_get_username_from_user_id.return_value = self.username
        mock_investmemt_date_report.return_value = self.investment_date_report

        response = handler(self.event, {})

        mock_investmemt_date_report.assert_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 200)
        self.assertEqual(
            response.get("body"), json.dumps(self.investment_date_report, default=str)
        )

    @mock.patch(
        "investment_date_report.InvestmentDateReport.get_peers_by_investment_date_report"
    )
    @mock.patch.object(report_handler, "get_username_from_user_id")
    @mock.patch.object(report_handler, "get_user_details_service_instance")
    @mock.patch.object(report_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_investment_date_report_handler_fail_should_return_error_400_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_get_user_service_instance,
        mock_get_username_from_user_id,
        mock_peers_by_investment_date,
    ):
        error_message = "Cannot get investment date report"
        mock_peers_by_investment_date.side_effect = Exception(error_message)
        mock_get_user_service_instance.return_value = object()
        mock_verify_user_access.return_value = True
        mock_get_username_from_user_id.return_value = self.username

        response = handler(self.event, {})

        mock_peers_by_investment_date.assert_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))
