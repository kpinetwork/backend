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
    def test_handler_should_response_success_status_code(self, mock_boto3):

        response = handler(self.event, {})

        self.assertEqual(response["statusCode"], 200)
        mock_boto3.assert_not_called()

    @mock.patch("src.handlers.websocket.message.boto3")
    def test_handler_should_raise_exception(self, mock_boto3):
        error_message = "Connection id not found"

        response = handler({}, {})

        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(response["error"], error_message)
