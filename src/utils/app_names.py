from strenum import StrEnum


class TableNames(StrEnum):
    COMPANY = "company"
    METRIC = "metric"
    RANGE = "value_range"
    INVESTOR = "investor"
    PERIOD = "time_period"
    INVESTMENT = "investment"
    SCENARIO = "financial_scenario"
    SCENARIO_METRIC = "scenario_metric"
    CURRENCY_METRIC = "currency_metric"
    METRIC_TYPES = "metric_types"


class ScenarioNames(StrEnum):
    ACTUALS = "Actuals"
    BUDGET = "Budget"


class MetricNames(StrEnum):
    REVENUE = "Revenue"
    EBITDA = "Ebitda"
    COST_OF_GOODS = "Cost of goods"
    GROSS_PROFIT = "Gross profit"
    SALES_AND_MARKETING = "Sales & marketing"
    R_AND_D = "R&D"
    G_AND_D = "G&D"


BASE_HEADERS = ["Unique ID", "Name", "Sector", "Vertical", "Investor Profile"]

COMPARISON_METRICS = [
    "revenue",
    "growth",
    "ebitda_margin",
    "revenue_vs_budget",
    "ebitda_vs_budget",
    "rule_of_40",
    "gross_profit",
    "gross_margin",
    "sales_and_marketing",
    "general_and_admin",
    "research_and_development",
]
