from unittest import TestCase

import pydash

from src.service.helloWorld import HelloWorld


class TestHelloWorld(TestCase):
    def setUp(self):
        self.hello_world_instance = HelloWorld()
        return

    def test_hello_world(self):
        response = self.hello_world_instance.hello_world()
        self.assertTrue(pydash.get(response, "message"))

    def test_sample(self):
        response = self.hello_world_instance.sample()
        self.assertTrue(pydash.get(response, "new_message"))
