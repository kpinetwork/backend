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
