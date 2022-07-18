class CalculatorRepository:
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

    def add_company_filters(self, **kwargs) -> dict:
        filters = dict()
        for k, v in kwargs.items():
            if k != "size_cohort" and k != "margin_group":
                values = [
                    f"'{element}'" for element in v if element and element.strip()
                ]
                filters[f"{self.company_table}.{k}"] = values
        return filters

    def get_columns(self, value_alias: str, need_all: bool) -> list:
        columns = [
            f"{self.company_table}.id",
            f"{self.metric_table}.value as {value_alias}",
        ]
        if need_all:
            columns.extend(
                [
                    f"{self.company_table}.name",
                    f"{self.company_table}.sector",
                    f"{self.company_table}.vertical",
                    f"{self.company_table}.inves_profile_name",
                ]
            )
        return columns

    def get_metric_option(
        self, scenario: str, metric: str, alias: str, year: str
    ) -> dict:
        return {
            "scenario": f"{scenario}-{year}",
            "metric": f"{metric}",
            "alias": f"{alias}",
        }

    def get_actuals_options(self, year: int) -> list:
        return [
            self.get_metric_option("Actuals", "Revenue", "actuals_revenue", year),
            self.get_metric_option("Actuals", "Ebitda", "actuals_ebitda", year),
            self.get_metric_option(
                "Actuals", "Cost of goods", "actuals_cost_of_goods", year
            ),
            self.get_metric_option(
                "Actuals", "Sales & marketing", "actuals_sales_marketing", year
            ),
            self.get_metric_option(
                "Actuals",
                "General & administration",
                "actuals_general_admin",
                year,
            ),
            self.get_metric_option(
                "Actuals",
                "Research & development",
                "actuals_research_development",
                year,
            ),
        ]

    def get_budget_options(self, year: int) -> list:
        return [
            self.get_metric_option("Budget", "Revenue", "budget_revenue", year),
            self.get_metric_option("Budget", "Ebitda", "budget_ebitda", year),
            self.get_metric_option(
                "Budget", "Cost of goods", "budget_cost_of_goods", year
            ),
            self.get_metric_option(
                "Budget", "Sales & marketing", "budget_sales_marketing", year
            ),
            self.get_metric_option(
                "Budget", "General & administration", "budget_general_admin", year
            ),
            self.get_metric_option(
                "Budget",
                "Research & development",
                "budget_research_development",
                year,
            ),
        ]

    def get_forward_budget_options(
        self, year: int, need_prior: bool, need_next: bool
    ) -> list:
        budget_options = []
        if need_prior:
            prior_year = year - 1
            budget_options.extend(
                [
                    self.get_metric_option(
                        "Budget", "Revenue", "prior_budget_revenue", prior_year
                    ),
                    self.get_metric_option(
                        "Budget", "Ebitda", "prior_budget_ebitda", prior_year
                    ),
                ]
            )

        if need_next:
            next_year = year + 1
            budget_options.extend(
                [
                    self.get_metric_option(
                        "Budget", "Revenue", "next_budget_revenue", next_year
                    ),
                    self.get_metric_option(
                        "Budget", "Ebitda", "next_budget_ebitda", next_year
                    ),
                ]
            )

        return budget_options

    def get_base_metrics_options(
        self,
        year: int,
        need_actuals_prior_year: bool,
        need_next_year: bool,
        need_budget_prior_year: bool,
    ) -> list:
        metrics = self.get_actuals_options(year)
        metrics.extend(self.get_budget_options(year))

        if need_actuals_prior_year:
            metrics.append(
                self.get_metric_option(
                    "Actuals", "Revenue", "prior_actuals_revenue", year - 1
                )
            )

        budget_options = self.get_forward_budget_options(
            year, need_budget_prior_year, need_next_year
        )
        metrics.extend(budget_options)

        return metrics

    def get_company_description(self, company_id: str) -> dict:
        try:
            if not (company_id and company_id.strip()):
                return dict()
            query = (
                self.query_builder.add_table_name(self.company_table)
                .add_sql_where_equal_condition(
                    {
                        f"{self.company_table}.id": f"'{company_id}'",
                        f"{self.company_table}.is_public": True,
                    }
                )
                .build()
                .get_query()
            )

            result = self.session.execute(query).fetchall()
            self.session.commit()
            return self.response_sql.process_query_result(result)
        except Exception as error:
            self.logger.info(error)
            raise error

    def get_most_recents_revenue(self, company_id: str) -> list:
        if not (company_id and company_id.strip()):
            return []
        try:
            where_condition = {
                f"{self.scenario_table}.type": "'Actuals'",
                f"{self.metric_table}.name": "'Revenue'",
                f"{self.scenario_table}.company_id": f"'{company_id}'",
                f"{self.company_table}.is_public": True,
            }
            columns = [f"{self.scenario_table}.name", f"{self.metric_table}.value"]

            query = (
                self.query_builder.add_table_name(self.company_table)
                .add_select_conditions(columns)
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
                .add_sql_where_equal_condition(where_condition)
                .add_sql_order_by_condition(["name"], self.query_builder.Order.DESC)
                .add_sql_limit_condition(2)
                .build()
                .get_query()
            )
            result = self.session.execute(query).fetchall()
            self.session.commit()
            return self.response_sql.process_query_list_results(result)

        except Exception as error:
            self.logger.info(error)
            return []

    def get_metric_by_scenario(
        self,
        scenario_name: str,
        metric: str,
        value_alias: str,
        company_id: str = None,
        filters: dict = None,
        need_all: bool = False,
    ) -> dict:
        try:
            columns = self.get_columns(value_alias, need_all)
            where_condition = {
                f"{self.scenario_table}.name": f"'{scenario_name}'",
                f"{self.metric_table}.name": f"'{metric}'",
                f"{self.company_table}.is_public": True,
            }

            if company_id and not filters:
                company_condition = {f"{self.company_table}.id": f"'{company_id}'"}
                where_condition.update(company_condition)

            if filters:
                where_condition.update(filters)

            query = (
                self.query_builder.add_table_name(self.company_table)
                .add_select_conditions(columns)
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
                .add_sql_where_equal_condition(where_condition)
                .build()
                .get_query()
            )
            result = self.session.execute(query).fetchall()
            self.session.commit()
            return self.response_sql.process_query_list_results(result)

        except Exception as error:
            self.logger.info(error)
            raise error

    def get_base_metrics(
        self,
        year: int,
        need_all: bool = False,
        company_id: str = None,
        need_actuals_prior_year: bool = False,
        need_next_year: bool = False,
        need_budget_prior_year: bool = False,
        **conditions,
    ) -> dict:
        filters = self.add_company_filters(**conditions)
        metric_options = self.get_base_metrics_options(
            year, need_actuals_prior_year, need_next_year, need_budget_prior_year
        )
        data = []
        for metric in metric_options:
            base_metric = self.get_metric_by_scenario(
                metric.get("scenario"),
                metric.get("metric"),
                metric.get("alias"),
                company_id,
                filters,
                need_all,
            )
            data.extend(base_metric)

        return self.response_sql.proccess_base_metrics_results(data)
