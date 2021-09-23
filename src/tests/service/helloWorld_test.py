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

    def test_test_sonar_cloud_if_branch(self):
        response = self.hello_world_instance.test_sonar_cloud(1)
        self.assertIs(12, response)

    def test_test_sonar_cloud(self):
        response = self.hello_world_instance.test_sonar_cloud(10)
        self.assertIs(12, response)
