import json
from src.tests.data.data_reader import read
from unittest import TestCase, mock
import src.handlers.universe_overview.get_universe_overview_handler as get_overview_handler
from src.handlers.universe_overview.get_universe_overview_handler import handler


class TestGetUniverseOverviewHandler(TestCase):
    def setUp(self):
        self.username = "user@email.com"
        self.universe_overview = read("sample_universe_overview.json")
        self.event = read("sample_event_company.json")

    @mock.patch(
        "universe_overview_service.UniverseOverviewService.get_universe_overview"
    )
    @mock.patch.object(get_overview_handler, "get_username_from_user_id")
    @mock.patch("company_anonymization.CompanyAnonymization.set_company_permissions")
    @mock.patch.object(get_overview_handler, "get_user_details_service_instance")
    @mock.patch.object(get_overview_handler, "verify_user_access")
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
        mock_get_universe_overview,
    ):
        mock_get_user_service_instance.return_value = object()
        mock_verify_user_access.return_value = True
        mock_get_username_from_user_id.return_value = self.username
        mock_get_universe_overview.return_value = self.universe_overview

        response = handler(self.event, {})

        mock_get_universe_overview.assert_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        mock_set_company_permissions.assert_called_with(self.username)
        self.assertEqual(response.get("statusCode"), 200)
        self.assertEqual(
            response.get("body"), json.dumps(self.universe_overview, default=str)
        )

    @mock.patch(
        "universe_overview_service.UniverseOverviewService.get_universe_overview"
    )
    @mock.patch.object(get_overview_handler, "get_username_from_user_id")
    @mock.patch("company_anonymization.CompanyAnonymization.set_company_permissions")
    @mock.patch.object(get_overview_handler, "get_user_details_service_instance")
    @mock.patch.object(get_overview_handler, "verify_user_access")
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
        mock_get_universe_overview,
    ):
        error_message = "Cannot get universe overview"
        mock_get_universe_overview.side_effect = Exception(error_message)
        mock_get_user_service_instance.return_value = object()
        mock_verify_user_access.return_value = True
        mock_get_username_from_user_id.return_value = self.username

        response = handler(self.event, {})

        mock_get_universe_overview.assert_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        mock_set_company_permissions.assert_called_with(self.username)
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))
