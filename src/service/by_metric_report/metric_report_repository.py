from base_exception import AppError
from app_names import TableNames, ScenarioNames, MetricNames


class MetricReportRepository:
    def __init__(self, session, query_builder, response_sql, logger):
        self.session = session
        self.query_builder = query_builder
        self.response_sql = response_sql
        self.logger = logger
        self.scenario_table_label = "scenario"

    def add_company_filters(self, **kwargs) -> dict:
        filters = dict()
        for k, v in kwargs.items():
            if k != "size_cohort" and k != "margin_group":
                values = [
                    f"'{element}'" for element in v if element and element.strip()
                ]
                filters[f"{TableNames.COMPANY}.{k}"] = values
        return filters

    def get_years(self) -> list:
        try:
            start = "start_at"
            query = (
                self.query_builder.add_table_name(TableNames.PERIOD)
                .add_select_conditions(
                    [f"DISTINCT ON({start}) extract(year from {start})::int as year"]
                )
                .add_sql_order_by_condition([f"{start}"], self.query_builder.Order.ASC)
                .build()
                .get_query()
            )
            result = self.session.execute(query).fetchall()
            self.session.commit()
            return [
                year["year"]
                for year in self.response_sql.process_query_list_results(result)
            ]
        except Exception as error:
            self.logger.info(error)
            return []

    def get_base_metric(self, metric: str, scenario: str, filters: dict) -> list:
        try:
            where_conditions = {
                f"{TableNames.METRIC}.name": f"'{metric}'",
                f"{TableNames.SCENARIO}.type": f"'{scenario}'",
            }
            from_count = int(len(scenario) + 2)
            where_conditions.update(filters)
            query = (
                self.query_builder.add_table_name(TableNames.COMPANY)
                .add_select_conditions(
                    [
                        f"{TableNames.COMPANY}.id",
                        f"{TableNames.COMPANY}.name",
                        f"substring({TableNames.SCENARIO}.name from {from_count})::int as year",
                        f"{TableNames.METRIC}.value",
                    ]
                )
                .add_join_clause(
                    {
                        f"{TableNames.SCENARIO}": {
                            "from": f"{TableNames.SCENARIO}.company_id",
                            "to": f"{TableNames.COMPANY}.id",
                        }
                    }
                )
                .add_join_clause(
                    {
                        f"{TableNames.SCENARIO_METRIC}": {
                            "from": f"{TableNames.SCENARIO_METRIC}.scenario_id",
                            "to": f"{TableNames.SCENARIO}.id",
                        }
                    }
                )
                .add_join_clause(
                    {
                        f"{TableNames.METRIC}": {
                            "from": f"{TableNames.SCENARIO_METRIC}.metric_id",
                            "to": f"{TableNames.METRIC}.id",
                        }
                    }
                )
                .add_sql_where_equal_condition(where_conditions)
                .build()
                .get_query()
            )
            result = self.session.execute(query).fetchall()
            self.session.commit()
            return self.response_sql.process_query_list_results(result)
        except Exception as error:
            self.logger.info(error)
            return []

    def __get_subquery_metric(
        self, metric: str, scenario: str, from_count: int = None
    ) -> str:
        from_count = from_count if from_count else int(len(scenario) + 2)
        substring = f"substring(scenario.name from {from_count})"
        return (
            self.query_builder.add_table_name(TableNames.SCENARIO)
            .add_select_conditions([f"NULLIF({TableNames.METRIC}.value, 0)"])
            .add_join_clause(
                {
                    f"{TableNames.SCENARIO_METRIC}": {
                        "from": f"{TableNames.SCENARIO_METRIC}.scenario_id",
                        "to": f"{TableNames.SCENARIO}.id",
                    }
                }
            )
            .add_join_clause(
                {
                    f"{TableNames.METRIC}": {
                        "from": f"{TableNames.SCENARIO_METRIC}.metric_id",
                        "to": f"{TableNames.METRIC}.id",
                    }
                }
            )
            .add_sql_where_equal_condition(
                {
                    f"{TableNames.SCENARIO}.company_id": "company.id",
                    f"{TableNames.SCENARIO}.name": f"concat('{scenario}-', {substring})",
                    f"{TableNames.METRIC}.name": f"'{metric}'",
                }
            )
            .build()
            .get_query()
        )

    def __get_no_base_metrics(
        self, where_conditions: dict, select_value_condition: list, from_count: int = 9
    ) -> list:
        try:
            select_options = [
                f"{TableNames.COMPANY}.id",
                f"{TableNames.COMPANY}.name",
                f"substring(scenario.name from {from_count})::int as year",
            ]
            select_options.extend(select_value_condition)
            query = (
                self.query_builder.add_table_name(TableNames.COMPANY)
                .add_select_conditions(select_options)
                .add_join_clause(
                    {
                        f"{TableNames.SCENARIO}": {
                            "from": f"{self.scenario_table_label}.company_id",
                            "to": f"{TableNames.COMPANY}.id",
                            "alias": f"{self.scenario_table_label}",
                        }
                    }
                )
                .add_join_clause(
                    {
                        f"{TableNames.SCENARIO_METRIC}": {
                            "from": f"{TableNames.SCENARIO_METRIC}.scenario_id",
                            "to": f"{self.scenario_table_label}.id",
                        }
                    }
                )
                .add_join_clause(
                    {
                        f"{TableNames.METRIC}": {
                            "from": f"{TableNames.SCENARIO_METRIC}.metric_id",
                            "to": f"{TableNames.METRIC}.id",
                        }
                    }
                )
                .add_sql_where_equal_condition(where_conditions)
                .add_sql_order_by_condition(
                    [f"{TableNames.COMPANY}.name", f"{self.scenario_table_label}.name"],
                    self.query_builder.Order.ASC,
                )
                .build()
                .get_query()
            )
            result = self.session.execute(query).fetchall()
            return self.response_sql.process_query_list_results(result)
        except Exception as error:
            self.logger.info(error)
            raise error

    def get_actuals_vs_budget_metric(self, metric: str, filters: dict) -> list:
        try:
            where_conditions = {
                f"{self.scenario_table_label}.type": f"'{ScenarioNames.ACTUALS}'",
                f"{TableNames.METRIC}.name": f"'{metric}'",
            }
            where_conditions.update(filters)
            subquery = self.__get_subquery_metric(
                metric,
                ScenarioNames.BUDGET,
                from_count=int(len(ScenarioNames.ACTUALS) + 2),
            )
            select_value = [
                f"{TableNames.METRIC}.value * 100 / ({subquery}) as value",
            ]

            return self.__get_no_base_metrics(where_conditions, select_value)
        except Exception as error:
            self.logger.info(error)
            return []

    def get_gross_profit(
        self, filters: dict, scenario: ScenarioNames = ScenarioNames.ACTUALS
    ) -> list:
        try:
            where_conditions = {
                f"{self.scenario_table_label}.type": f"'{scenario}'",
                f"{TableNames.METRIC}.name": "'Revenue'",
            }
            where_conditions.update(filters)
            subquery = self.__get_subquery_metric("Cost of goods", scenario)
            select_value = [
                f"{TableNames.METRIC}.value - ({subquery}) as value",
            ]
            return self.__get_no_base_metrics(
                where_conditions, select_value, from_count=int(len(scenario) + 2)
            )
        except Exception as error:
            self.logger.info(error)
            return []

    def get_gross_margin(self, filters: dict) -> list:
        try:
            where_conditions = {
                f"{self.scenario_table_label}.type": f"'{ScenarioNames.ACTUALS}'",
                f"{TableNames.METRIC}.name": "'Cost of goods'",
            }
            where_conditions.update(filters)
            subquery = self.__get_subquery_metric("Revenue", ScenarioNames.ACTUALS)
            select_value = [
                f"(1 - ({TableNames.METRIC}.value / ({subquery}))) * 100 as value",
            ]
            return self.__get_no_base_metrics(where_conditions, select_value)
        except Exception as error:
            self.logger.info(error)
            return []

    def get_revenue_per_employee(self, filters: dict) -> list:
        try:
            where_conditions = {
                f"{self.scenario_table_label}.type": f"'{ScenarioNames.ACTUALS}'",
                f"{TableNames.METRIC}.name": "'Run rate revenue'",
            }
            where_conditions.update(filters)
            subquery = self.__get_subquery_metric("Headcount", ScenarioNames.ACTUALS)
            select_value = [
                f"({TableNames.METRIC}.value / ({subquery})) * 1000000 as value",
            ]
            return self.__get_no_base_metrics(where_conditions, select_value)
        except Exception as error:
            self.logger.info(error)
            return []

    def get_opex_as_revenue(self, filters: dict) -> list:
        try:
            where_conditions = {
                f"{self.scenario_table_label}.type": f"'{ScenarioNames.ACTUALS}'",
                f"{TableNames.METRIC}.name": "'Other operating expenses'",
            }
            where_conditions.update(filters)
            sales_and_marketing = self.__get_subquery_metric(
                MetricNames.SALES_AND_MARKETING, ScenarioNames.ACTUALS
            )
            research_and_dev = self.__get_subquery_metric(
                MetricNames.RESEARCH_AND_DEVELOPMENT, ScenarioNames.ACTUALS
            )
            general_and_admin = self.__get_subquery_metric(
                MetricNames.GENERAL_AND_ADMINISTRATION, ScenarioNames.ACTUALS
            )
            revenue = self.__get_subquery_metric("Revenue", ScenarioNames.ACTUALS)
            sum_factors = f"({sales_and_marketing}) + ({research_and_dev}) + ({general_and_admin})"
            select_value = [
                f"({TableNames.METRIC}.value + {sum_factors}) / ({revenue}) * 100 as value",
            ]
            return self.__get_no_base_metrics(where_conditions, select_value)
        except Exception as error:
            self.logger.info(error)
            return []

    def get_debt_ebitda(self, filters: dict) -> list:
        try:
            where_conditions = {
                f"{self.scenario_table_label}.type": f"'{ScenarioNames.ACTUALS}'",
                f"{TableNames.METRIC}.name": "'Long term debt'",
            }
            where_conditions.update(filters)
            subquery = self.__get_subquery_metric("Ebitda", ScenarioNames.ACTUALS)
            select_value = [
                f"({TableNames.METRIC}.value / ({subquery})) as value",
            ]
            return self.__get_no_base_metrics(where_conditions, select_value)
        except Exception as error:
            self.logger.info(error)
            return []

    def get_gross_retention(self, filters: dict) -> list:
        try:
            where_conditions = {
                f"{self.scenario_table_label}.type": f"'{ScenarioNames.ACTUALS}'",
                f"{TableNames.METRIC}.name": "'Losses and downgrades'",
            }
            where_conditions.update(filters)
            subquery = self.__get_subquery_metric(
                "Run rate revenue", ScenarioNames.ACTUALS
            )
            select_value = [
                f"(1 - ({TableNames.METRIC}.value / ({subquery}))) * 100 as value",
            ]
            return self.__get_no_base_metrics(where_conditions, select_value)
        except Exception as error:
            self.logger.info(error)
            return []

    def get_metric_as_percentage_of_revenue(self, metric: str, filters: dict) -> list:
        try:
            where_conditions = {
                f"{self.scenario_table_label}.type": f"'{ScenarioNames.ACTUALS}'",
                f"{TableNames.METRIC}.name": f"'{metric}'",
            }
            where_conditions.update(filters)
            subquery = self.__get_subquery_metric("Revenue", ScenarioNames.ACTUALS)
            select_value = [
                f"{TableNames.METRIC}.value * 100 / ({subquery}) as value",
            ]
            return self.__get_no_base_metrics(where_conditions, select_value)
        except Exception as error:
            self.logger.info(error)
            return []

    def get_metric_ratio(self, dividend: str, divisor: str, filters: dict) -> list:
        try:
            where_conditions = {
                f"{self.scenario_table_label}.type": f"'{ScenarioNames.ACTUALS}'",
                f"{TableNames.METRIC}.name": f"'{dividend}'",
            }
            where_conditions.update(filters)
            subquery = self.__get_subquery_metric(f"{divisor}", ScenarioNames.ACTUALS)
            select_value = [
                f"{TableNames.METRIC}.value / ({subquery}) as value",
            ]
            return self.__get_no_base_metrics(where_conditions, select_value)
        except Exception as error:
            self.logger.info(error)
            return []

    def get_ebitda_margin_metric(self, filters: dict) -> list:
        return self.get_metric_as_percentage_of_revenue("Ebitda", filters)

    def __get_revenue_subquery(self) -> str:
        return (
            self.query_builder.add_table_name(TableNames.SCENARIO)
            .add_select_conditions(
                [f"{TableNames.SCENARIO}.name", f"{TableNames.METRIC}.value"]
            )
            .add_join_clause(
                {
                    f"{TableNames.SCENARIO_METRIC}": {
                        "from": f"{TableNames.SCENARIO_METRIC}.scenario_id",
                        "to": f"{TableNames.SCENARIO}.id",
                    }
                }
            )
            .add_join_clause(
                {
                    f"{TableNames.METRIC}": {
                        "from": f"{TableNames.SCENARIO_METRIC}.metric_id",
                        "to": f"{TableNames.METRIC}.id",
                    }
                }
            )
            .add_sql_where_equal_condition(
                {
                    f"{TableNames.SCENARIO}.company_id": "company.id",
                    f"{TableNames.SCENARIO}.type": f"'{ScenarioNames.ACTUALS}'",
                    f"{TableNames.METRIC}.name": "'Revenue'",
                }
            )
            .add_sql_order_by_condition(
                [f"{TableNames.SCENARIO}.name"], self.query_builder.Order.DESC
            )
            .add_sql_limit_condition(2)
            .build()
            .get_query()
        )

    def get_most_recents_revenue(self, filters: dict) -> list:
        try:
            columns = [f"{TableNames.COMPANY}.id", "revenue.*"]
            select_query = (
                self.query_builder.add_table_name(TableNames.COMPANY)
                .add_select_conditions(columns)
                .build()
                .get_query()
            )
            subquery = self.__get_revenue_subquery()
            where_query = self.query_builder.add_sql_where_equal_condition(
                filters
            ).get_where_query()

            query = """
            {select}
            JOIN LATERAL (
                {subquery}
            ) as revenue on true
            {where}
            """.format(
                select=select_query, subquery=subquery, where=where_query
            )

            result = self.session.execute(query).fetchall()
            self.session.commit()
            return self.response_sql.process_query_list_results(result)

        except Exception as error:
            self.logger.info(error)
            return []

    def __get_arguments(
        self, filters: dict, metric: str = None, scenario: str = None
    ) -> dict:
        arguments = {"filters": filters}
        if metric:
            arguments["metric"] = metric
        if scenario:
            arguments["scenario"] = scenario
        return arguments

    def __get_ratio_arguments(
        self, filters: dict, dividend: str = None, divisor: str = None
    ) -> dict:
        arguments = {"filters": filters}
        if dividend:
            arguments["dividend"] = dividend
        if divisor:
            arguments["divisor"] = divisor
        return arguments

    def __get_metric_names_config(self) -> dict:
        return {
            "revenue": "Revenue",
            "ebitda": "Ebitda",
            "cost_of_goods": "Cost of goods",
            "sales_marketing": "Sales & marketing",
            "general_admin": "General & administration",
            "research_development": "Research & development",
            "customer_lifetime_value": "CLV",
            "customer_acquition_costs": "CAC",
            "customer_annual_value": "CAV",
            "other_operating_expenses": "Other operating expenses",
            "run_rate_revenue": "Run rate revenue",
            "headcount": "Headcount",
            "losses_and_downgrades": "Losses and downgrades",
            "upsells": "Upsells",
            "new_bookings": "New bookings",
            "cash_and_equivalents": "Cash & Equivalents",
            "long_term_debt": "Long term debt",
            "equity_invested": "Equity invested",
            "cash_flow_operations": "Cash flow from operations",
        }

    def __get_base_functions_metric(
        self, filters: dict, scenario_type: ScenarioNames
    ) -> dict:
        metric_names = self.__get_metric_names_config()
        scenario = str(scenario_type).lower()

        return {
            f"{scenario}_{metric}": {
                "function": self.get_base_metric,
                "arguments": self.__get_arguments(
                    filters, metric_names[metric], scenario_type
                ),
            }
            for metric in metric_names
        }

    def __get_actuals_vs_budget_functions_metric(self, filters: dict) -> dict:
        return {
            "revenue_vs_budget": {
                "function": self.get_actuals_vs_budget_metric,
                "arguments": self.__get_arguments(filters, "Revenue"),
            },
            "ebitda_vs_budget": {
                "function": self.get_actuals_vs_budget_metric,
                "arguments": self.__get_arguments(filters, "Ebitda"),
            },
        }

    def __get_gross_profit_functions_metric(self, filters: dict) -> dict:
        return {
            "actuals_gross_profit": {
                "function": self.get_gross_profit,
                "arguments": self.__get_arguments(
                    filters, scenario=ScenarioNames.ACTUALS
                ),
            },
            "budget_gross_profit": {
                "function": self.get_gross_profit,
                "arguments": self.__get_arguments(
                    filters, scenario=ScenarioNames.BUDGET
                ),
            },
        }

    def get_functions_metric(self, filters: dict) -> dict:
        metric_config = {
            "ebitda_margin": {
                "function": self.get_ebitda_margin_metric,
                "arguments": self.__get_arguments(filters),
            },
            "gross_margin": {
                "function": self.get_gross_margin,
                "arguments": self.__get_arguments(filters),
            },
            "sales_and_marketing": {
                "function": self.get_metric_as_percentage_of_revenue,
                "arguments": self.__get_arguments(
                    filters, MetricNames.SALES_AND_MARKETING
                ),
            },
            "general_and_admin": {
                "function": self.get_metric_as_percentage_of_revenue,
                "arguments": self.__get_arguments(
                    filters, MetricNames.GENERAL_AND_ADMINISTRATION
                ),
            },
            "research_and_development": {
                "function": self.get_metric_as_percentage_of_revenue,
                "arguments": self.__get_arguments(
                    filters, MetricNames.RESEARCH_AND_DEVELOPMENT
                ),
            },
            "clv_cac_ratio": {
                "function": self.get_metric_ratio,
                "arguments": self.__get_ratio_arguments(filters, "CLV", "CAC"),
            },
            "cac_ratio": {
                "function": self.get_metric_ratio,
                "arguments": self.__get_ratio_arguments(filters, "CAC", "CAV"),
            },
            "revenue_per_employee": {
                "function": self.get_revenue_per_employee,
                "arguments": self.__get_arguments(filters),
            },
            "opex_as_revenue": {
                "function": self.get_opex_as_revenue,
                "arguments": self.__get_arguments(filters),
            },
            "debt_ebitda": {
                "function": self.get_debt_ebitda,
                "arguments": self.__get_arguments(filters),
            },
        }
        metric_config.update(
            self.__get_base_functions_metric(filters, ScenarioNames.ACTUALS)
        )
        metric_config.update(
            self.__get_base_functions_metric(filters, ScenarioNames.BUDGET)
        )
        metric_config.update(self.__get_gross_profit_functions_metric(filters))
        metric_config.update(self.__get_actuals_vs_budget_functions_metric(filters))

        return metric_config

    def get_metric_records(self, metric: str, filters: dict) -> list:
        functions_metric = self.get_functions_metric(filters)
        metric_config = functions_metric.get(metric)
        if not metric_config:
            raise AppError("Metric not found")

        function = metric_config["function"]
        return function(**metric_config["arguments"])
