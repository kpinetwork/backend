from unittest import TestCase
from src.utils.commons_functions import remove_white_spaces


class TestQueryBuilder(TestCase):
    def setUp(self):
        self.text = "\t Test \n\n"
        pass

    def test_remove_white_spaces(self):
        result = remove_white_spaces(self.text)

        expected_result = "Test"

        self.assertEqual(result, expected_result)
