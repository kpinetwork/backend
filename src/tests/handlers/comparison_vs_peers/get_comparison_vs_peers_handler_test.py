import json
from src.tests.data.data_reader import read
from unittest import TestCase, mock
from src.handlers.comparison_vs_peers.get_comparison_vs_peers_handler import handler


class TestComparisonVsPeersHandler(TestCase):
    def setUp(self):
        self.username = "user@email.com"
        self.comparison_vs_peers = read("sample_company_report.json")
        self.event = read("sample_event_company.json")

    @mock.patch("comparison_vs_peers.ComparisonvsPeersService.get_peers_comparison")
    @mock.patch(
        "comparison_vs_peers.get_comparison_vs_peers_handler.get_username_from_user_id"
    )
    @mock.patch("company_anonymization.CompanyAnonymization.set_company_permissions")
    @mock.patch(
        "comparison_vs_peers.get_comparison_vs_peers_handler.get_user_details_service_instance"
    )
    @mock.patch(
        "comparison_vs_peers.get_comparison_vs_peers_handler.verify_user_access"
    )
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_comparison_vs_peers_handler_success_should_return_200_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_get_user_service_instance,
        mock_set_company_permissions,
        mock_get_username_from_user_id,
        mock_get_peers_comparison,
    ):
        mock_get_user_service_instance.return_value = object()
        mock_verify_user_access.return_value = True
        mock_get_username_from_user_id.return_value = self.username
        mock_get_peers_comparison.return_value = self.comparison_vs_peers

        response = handler(self.event, {})

        mock_get_peers_comparison.assert_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        mock_set_company_permissions.assert_called_with(self.username)
        self.assertEqual(response.get("statusCode"), 200)
        self.assertEqual(
            response.get("body"), json.dumps(self.comparison_vs_peers, default=str)
        )

    @mock.patch("comparison_vs_peers.ComparisonvsPeersService.get_peers_comparison")
    @mock.patch(
        "comparison_vs_peers.get_comparison_vs_peers_handler.get_username_from_user_id"
    )
    @mock.patch("company_anonymization.CompanyAnonymization.set_company_permissions")
    @mock.patch(
        "comparison_vs_peers.get_comparison_vs_peers_handler.get_user_details_service_instance"
    )
    @mock.patch(
        "comparison_vs_peers.get_comparison_vs_peers_handler.verify_user_access"
    )
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_comparison_vs_peers_handler_fail_should_return_error_400_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_get_user_service_instance,
        mock_set_company_permissions,
        mock_get_username_from_user_id,
        mock_get_peers_comparison,
    ):
        error_message = "Cannot get comparison vs peers"
        mock_get_peers_comparison.side_effect = Exception(error_message)
        mock_get_user_service_instance.return_value = object()
        mock_verify_user_access.return_value = True
        mock_get_username_from_user_id.return_value = self.username

        response = handler(self.event, {})

        mock_get_peers_comparison.assert_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        mock_set_company_permissions.assert_called_with(self.username)
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))
