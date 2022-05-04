import logging
from unittest import TestCase, mock
from src.service.websocket.connection_service import WebsocketConnectionService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestWebsocketConnectionService(TestCase):
    def setUp(self):
        self.filename = "file.csv"
        self.connection_id = "connection"
        self.session = mock.Mock()
        self.connection_instance = WebsocketConnectionService(self.session, logger)

    def test_register_connection_success_should_return_true(self) -> bool:

        was_created = self.connection_instance.register_connection(
            self.connection_id, "user_id", self.filename
        )

        self.assertEqual(was_created, True)

    def test_register_connection_fail_should_return_false(self) -> bool:
        self.session.execute.side_effect = Exception("No valid connection db url")

        was_created = self.connection_instance.register_connection(
            self.connection_id, "user_id", self.filename
        )

        self.assertEqual(was_created, False)

    def test_remove_connection_success_should_return_true(self) -> bool:

        was_created = self.connection_instance.remove_connection(self.connection_id)

        self.assertEqual(was_created, True)

    def test_remove_connection_fail_should_return_false(self) -> bool:
        self.session.execute.side_effect = Exception("No valid connection db url")

        was_created = self.connection_instance.remove_connection(self.connection_id)

        self.assertEqual(was_created, False)
