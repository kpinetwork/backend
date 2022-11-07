from app_names import MetricNames, CalculatedAnonymizeMetrics

METRICS_CONFIG_NAME = {
    MetricNames.REVENUE: "revenue",
    MetricNames.EBITDA: "ebitda",
    MetricNames.COST_OF_GOODS: "cost_of_goods",
    MetricNames.SALES_AND_MARKETING: "sales_marketing",
    MetricNames.GENERAL_AND_ADMINISTRATION: "general_admin",
    MetricNames.RESEARCH_AND_DEVELOPMENT: "research_development",
    MetricNames.CUSTOMER_LIFETIME_VALUE: "customer_lifetime_value",
    MetricNames.CUSTOMER_ACQUITION_COSTS: "customer_acquition_costs",
    MetricNames.CUSTOMER_ANNUAL_VALUE: "customer_annual_value",
    MetricNames.OTHER_OPERATING_EXPENSES: "other_operating_expenses",
    MetricNames.RUN_RATE_REVENUE: "run_rate_revenue",
    MetricNames.HEADCOUNT: "headcount",
    MetricNames.LOSSES_AND_DOWNGRADES: "losses_and_downgrades",
    MetricNames.UPSELLS: "upsells",
    MetricNames.NEW_BOOKINGS: "new_bookings",
    MetricNames.CASH_AND_EQUIVALENTS: "cash_and_equivalents",
    MetricNames.LONG_TERM_DEBT: "long_term_debt",
    MetricNames.EQUITY_INVESTED: "equity_invested",
    MetricNames.CASH_FLOW_OPERATIONS: "cash_flow_operations",
}


CALCULATED_METRICS_TO_ANONYMIZE = {
    CalculatedAnonymizeMetrics.GROSS_PROFIT: "gross_profit",
    CalculatedAnonymizeMetrics.REVENUE_PER_EMPLOYEE: "revenue_per_employee",
}


def get_all_metrics_to_anonymize():
    all_metrics = METRICS_CONFIG_NAME.copy()
    all_metrics.update(CALCULATED_METRICS_TO_ANONYMIZE.copy())
    return all_metrics


METRICS_TO_ANONYMIZE = get_all_metrics_to_anonymize()
