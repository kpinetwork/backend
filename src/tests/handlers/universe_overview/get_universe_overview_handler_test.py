import json
from src.tests.data.data_reader import read
from unittest import TestCase, mock
from src.handlers.universe_overview.get_universe_overview_handler import handler


class TestGetUniverseOverviewHandler(TestCase):
    def setUp(self):
        self.universe_overview = read("sample_universe_overview.json")
        self.event = read("sample_event_company.json")

    @mock.patch(
        "universe_overview_service.UniverseOverviewService.get_universe_overview"
    )
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_comparison_vs_peers_handler_success_should_return_200_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_get_universe_overview,
    ):
        mock_get_universe_overview.return_value = self.universe_overview

        response = handler(self.event, {})

        mock_get_universe_overview.assert_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 200)
        self.assertEqual(
            response.get("body"), json.dumps(self.universe_overview, default=str)
        )

    @mock.patch(
        "universe_overview_service.UniverseOverviewService.get_universe_overview"
    )
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_comparison_vs_peers_handler_fail_should_return_error_400_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_get_universe_overview,
    ):
        error_message = "Cannot get universe overview"
        mock_get_universe_overview.side_effect = Exception(error_message)

        response = handler(self.event, {})

        mock_get_universe_overview.assert_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))
