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

    def test_foo(self):
        response = self.hello_world_instance.foo(2)
        self.assertIs(12, response)

    def test_foo_if(self):
        response = self.hello_world_instance.foo(1)
        self.assertIs(12, response)
