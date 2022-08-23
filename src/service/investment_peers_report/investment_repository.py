from collections import defaultdict
from app_names import MetricNames


class InvestmentRepository:
    def __init__(
        self,
        session,
        query_builder,
        response_sql,
        logger,
    ) -> None:
        self.session = session
        self.query_builder = query_builder
        self.response_sql = response_sql
        self.logger = logger
        self.metric_table = "metric"
        self.company_table = "company"
        self.scenario_table = "financial_scenario"
        self.scenario_metric_table = "scenario_metric"
        self.time_period_table = "time_period"
        self.base_metrics = {
            "Actuals": {
                MetricNames.REVENUE: "actuals_revenue",
                MetricNames.EBITDA: "actuals_ebitda",
                MetricNames.COST_OF_GOODS: "actuals_cost_of_goods",
                MetricNames.SALES_AND_MARKETING: "actuals_sales_marketing",
                MetricNames.GENERAL_AND_ADMINISTRATION: "actuals_general_admin",
                MetricNames.RESEARCH_AND_DEVELOPMENT: "actuals_research_development",
                MetricNames.CUSTOMER_LIFETIME_VALUE: "actuals_clv",
                MetricNames.CUSTOMER_ANNUAL_VALUE: "actuals_cav",
                MetricNames.CUSTOMER_ACQUITION_COSTS: "actuals_cac",
                MetricNames.OTHER_OPERATING_EXPENSES: "actuals_other_operating_expenses",
                MetricNames.HEADCOUNT: "actuals_headcount",
                MetricNames.RUN_RATE_REVENUE: "actuals_run_rate_revenue",
                MetricNames.LOSSES_AND_DOWNGRADES: "actuals_losses_and_downgrades",
                MetricNames.UPSELLS: "actuals_upsells",
                MetricNames.NEW_BOOKINGS: "actuals_new_bookings",
            },
            "Budget": {
                MetricNames.REVENUE: "budget_revenue",
                MetricNames.EBITDA: "budget_ebitda",
                MetricNames.COST_OF_GOODS: "budget_cost_of_goods",
                MetricNames.SALES_AND_MARKETING: "budget_sales_marketing",
                MetricNames.GENERAL_AND_ADMINISTRATION: "budget_general_admin",
                MetricNames.RESEARCH_AND_DEVELOPMENT: "budget_research_development",
                MetricNames.CUSTOMER_LIFETIME_VALUE: "budget_clv",
                MetricNames.CUSTOMER_ANNUAL_VALUE: "budget_cav",
                MetricNames.CUSTOMER_ACQUITION_COSTS: "budget_cac",
                MetricNames.OTHER_OPERATING_EXPENSES: "budget_other_operating_expenses",
                MetricNames.HEADCOUNT: "budget_headcount",
                MetricNames.RUN_RATE_REVENUE: "budget_run_rate_revenue",
                MetricNames.LOSSES_AND_DOWNGRADES: "budget_losses_and_downgrades",
                MetricNames.UPSELLS: "budget_upsells",
                MetricNames.NEW_BOOKINGS: "budget_new_bookings",
            },
        }
        self.metrics = [
            "Revenue",
            "Ebitda",
            "Cost of goods",
            "Sales & marketing",
            "General & administration",
            "Research & development",
            "CLV",
            "CAC",
            "CAV",
            "Other operating expenses",
            "Headcount",
            "Run rate revenue",
            "Losses and downgrades",
            "Upsells",
            "New bookings",
        ]

    def add_company_filters(self, **kwargs) -> dict:
        filters = dict()
        for k, v in kwargs.items():
            if k != "size_cohort" and k != "margin_group":
                values = [
                    f"'{element}'" for element in v if element and element.strip()
                ]
                filters[f"{self.company_table}.{k}"] = values
        return filters

    def get_scenarios_columns(self) -> list:
        return [
            f"{self.company_table}.*",
            f"{self.scenario_table}.name as scenario",
            f"{self.scenario_table}.type",
            f"{self.metric_table}.name as metric",
            f"{self.metric_table}.value",
        ]

    def get_investments_columns(self) -> list:
        return [
            "DISTINCT ON(company_id) company_id",
            "extract(year from investment_date)::int as invest_year",
            "round",
        ]

    def get_years(self, years: list) -> list:
        metric_years = set()
        for year in years:
            metric_years.add(year)
            metric_years.add(year - 1)
        return list(metric_years)

    def get_in_values(self, values: list) -> list:
        return [
            f"'{str(value)}'"
            for value in values
            if value is not None and str(value).strip()
        ]

    def get_year_query_array(self, years: list) -> list:
        return [
            f"'%-{str(year)}'"
            for year in years
            if year is not None and str(year).strip()
        ]

    def get_investments_dict(self, records: list) -> dict:
        investment_data = defaultdict(dict)
        [investment_data[invest.get("company_id")].update(invest) for invest in records]

        return investment_data

    def get_investments(self) -> dict:
        try:
            query = (
                self.query_builder.add_table_name("investment")
                .add_select_conditions(self.get_investments_columns())
                .add_sql_order_by_condition(
                    ["company_id", "investment_date", "round"],
                    self.query_builder.Order.ASC,
                )
                .build()
                .get_query()
            )
            result = self.session.execute(query).fetchall()
            self.session.commit()
            return self.get_investments_dict(
                self.response_sql.process_query_list_results(result)
            )
        except Exception as error:
            self.logger.info(error)
            return dict()

    def get_base_scenarios_query(self, companies: list, filters: dict) -> str:
        where_conditions = {
            f"{self.company_table}.id": self.get_in_values(companies),
            f"{self.company_table}.is_public": True,
            f"{self.scenario_table}.type": ["'Actuals'", "'Budget'"],
        }
        if filters:
            where_conditions.update(filters)

        query = (
            self.query_builder.add_table_name(self.company_table)
            .add_select_conditions(self.get_scenarios_columns())
            .add_join_clause(
                {
                    f"{self.scenario_table}": {
                        "from": f"{self.scenario_table}.company_id",
                        "to": f"{self.company_table}.id",
                    }
                }
            )
            .add_join_clause(
                {
                    f"{self.scenario_metric_table}": {
                        "from": f"{self.scenario_metric_table}.scenario_id",
                        "to": f"{self.scenario_table}.id",
                    }
                }
            )
            .add_join_clause(
                {
                    f"{self.metric_table}": {
                        "from": f"{self.scenario_metric_table}.metric_id",
                        "to": f"{self.metric_table}.id",
                    }
                }
            )
            .add_sql_where_equal_condition(where_conditions)
            .build()
            .get_query()
        )

        return query

    def get_scenarios(self, companies: list, years: list, filters: dict) -> list:
        try:
            base_query = self.get_base_scenarios_query(companies, filters)
            query_years = self.get_years(years)
            query = """
                {base_query}
                AND {scenario_table}.name LIKE ANY (array[{years}]);
            """.format(
                base_query=base_query,
                scenario_table=self.scenario_table,
                years=",".join(self.get_year_query_array(query_years)),
            )

            records = self.session.execute(query).fetchall()
            self.session.commit()
            return self.response_sql.process_query_list_results(records)
        except Exception as error:
            self.logger.info(error)
            raise error

    def get_metric(self, scenario: dict, base_year: int) -> dict:
        scenario_name = scenario.get("scenario")
        year = int(scenario_name.split("-")[1])
        if scenario["metric"] not in self.metrics:
            return dict()
        if year not in [base_year - 1, base_year]:
            return dict()

        metric_name = self.base_metrics[scenario["type"]][scenario["metric"]]
        if year < base_year:
            metric_name = f"prior_{metric_name}"
        scenario.update({metric_name: scenario.get("value")})
        return scenario

    def get_scenarios_dict(
        self, data: list, investments: dict, invest_year: int
    ) -> dict:
        scenarios_data = defaultdict(dict)
        for scenario in data:
            base_year = investments[scenario.get("id")]["invest_year"]
            metric_data = self.get_metric(scenario, base_year + invest_year)
            scenarios_data[scenario.get("id")].update(metric_data)
        scenarios = {
            company_id: scenarios_data[company_id]
            for company_id in scenarios_data.keys()
            if scenarios_data[company_id]
        }
        return scenarios

    def get_base_metrics(self, invest_year: int, **conditions) -> dict:
        investments = self.get_investments()
        companies = investments.keys()
        years = [
            investments[company_id]["invest_year"] + invest_year
            for company_id in investments
        ]
        if not years:
            return dict()

        years = self.get_years(years)

        filters = self.add_company_filters(**conditions)

        scenarios = self.get_scenarios(companies, years, filters)

        return self.get_scenarios_dict(scenarios, investments, invest_year)
