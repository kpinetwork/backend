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
    TAG = "tag"
    COMPANY_TAG = "company_tag"


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


class CalculatedAnonymizeMetrics(StrEnum):
    GROWTH = "Growth"
    GROSS_PROFIT = "Gross profit"
    REVENUE_PER_EMPLOYEE = "Revenue per employee"


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

YEAR_REPORT_ANONYMIZABLE_METRICS = [
    "revenue",
    "revenue_per_employee",
    "gross_profit",
]

METRIC_PERIOD_NAMES = [
    {"period_name": "Q1", "start_at": "01-01", "end_at": "03-31"},
    {"period_name": "Q2", "start_at": "04-01", "end_at": "06-30"},
    {"period_name": "Q3", "start_at": "07-01", "end_at": "09-30"},
    {"period_name": "Q4", "start_at": "10-01", "end_at": "12-31"},
    {"period_name": "Full-year", "start_at": "01-01", "end_at": "12-31"},
]

DEFAULT_RANGES = [
    {"label": "<$25 million", "min_value": None, "max_value": 25.0},
    {"label": "$100 million+", "min_value": 100.0, "max_value": None},
    {"label": "$25-<$50 million", "min_value": 25.0, "max_value": 50.0},
    {"label": "$75-$100 million", "min_value": 75.0, "max_value": 100.0},
    {"label": "$50-<$75 million", "min_value": 50.0, "max_value": 75.0},
]
