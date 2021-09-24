from unittest import TestCase

import pydash

from src.service.dbSample import DBSample


class TestDBSample(TestCase):
    def setUp(self):
        self.db_sample_instance = DBSample()
        return

    def test_db_sample(self):
        response = self.db_sample_instance.sample()
        self.assertTrue(pydash.get(response, "message"))
