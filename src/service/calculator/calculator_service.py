from decimal import Decimal
from typing import Union


class CalculatorService:
    def __init__(
        self,
        logger,
    ) -> None:
        self.logger = logger

    def is_valid_number(self, number) -> bool:
        return number is not None and isinstance(number, (int, float, Decimal))

    def calculate_growth_rate(
        self, value_recent_year: float, value_prior_year: float, rounded: bool = True
    ) -> Union[float, str]:
        try:
            growth = ((value_recent_year / value_prior_year) - 1) * 100
            if rounded:
                return round(growth)
            return growth
        except Exception as error:
            self.logger.info(error)
            return "NA"

    def calculate_ebitda_margin(
        self, ebitda: float, revenue: float, rounded: bool = True
    ) -> Union[float, str]:
        try:
            margin = (ebitda / revenue) * 100
            if rounded:
                return round(margin)
            return margin
        except Exception as error:
            self.logger.info(error)
            return "NA"

    def calculate_base_metric(self, metric_value: float) -> Union[float, str]:
        if self.is_valid_number(metric_value):
            return round(metric_value * 1)
        return "NA"

    def calculate_sum(
        self, number: float, second_number: float, rounded: bool = True
    ) -> Union[float, str]:
        try:
            return round(number + second_number) if rounded else number + second_number
        except Exception as error:
            self.logger.info(error)
            return "NA"

    def calculate_rule_of_40(
        self,
        revenue_recent_year: float,
        revenue_prior_year: float,
        ebitda_recent_year: float,
        rounded: bool = True,
    ) -> Union[float, str]:
        revenue_growth = self.calculate_growth_rate(
            revenue_recent_year, revenue_prior_year, False
        )
        ebitda_margin = self.calculate_ebitda_margin(
            ebitda_recent_year, revenue_recent_year, False
        )
        if self.is_valid_number(revenue_growth) and self.is_valid_number(ebitda_margin):
            rule_of_40 = revenue_growth + ebitda_margin
            return round(rule_of_40) if rounded else rule_of_40
        return "NA"

    def calculate_actual_vs_budget(
        self, actual_value: float, budget_value: float, rounded: bool = True
    ) -> Union[float, str]:
        try:
            actual_vs_budget = (actual_value / budget_value) * 100
            return round(actual_vs_budget) if rounded else actual_vs_budget
        except Exception as error:
            self.logger.info(error)
            return "NA"

    def calculate_gross_profit(
        self, revenue_value: float, cost_of_goods: float, rounded: bool = True
    ) -> Union[float, str]:
        try:
            gross_profit = revenue_value - cost_of_goods
            return round(revenue_value - cost_of_goods) if rounded else gross_profit
        except Exception as error:
            self.logger.info(error)
            return "NA"

    def calculate_gross_margin(
        self, revenue_value: float, cost_of_goods: float, rounded: bool = True
    ) -> Union[float, str]:
        try:
            gross_profit = self.calculate_gross_profit(
                revenue_value, cost_of_goods, False
            )
            gross_margin = (gross_profit / revenue_value) * 100
            return round(gross_margin) if rounded else gross_margin
        except Exception as error:
            self.logger.info(error)
            return "NA"

    def calculate_sales_and_marketing_of_revenue(
        self,
        revenue_value: float,
        sales_and_marketing_value: float,
        rounded: bool = True,
    ) -> Union[float, str]:
        try:
            sales_and_marketing_of_revenue = (
                sales_and_marketing_value / revenue_value
            ) * 100
            return (
                round(sales_and_marketing_of_revenue)
                if rounded
                else sales_and_marketing_of_revenue
            )
        except Exception as error:
            self.logger.info(error)
            return "NA"

    def calculate_research_and_development_of_revenue(
        self,
        revenue_value: float,
        research_and_development_value: float,
        rounded: bool = True,
    ) -> Union[float, str]:
        try:
            research_and_development_of_revenue = (
                research_and_development_value / revenue_value
            ) * 100
            return (
                round(research_and_development_of_revenue)
                if rounded
                else research_and_development_of_revenue
            )
        except Exception as error:
            self.logger.info(error)
            return "NA"

    def calculate_general_and_admin_of_revenue(
        self, revenue_value: float, general_and_admin_value: float, rounded: bool = True
    ) -> Union[float, str]:
        try:
            general_and_admin_of_revenue = (
                general_and_admin_value / revenue_value
            ) * 100
            return (
                round(general_and_admin_of_revenue)
                if rounded
                else general_and_admin_of_revenue
            )
        except Exception as error:
            self.logger.info(error)
            return "NA"
