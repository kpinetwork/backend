from unittest import TestCase
from src.utils.commons_functions import (
    get_list_param,
    remove_white_spaces,
    get_condition_params,
    get_edit_modify_condition_params,
)
from src.utils.app_names import TableNames


class TestQueryBuilder(TestCase):
    def setUp(self):
        self.text = "\t Test \n\n"
        self.expected_full_list = ["1", "2", "3", "4"]
        self.params = {
            "sector": "Application Software,Computer",
            "vertical": "Law,Insurance",
            "size": "<$10million,$30-50million",
            "name": "Company A,Company B",
            "tag": "Industry",
        }

    def test_remove_white_spaces_should_remove_empty_spaces(self):
        result = remove_white_spaces(self.text)

        expected_result = "Test"

        self.assertEqual(result, expected_result)

    def test_get_list_param_should_return_same_values_in_a_list_with_no_empty_string(
        self,
    ):
        values = "1,2,3,4"

        out = get_list_param(values)

        self.assertEqual(out, self.expected_full_list)

    def test_get_list_param_should_return_empty_list_with_empty_string(self):
        values = ""

        out = get_list_param(values)

        self.assertEqual(out, [])

    def test_get_condition_params_should_return_valid_dict_conditions_with_no_empty_param_dict(
        self,
    ):
        expected_result = {
            "size_cohort": self.params["size"].split(","),
            f"{TableNames.TAG}.name": self.params["tag"].split(","),
        }

        conditions = get_condition_params(self.params)

        self.assertEqual(conditions, expected_result)

    def test_get_condition_params_should_return_empty_condition_dict_with_empty_dict_input(
        self,
    ):
        expected_result = dict()

        conditions = get_condition_params(dict())

        self.assertEqual(conditions, expected_result)

    def test_get_edit_modify_conditions_should_return_full_condition_dict_without_empty_strings(
        self,
    ):
        edit_params = {"names": "Company A", "sectors": "Application Software"}
        expected_conditions = {
            "name": [edit_params["names"]],
            "sector": [edit_params["sectors"]],
        }

        conditions = get_edit_modify_condition_params(edit_params)

        self.assertEqual(conditions, expected_conditions)
