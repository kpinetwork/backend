from src.tests.data.data_reader import read
import src.handlers.comparison_vs_peers.get_peers_data as get_peers
from unittest import TestCase, mock
from src.handlers.comparison_vs_peers.get_peers_data import get_comparison_vs_peers


class TestGetPeersData(TestCase):
    def setUp(self):
        self.username = "user@email.com"
        self.comparison_vs_peers = read("sample_comparison_vs_peers.json")
        self.event = read("sample_event_company.json")

    @mock.patch(
        "comparison_vs_peers_service.ComparisonvsPeersService.get_peers_comparison"
    )
    @mock.patch.object(get_peers, "get_username_from_user_id")
    @mock.patch.object(get_peers, "get_user_details_service_instance")
    @mock.patch.object(get_peers, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_comparison_vs_peers_success_should_return_200_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_get_user_service_instance,
        mock_get_username_from_user_id,
        mock_get_peers_comparison,
    ):
        mock_get_user_service_instance.return_value = object()
        mock_verify_user_access.return_value = True
        mock_get_username_from_user_id.return_value = self.username
        mock_get_peers_comparison.return_value = self.comparison_vs_peers

        response = get_comparison_vs_peers(self.event)

        mock_get_peers_comparison.assert_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response, self.comparison_vs_peers)

    @mock.patch(
        "comparison_vs_peers_service.ComparisonvsPeersService.get_peers_comparison"
    )
    @mock.patch.object(get_peers, "get_username_from_user_id")
    @mock.patch.object(get_peers, "get_user_details_service_instance")
    @mock.patch.object(get_peers, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_comparison_vs_peers_fail_should_return_error_400_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_get_user_service_instance,
        mock_get_username_from_user_id,
        mock_get_peers_comparison,
    ):
        error_message = "Cannot get comparison vs peers"
        mock_get_peers_comparison.side_effect = Exception(error_message)
        mock_get_user_service_instance.return_value = object()
        mock_verify_user_access.return_value = True
        mock_get_username_from_user_id.return_value = self.username

        with self.assertRaises(Exception) as context:
            get_comparison_vs_peers(self.event)

        mock_get_peers_comparison.assert_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(str(context.exception), error_message)
