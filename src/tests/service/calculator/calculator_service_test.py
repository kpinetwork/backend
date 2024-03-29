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

    @parameterized.expand([["3.2x", 3.2], [14.3, 14.3]])
    def test_get_valid_number(self, number, is_valid):

        valid = self.calculator.get_valid_number(number)

        self.assertEqual(valid, is_valid)

    @parameterized.expand(
        [
            [[12, 34.2, 17.9, 4.3], 17],
            [[12, 25, 35, 21], 23],
        ]
    )
    def test_calculate_average(self, values, expected_average):

        average = self.calculator.calculate_average(values)

        self.assertEqual(average, expected_average)

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

    @parameterized.expand(
        [
            [None, 45, "NA"],
            [14, 16, -2],
            [32, 41, -9],
        ]
    )
    def test_calculate_gross_profit(self, revenue, cost_of_goods, expected_value):

        result = self.calculator.calculate_gross_profit(revenue, cost_of_goods)

        self.assertEqual(result, expected_value)

    @parameterized.expand(
        [
            [None, 45, "NA"],
            [2, 5, -150],
            [10, 40, -300],
        ]
    )
    def test_calculate_gross_margin(self, revenue, cost_of_goods, expected_value):

        result = self.calculator.calculate_gross_margin(revenue, cost_of_goods)

        self.assertEqual(result, expected_value)

    @parameterized.expand(
        [
            [None, 45, "NA"],
            [8, 2, 25],
            [10, 3, 30],
        ]
    )
    def test_calculate_sales_and_markenting_of_revenue(
        self, revenue_value, sales_and_marketing_value, expected_value
    ):

        result = self.calculator.calculate_sales_and_marketing_of_revenue(
            revenue_value, sales_and_marketing_value
        )

        self.assertEqual(result, expected_value)

    @parameterized.expand(
        [
            [None, 45, "NA"],
            [8, 2, 25],
            [10, 3, 30],
        ]
    )
    def test_calculate_research_and_development_of_revenue(
        self, revenue_value, research_and_development, expected_value
    ):

        result = self.calculator.calculate_research_and_development_of_revenue(
            revenue_value, research_and_development
        )

        self.assertEqual(result, expected_value)

    @parameterized.expand(
        [
            [None, 45, "NA"],
            [8, 2, 25],
            [10, 3, 30],
        ]
    )
    def test_calculate_general_and_admin_of_revenue(
        self, revenue_value, general_and_admin_value, expected_value
    ):

        result = self.calculator.calculate_general_and_admin_of_revenue(
            revenue_value, general_and_admin_value
        )

        self.assertEqual(result, expected_value)

    @parameterized.expand(
        [
            [95, 3, 1, "31.7x"],
            [16.5, 15.8, 1, "1.0x"],
            [5, 2.7, 1, "1.9x"],
            [None, 2, 1, "NA"],
            [1, 0, 1, "NA"],
            [5, 2, 2, "2.50x"],
            [9, 3.5, 2, "2.57x"],
            [18, 4.3, 2, "4.19x"],
            [None, 1, 2, "NA"],
            [1, 0, 2, "NA"],
            [0, 1, 2, "0.00x"],
        ]
    )
    def test_calculate_ratio(
        self, dividend_value, divisor_value, decimal_places, expected_value
    ):

        result = self.calculator.calculate_ratio(
            dividend_value, divisor_value, decimal_places
        )

        self.assertEqual(result, expected_value)

    @parameterized.expand(
        [
            [3.8, 5.9, 1, 1.6, 50, 25],
            [1, "NA", 0, 8, 50, "NA"],
            [None, 1, 0, 8, 50, "NA"],
            [3.8, 5.9, 1, 1000, 0, "NA"],
            [3.8, 5.9, 1, 1000, None, "NA"],
        ]
    )
    def test_calculate_opex_of_revenue(
        self,
        sales_and_marketing_value,
        research_and_development_value,
        general_and_admin_value,
        other_operating_expenses,
        revenue,
        expected_value,
    ):

        result = self.calculator.calculate_opex_of_revenue(
            sales_and_marketing_value,
            research_and_development_value,
            general_and_admin_value,
            other_operating_expenses,
            revenue,
        )

        self.assertEqual(result, expected_value)

    @parameterized.expand(
        [
            [2, 5, 400000],
            [None, 5, "NA"],
            [1, 0, "NA"],
        ]
    )
    def test_calculate_revenue_per_employee(
        self, run_rate_revenue, headcount, expected_value
    ):

        result = self.calculator.calculate_revenue_per_employee(
            run_rate_revenue, headcount
        )

        self.assertEqual(result, expected_value)

    @parameterized.expand(
        [
            [2.8, 5.9, -111],
            [0, 5.9, "NA"],
            [None, 5.9, "NA"],
        ]
    )
    def test_calculate_gross_retention(
        self, run_rate_revenue, losses_and_downgrades, expected_value
    ):

        result = self.calculator.calculate_gross_retention(
            run_rate_revenue, losses_and_downgrades
        )

        self.assertEqual(result, expected_value)

    @parameterized.expand(
        [
            [6.8, 9.3, 8.7, 91],
            [0, 5.9, 19, "NA"],
            [None, 5.9, 16, "NA"],
        ]
    )
    def test_calculate_net_retention(
        self, run_rate_revenue, losses_and_downgrades, upsells, expected_value
    ):

        result = self.calculator.calculate_net_retention(
            run_rate_revenue, losses_and_downgrades, upsells
        )

        self.assertEqual(result, expected_value)

    @parameterized.expand(
        [
            [86.8, 89.3, 97],
            [0, 5.9, 0],
            [None, 5.9, "NA"],
            [65, 0, "NA"],
        ]
    )
    def test_calculate_new_bookings_growth(
        self, current_new_bookings, previous_new_bookings, expected_value
    ):

        result = self.calculator.calculate_new_bookings_growth(
            current_new_bookings, previous_new_bookings
        )

        self.assertEqual(result, expected_value)

    @parameterized.expand(
        [
            [10, 12, 0.83],
            [5, 8, 0.62],
            [None, 5.9, "NA"],
            [25, 0, "NA"],
        ]
    )
    def test_calculate_debt_ebitda(self, long_term_debt, ebitda, expected_value):

        result = self.calculator.calculate_debt_ebitda(long_term_debt, ebitda)

        self.assertEqual(result, expected_value)
