from unittest import TestCase
from unittest.mock import patch
import pydash

from src.handlers.helloWorldHandler import lambda_handler
from src.service.helloWorld import HelloWorld


class MockHelloWorldClass:
    def hello_world(self):
        return {"message": "hello test"}


class TestHelloWorldHandler(TestCase):
    def setUp(self):
        self.lambda_handler_instance = lambda_handler
        return

    @patch.object(HelloWorld, "hello_world", new=MockHelloWorldClass.hello_world)
    def test_hello_world(self):
        response = self.lambda_handler_instance({}, {})
        self.assertEqual(pydash.get(response, "statusCode"), 200)
        self.assertEqual(pydash.get(response, "body"), '{"message": "hello test"}')
