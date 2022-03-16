import os
import json
from src.tests.data.data_reader import read
import src.handlers.comparison_vs_peers.download_comparison_vs_peers_handler as download_peers
from unittest import TestCase, mock
from src.handlers.comparison_vs_peers.download_comparison_vs_peers_handler import (
    handler,
)


def get_path(filename: str) -> str:
    root_path = os.path.abspath(".")
    return f"{root_path}/src/tests/data/{filename}"


class TestDownloadComparisonVsPeersHandler(TestCase):
    def setUp(self):
        self.username = "user@email.com"
        self.comparison_vs_peers = read("sample_comparison_vs_peers.json")
        self.event = read("sample_event_company.json")

    @mock.patch.object(download_peers, "get_comparison_vs_peers")
    @mock.patch.object(download_peers, "file_path", return_value=get_path("data.csv"))
    def test_download_comparison_vs_peers_handler_success_should_return_200_response(
        self, mock_file_path, mock_get_comparison_vs_peers
    ):
        mock_get_comparison_vs_peers.return_value = self.comparison_vs_peers

        response = handler(self.event, {})

        file_data = response.get("body")

        mock_get_comparison_vs_peers.assert_called_with(self.event)
        self.assertEqual(response.get("statusCode"), 200)
        self.assertEqual(type(file_data), str)

    @mock.patch.object(download_peers, "get_comparison_vs_peers")
    @mock.patch.object(download_peers, "file_path", return_value=get_path("data.csv"))
    def test_download_comparison_vs_peers_handler_fail_should_return_error_400_response(
        self, mock_file_path, mock_get_comparison_vs_peers
    ):
        error_message = "Cannot get comparison vs peers"
        mock_get_comparison_vs_peers.side_effect = Exception(error_message)

        response = handler(self.event, {})

        mock_get_comparison_vs_peers.assert_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))
