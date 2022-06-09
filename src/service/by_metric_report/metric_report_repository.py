from base_exception import AppError


class MetricReportRepository:
    def __init__(self, session, query_builder, response_sql, logger):
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

    def get_years(self) -> list:
        try:
            start = "start_at"
            query = (
                self.query_builder.add_table_name(self.time_period_table)
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
                f"{self.metric_table}.name": f"'{metric}'",
                f"{self.scenario_table}.type": f"'{scenario}'",
            }
            from_count = int(len(scenario) + 2)
            where_conditions.update(filters)
            query = (
                self.query_builder.add_table_name(self.company_table)
                .add_select_conditions(
                    [
                        f"{self.company_table}.id",
                        f"{self.company_table}.name",
                        f"substring({self.scenario_table}.name from {from_count})::int as year",
                        f"{self.metric_table}.value",
                    ]
                )
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
            result = self.session.execute(query).fetchall()
            self.session.commit()
            return self.response_sql.process_query_list_results(result)
        except Exception as error:
            self.logger.info(error)
            return []

    def get_subquery_metric(self, metric: str, scenario: str) -> str:
        substring = "substring(scenario.name from 9)"
        return (
            self.query_builder.add_table_name(self.scenario_table)
            .add_select_conditions([f"NULLIF({self.metric_table}.value, 0)"])
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
            .add_sql_where_equal_condition(
                {
                    f"{self.scenario_table}.company_id": "company.id",
                    f"{self.scenario_table}.name": f"concat('{scenario}-', {substring})",
                    f"{self.metric_table}.name": f"'{metric}'",
                }
            )
            .build()
            .get_query()
        )

    def get_actuals_vs_budget_metric(self, metric: str, filters: dict) -> list:
        try:
            where_conditions = {
                "scenario.type": "'Actuals'",
                f"{self.metric_table}.name": f"'{metric}'",
            }
            where_conditions.update(filters)
            subquery = self.get_subquery_metric(metric, "Budget")
            query = (
                self.query_builder.add_table_name(self.company_table)
                .add_select_conditions(
                    [
                        f"{self.company_table}.id",
                        f"{self.company_table}.name",
                        "substring(scenario.name from 9)::int as year",
                        f"{self.metric_table}.value * 100 / ({subquery}) as value",
                    ]
                )
                .add_join_clause(
                    {
                        f"{self.scenario_table}": {
                            "from": "scenario.company_id",
                            "to": f"{self.company_table}.id",
                            "alias": "scenario",
                        }
                    }
                )
                .add_join_clause(
                    {
                        f"{self.scenario_metric_table}": {
                            "from": f"{self.scenario_metric_table}.scenario_id",
                            "to": "scenario.id",
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
                .add_sql_order_by_condition(
                    [f"{self.company_table}.name", "scenario.name"],
                    self.query_builder.Order.ASC,
                )
                .build()
                .get_query()
            )

            result = self.session.execute(query).fetchall()
            self.session.commit()
            return self.response_sql.process_query_list_results(result)
        except Exception as error:
            self.logger.info(error)
            return []

    def get_ebitda_margin_metric(self, filters: dict) -> list:
        try:
            where_conditions = {
                "scenario.type": "'Actuals'",
                f"{self.metric_table}.name": "'Ebitda'",
            }
            where_conditions.update(filters)
            subquery = self.get_subquery_metric("Revenue", "Actuals")
            query = (
                self.query_builder.add_table_name(self.company_table)
                .add_select_conditions(
                    [
                        f"{self.company_table}.id",
                        f"{self.company_table}.name",
                        "substring(scenario.name from 9)::int as year",
                        f"{self.metric_table}.value * 100 / ({subquery}) as value",
                    ]
                )
                .add_join_clause(
                    {
                        f"{self.scenario_table}": {
                            "from": "scenario.company_id",
                            "to": f"{self.company_table}.id",
                            "alias": "scenario",
                        }
                    }
                )
                .add_join_clause(
                    {
                        f"{self.scenario_metric_table}": {
                            "from": f"{self.scenario_metric_table}.scenario_id",
                            "to": "scenario.id",
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
                .add_sql_order_by_condition(
                    [f"{self.company_table}.name", "scenario.name"],
                    self.query_builder.Order.ASC,
                )
                .build()
                .get_query()
            )
            result = self.session.execute(query).fetchall()
            self.session.commit()
            return self.response_sql.process_query_list_results(result)
        except Exception as error:
            self.logger.info(error)
            return []

    def get_revenue_subquery(self) -> str:
        return (
            self.query_builder.add_table_name(self.scenario_table)
            .add_select_conditions(
                [f"{self.scenario_table}.name", f"{self.metric_table}.value"]
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
            .add_sql_where_equal_condition(
                {
                    f"{self.scenario_table}.company_id": "company.id",
                    f"{self.scenario_table}.type": "'Actuals'",
                    f"{self.metric_table}.name": "'Revenue'",
                }
            )
            .add_sql_order_by_condition(
                [f"{self.scenario_table}.name"], self.query_builder.Order.DESC
            )
            .add_sql_limit_condition(2)
            .build()
            .get_query()
        )

    def get_most_recents_revenue(self, filters: dict) -> list:
        try:
            columns = [f"{self.company_table}.id", "revenue.*"]
            select_query = (
                self.query_builder.add_table_name(self.company_table)
                .add_select_conditions(columns)
                .build()
                .get_query()
            )
            subquery = self.get_revenue_subquery()
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

    def get_arguments(
        self, filters: dict, metric: str = None, scenario: str = None
    ) -> dict:
        arguments = {"filters": filters}
        if metric:
            arguments["metric"] = metric
        if scenario:
            arguments["scenario"] = scenario
        return arguments

    def get_functions_metric(self, filters: dict) -> dict:
        return {
            "actuals_revenue": {
                "function": self.get_base_metric,
                "arguments": self.get_arguments(filters, "Revenue", "Actuals"),
            },
            "actuals_ebitda": {
                "function": self.get_base_metric,
                "arguments": self.get_arguments(filters, "Ebitda", "Actuals"),
            },
            "budget_revenue": {
                "function": self.get_base_metric,
                "arguments": self.get_arguments(filters, "Revenue", "Budget"),
            },
            "budget_ebitda": {
                "function": self.get_base_metric,
                "arguments": self.get_arguments(filters, "Ebitda", "Budget"),
            },
            "revenue_vs_budget": {
                "function": self.get_actuals_vs_budget_metric,
                "arguments": self.get_arguments(filters, "Revenue"),
            },
            "ebitda_vs_budget": {
                "function": self.get_actuals_vs_budget_metric,
                "arguments": self.get_arguments(filters, "Ebitda"),
            },
            "ebitda_margin": {
                "function": self.get_ebitda_margin_metric,
                "arguments": self.get_arguments(filters),
            },
        }

    def get_metric_records(self, metric: str, filters: dict) -> list:
        functions_metric = self.get_functions_metric(filters)
        metric_config = functions_metric.get(metric)
        if not metric_config:
            raise AppError("Metric not found")

        function = metric_config["function"]
        return function(**metric_config["arguments"])
