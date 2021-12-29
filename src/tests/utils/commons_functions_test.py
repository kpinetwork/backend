from unittest import TestCase
from src.utils.commons_functions import get_list_param, remove_white_spaces


class TestQueryBuilder(TestCase):
    def setUp(self):
        self.text = "\t Test \n\n"
        self.expected_full_list = ["1", "2", "3", "4"]

    def test_remove_white_spaces(self):
        result = remove_white_spaces(self.text)

        expected_result = "Test"

        self.assertEqual(result, expected_result)

    def test_get_list_param_with_no_empty_string(self):
        values = "1,2,3,4"

        out = get_list_param(values)

        self.assertEqual(out, self.expected_full_list)

    def test_get_list_param_with_empty_string(self):
        values = ""

        out = get_list_param(values)

        self.assertEqual(out, [])
