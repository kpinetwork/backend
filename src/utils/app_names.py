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
    METRIC_SORT = "metric_sort"
    TAGS = "tag"


class ScenarioNames(StrEnum):
    ACTUALS = "Actuals"
    BUDGET = "Budget"


class MetricNames(StrEnum):
    REVENUE = "Revenue"
    EBITDA = "Ebitda"
    COST_OF_GOODS = "Cost of goods"
    SALES_AND_MARKETING = "Sales & marketing"
    GENERAL_AND_ADMINISTRATION = "General & administration"
    RESEARCH_AND_DEVELOPMENT = "Research & development"
    CUSTOMER_LIFETIME_VALUE = "CLV"
    CUSTOMER_ACQUITION_COSTS = "CAC"
    CUSTOMER_ANNUAL_VALUE = "CAV"
    OTHER_OPERATING_EXPENSES = "Other operating expenses"
    HEADCOUNT = "Headcount"
    RUN_RATE_REVENUE = "Run rate revenue"
    LOSSES_AND_DOWNGRADES = "Losses and downgrades"
    UPSELLS = "Upsells"
    NEW_BOOKINGS = "New bookings"
    CASH_AND_EQUIVALENTS = "Cash & Equivalents"
    LONG_TERM_DEBT = "Long term debt"
    EQUITY_INVESTED = "Equity invested"
    CASH_FLOW_OPERATIONS = "Cash flow from operations"


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
    "debt_ebitda",
]
