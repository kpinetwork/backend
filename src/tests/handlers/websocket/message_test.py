from parameterized import parameterized
from src.tests.data.data_reader import read
from unittest import TestCase, mock
from src.handlers.websocket.message import handler, get_api_url


class TestWebsocketMessageRoute(TestCase):
    def setUp(self):
        self.event = read("sample_event_websocket.json")

    @parameterized.expand(
        [
            ["wss://api_id.amazon.com/stage", "https://api_id.amazon.com/stage"],
            ["api_id.amazon.com/demo", "api_id.amazon.com/demo"],
        ]
    )
    def test_get_api_url(self, invoke_url, api_url):

        response = get_api_url(invoke_url)

        self.assertEqual(response, api_url)

    @mock.patch("src.handlers.websocket.message.boto3")
    def test_handler_with_valid_data_should_return_success(self, mock_boto3):

        response = handler(self.event, {})

        mock_boto3.assert_not_called()
        self.assertEqual(response.get("statusCode"), 200)

    @mock.patch("src.handlers.websocket.message.boto3")
    def test_handler_without_connection_id_should_fail(self, mock_boto3):

        response = handler({}, {})

        mock_boto3.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
