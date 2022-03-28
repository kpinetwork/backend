from unittest import TestCase
from src.utils.commons_functions import (
    get_list_param,
    remove_white_spaces,
    get_condition_params,
)


class TestQueryBuilder(TestCase):
    def setUp(self):
        self.text = "\t Test \n\n"
        self.expected_full_list = ["1", "2", "3", "4"]
        self.params = {
            "sector": "A,B",
            "vertical": "V1,V2",
            "size": "<$10million,$30-50million",
        }

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

    def test_get_condition_params(self):
        expected_result = {
            "sector": self.params["sector"].split(","),
            "vertical": self.params["vertical"].split(","),
            "size_cohort": self.params["size"].split(","),
        }

        conditions = get_condition_params(self.params)

        self.assertEqual(conditions, expected_result)

    def test_get_condition_params_with_empty_dict(self):
        expected_result = dict()

        conditions = get_condition_params(dict())

        self.assertEqual(conditions, expected_result)
