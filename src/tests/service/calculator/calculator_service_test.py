from unittest import TestCase
import logging
from parameterized import parameterized
from src.service.calculator.calculator_service import CalculatorService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestCalculatorService(TestCase):
    def setUp(self):
        self.calculator = CalculatorService(logger)

    @parameterized.expand(
        [
            [None, False],
            ["45", False],
            [14.3, True],
            [45, True],
        ]
    )
    def test_is_valid_number(self, number, is_valid):

        valid = self.calculator.is_valid_number(number)

        self.assertEqual(valid, is_valid)

    @parameterized.expand(
        [
            [None, 23, False, "NA"],
            [14, 23, True, -39],
            [14, 16, False, -12.5],
        ]
    )
    def test_calculate_growth_rate(
        self, recent_value, prior_value, rounded, expected_growth
    ):

        result = self.calculator.calculate_growth_rate(
            recent_value, prior_value, rounded
        )

        self.assertEqual(result, expected_growth)

    @parameterized.expand(
        [
            [None, 15, False, "NA"],
            [14, 23, True, 61],
            [14, 16, False, 87.5],
        ]
    )
    def test_calculate_ebitda_margin(
        self, ebitda, revenue, rounded, expected_ebitda_margin
    ):

        result = self.calculator.calculate_ebitda_margin(ebitda, revenue, rounded)

        self.assertEqual(result, expected_ebitda_margin)

    @parameterized.expand(
        [
            [None, "NA"],
            ["14", "NA"],
            [76.4, 76],
            [23, 23],
        ]
    )
    def test_calculate_base_metric(self, metric, expected_value):

        result = self.calculator.calculate_base_metric(metric)

        self.assertEqual(result, expected_value)

    @parameterized.expand(
        [
            [None, 45, 30, "NA"],
            [14, 16, -10, -84],
        ]
    )
    def test_calculate_rule_of_40(
        self, recent_revenue, prior_revenue, recent_ebitda, expected_value
    ):

        result = self.calculator.calculate_rule_of_40(
            recent_revenue, prior_revenue, recent_ebitda
        )

        self.assertEqual(result, expected_value)

    @parameterized.expand(
        [
            [None, 45, "NA"],
            [14, 16, 88],
            [32, 41, 78],
        ]
    )
    def test_calculate_actual_vs_budget(self, actual, budget, expected_value):

        result = self.calculator.calculate_actual_vs_budget(actual, budget)

        self.assertEqual(result, expected_value)

    @parameterized.expand(
        [
            [None, 45, "NA"],
            [14, 16, 30],
            [32, 41, 73],
        ]
    )
    def test_calculate_dum(self, number, second_number, expected_sum):

        result = self.calculator.calculate_sum(number, second_number)

        self.assertEqual(result, expected_sum)
