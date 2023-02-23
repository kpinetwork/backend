from base_exception import AppError
from app_names import TableNames, ScenarioNames, MetricNames
from base_metrics_config_name import METRICS_CONFIG_NAME
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL


class MetricReportRepository:
    def __init__(
        self, session, query_builder: QuerySQLBuilder, response_sql: ResponseSQL, logger
    ):
        self.session = session
        self.query_builder = query_builder
        self.response_sql = response_sql
        self.logger = logger
        self.scenario_table_label = "scenario"
        self.id_general_table_label = "first_full_year.id"
        self.full_year_period_label = "Full-year"
        self.quarters_period_label = "Quarters"

    def add_filters(self, **kwargs) -> dict:
        filters = dict()
        for k, v in kwargs.items():
            if k != "size_cohort" and k != "margin_group":
                values = [
                    f"'{element}'" for element in v if element and element.strip()
                ]
                filters[k] = values
        return filters

    def get_years(self) -> list:
        try:
            start = "start_at"
            query = (
                self.query_builder.add_table_name(TableNames.PERIOD)
                .add_select_conditions(
                    [f"DISTINCT extract(year from {start})::int as year"]
                )
                .add_sql_order_by_condition(["year"], self.query_builder.Order.ASC)
                .build()
                .get_query()
            )
            result = self.session.execute(query).fetchall()
            return [
                year["year"]
                for year in self.response_sql.process_query_list_results(result)
            ]
        except Exception as error:
            self.logger.info(error)
            return []

    def __get_case_of_time_periods(self) -> str:
        return """
        CASE
            WHEN {period_table}.period_name = 'Full-year' THEN 'Full-year'
            ELSE 'Quarters'
        END AS period
        """.format(
            period_table=TableNames.PERIOD
        )

    def __get_calculated_submetric_subquery(self, metric: str, scenario: str) -> str:
        substring = "first_full_year.year"
        query = (
            self.query_builder.add_table_name(TableNames.COMPANY)
            .add_select_conditions(
                [
                    f"{TableNames.COMPANY}.*",
                    f"{TableNames.SCENARIO}.type as scenario_name",
                    f"{substring} as year",
                    f"{TableNames.METRIC}.name as metric",
                    f"{TableNames.METRIC}.value as value",
                    self.__get_case_of_time_periods(),
                ]
            )
            .add_join_clause(
                {
                    f"{TableNames.SCENARIO}": {
                        "from": f"{TableNames.SCENARIO}.company_id",
                        "to": f"{TableNames.COMPANY}.id",
                    },
                }
            )
            .add_join_clause(
                {
                    f"{TableNames.PERIOD}": {
                        "from": f"{TableNames.PERIOD}.id",
                        "to": f"{TableNames.SCENARIO}.period_id",
                    },
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
            .add_sql_where_equal_condition(
                {
                    f"{TableNames.SCENARIO}.company_id": f"{self.id_general_table_label}",
                    f"{TableNames.SCENARIO}.name": f"concat('{scenario}-', {substring})",
                    f"{TableNames.METRIC}.name": f"'{metric}'",
                }
            )
            .add_sql_group_by_condition(
                [
                    f"{TableNames.COMPANY}.id",
                    f"{TableNames.SCENARIO}.type",
                    f"{TableNames.SCENARIO}.name",
                    f"{TableNames.METRIC}.name",
                    f"{TableNames.METRIC}.value",
                    f"{TableNames.PERIOD}.period_name",
                ]
            )
            .build()
            .get_query()
        )
        return query

    def __get_metric_values_subquery(
        self, metric: str, scenario: str, filters: dict
    ) -> str:
        filters.update(
            {
                f"{TableNames.SCENARIO}.type": f"'{scenario}'",
                f"{TableNames.METRIC}.name": f"'{metric}'",
            }
        )
        tag_join_type = (
            self.query_builder.JoinType.JOIN
            if filters.get("tag")
            else self.query_builder.JoinType.LEFT
        )
        from_count = len(scenario) + 2
        query = (
            self.query_builder.add_table_name(TableNames.COMPANY)
            .add_select_conditions(
                [
                    f"{TableNames.COMPANY}.*",
                    f"{TableNames.SCENARIO}.type as scenario",
                    f"substring({TableNames.SCENARIO}.name from {from_count})::int as year",
                    f"{TableNames.METRIC}.name as metric",
                    f"{TableNames.METRIC}.value as value",
                    self.__get_case_of_time_periods(),
                ]
            )
            .add_join_clause(
                {
                    f"{TableNames.COMPANY_TAG}": {
                        "from": f"{TableNames.COMPANY_TAG}.company_id",
                        "to": f"{TableNames.COMPANY}.id",
                    }
                },
                tag_join_type,
            )
            .add_join_clause(
                {
                    f"{TableNames.TAG}": {
                        "from": f"{TableNames.TAG}.id",
                        "to": f"{TableNames.COMPANY_TAG}.tag_id",
                    }
                },
                tag_join_type,
            )
            .add_join_clause(
                {
                    f"{TableNames.SCENARIO}": {
                        "from": f"{TableNames.SCENARIO}.company_id",
                        "to": f"{TableNames.COMPANY}.id",
                    },
                }
            )
            .add_join_clause(
                {
                    f"{TableNames.PERIOD}": {
                        "from": f"{TableNames.PERIOD}.id",
                        "to": f"{TableNames.SCENARIO}.period_id",
                    },
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
            .add_sql_where_equal_condition(filters)
            .add_sql_group_by_condition(
                [
                    f"{TableNames.COMPANY}.id",
                    f"{TableNames.SCENARIO}.type",
                    f"{TableNames.SCENARIO}.name",
                    f"{TableNames.METRIC}.name",
                    f"{TableNames.METRIC}.value",
                    f"{TableNames.PERIOD}.period_name",
                ]
            )
            .build()
            .get_query()
        )
        return query

    def __add_period_name_where_condition(self, query):
        index = query.find("GROUP BY")
        new_query = (
            query[:index]
            + f"""AND ({TableNames.PERIOD}.period_name = 'Full-year'
            OR {TableNames.PERIOD}.period_name IN ('Q1', 'Q2', 'Q3', 'Q4'))"""
            + query[index:]
        )
        return new_query

    def __add_having_condition(self, query):
        new_query = (
            query
            + """ HAVING (COUNT(full_year.period) = 1 AND full_year.period = 'Full-year')
            OR (COUNT(full_year.period) = 4 AND full_year.period='Quarters')
            LIMIT 1"""
        )
        return new_query

    def __add_having_condition_for_main_metric(self, query):
        new_query = (
            query
            + """ HAVING (COUNT(first_full_year.period) = 1
            AND first_full_year.period = 'Full-year')
            OR (COUNT(first_full_year.period) = 4 AND first_full_year.period='Quarters')"""
        )
        return new_query

    def __get_scenario_values_by_period_subquery(
        self, metric: str, scenario: str, filters: dict
    ) -> str:
        subquery = self.__get_metric_values_subquery(metric, scenario, filters)
        return self.__add_period_name_where_condition(subquery)

    def get_base_metric(self, metric: str, scenario: str, filters: dict) -> list:
        try:
            columns = [
                "full_year.id",
                "full_year.name",
                "full_year.scenario",
                "full_year.year",
                "full_year.period",
            ]
            select_condition = columns.copy()
            select_condition.extend(
                [
                    """SUM(CASE WHEN full_year.period = 'Full-year' THEN full_year.value WHEN
                    full_year.period = 'Quarters' THEN full_year.value END) AS total
                    ,COUNT(full_year.period) as count_periods""",
                ]
            )
            table = self.__get_scenario_values_by_period_subquery(
                metric, scenario, filters
            )
            query = (
                self.query_builder.add_table_name(f"( {table} ) as full_year")
                .add_select_conditions(select_condition)
                .add_sql_where_equal_condition(
                    {
                        "period": [
                            f"'{self.full_year_period_label}'",
                            f"'{self.quarters_period_label}'",
                        ]
                    }
                )
                .add_sql_group_by_condition(columns)
                .build()
                .get_query()
            )
            scenario_results = self.session.execute(query).fetchall()
            return self.response_sql.process_query_list_results(scenario_results)
        except Exception as error:
            self.logger.error(error)
            raise error

    def __get_subquery_for_submetric(
        self,
        metric: str,
        scenario: str,
    ) -> str:
        columns = [
            "full_year.id",
            "full_year.name",
            "full_year.scenario_name",
            "full_year.year",
            "full_year.period",
        ]
        table = self.__get_calculated_submetric_subquery(metric, scenario)
        query = (
            self.query_builder.add_table_name(
                f"( {self.__add_period_name_where_condition(table)} ) as full_year"
            )
            .add_select_conditions(
                [
                    """NULLIF(SUM(CASE WHEN full_year.period = 'Full-year' THEN full_year.value
                    WHEN full_year.period = 'Quarters'
                    THEN full_year.value END), 0)""",
                ]
            )
            .add_sql_where_equal_condition(
                {
                    "period": [
                        f"'{self.full_year_period_label}'",
                        f"'{self.quarters_period_label}'",
                    ]
                }
            )
            .add_sql_group_by_condition(columns)
            .build()
            .get_query()
        )
        return query

    def __get_calculated_metric_subquery(
        self, scenario: str, where_conditions: dict
    ) -> str:
        from_count = len(scenario) + 2
        tag_join_type = (
            self.query_builder.JoinType.JOIN
            if where_conditions.get("tag")
            else self.query_builder.JoinType.LEFT
        )
        query = (
            self.query_builder.add_table_name(TableNames.COMPANY)
            .add_select_conditions(
                [
                    f"{TableNames.COMPANY}.*",
                    "scenario.type as scenario_name",
                    f"substring(scenario.name from {from_count})::int as year",
                    f"{TableNames.METRIC}.name as metric",
                    f"{TableNames.METRIC}.value as value",
                    self.__get_case_of_time_periods(),
                ]
            )
            .add_join_clause(
                {
                    f"{TableNames.COMPANY_TAG}": {
                        "from": f"{TableNames.COMPANY_TAG}.company_id",
                        "to": f"{TableNames.COMPANY}.id",
                    }
                },
                tag_join_type,
            )
            .add_join_clause(
                {
                    f"{TableNames.TAG}": {
                        "from": f"{TableNames.TAG}.id",
                        "to": f"{TableNames.COMPANY_TAG}.tag_id",
                    }
                },
                tag_join_type,
            )
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
                    f"{TableNames.PERIOD}": {
                        "from": f"{TableNames.PERIOD}.id",
                        "to": "scenario.period_id",
                    },
                }
            )
            .add_join_clause(
                {
                    f"{TableNames.SCENARIO_METRIC}": {
                        "from": f"{TableNames.SCENARIO_METRIC}.scenario_id",
                        "to": "scenario.id",
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
            .add_sql_group_by_condition(
                [
                    f"{TableNames.COMPANY}.id",
                    "scenario.type",
                    "scenario.name",
                    f"{TableNames.METRIC}.name",
                    f"{TableNames.METRIC}.value",
                    f"{TableNames.PERIOD}.period_name",
                ]
            )
            .build()
            .get_query()
        )
        return query

    def __get_no_base_metrics(
        self,
        where_conditions: dict,
        select_value_condition: list,
        scenario: str,
    ) -> list:
        try:
            columns = [
                f"{self.id_general_table_label}",
                "first_full_year.name",
                "first_full_year.year as year",
                "first_full_year.period",
                "COUNT(first_full_year.period) as count_periods",
            ]
            select_options = columns.copy()
            select_options.extend(select_value_condition)
            table = self.__get_calculated_metric_subquery(scenario, where_conditions)
            query = (
                self.query_builder.add_table_name(
                    f"( {self.__add_period_name_where_condition(table)} ) as first_full_year"
                )
                .add_select_conditions(select_options)
                .add_sql_where_equal_condition(
                    {
                        "period": [
                            f"'{self.full_year_period_label}'",
                            f"'{self.quarters_period_label}'",
                        ]
                    }
                )
                .add_sql_group_by_condition(
                    [
                        f"{self.id_general_table_label}",
                        "first_full_year.name",
                        "first_full_year.year",
                        "first_full_year.period",
                    ]
                )
                .build()
                .get_query()
            )
            new_query = self.__add_having_condition_for_main_metric(query)
            result = self.session.execute(new_query).fetchall()
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
            subquery = self.__add_having_condition(
                self.__get_subquery_for_submetric(metric, ScenarioNames.BUDGET)
            )
            select_value = [
                f"(SUM(first_full_year.value) * 100) / ({subquery}) as total",
            ]

            return self.__get_no_base_metrics(
                where_conditions, select_value, ScenarioNames.ACTUALS
            )
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
            subquery = self.__add_having_condition(
                self.__get_subquery_for_submetric("Cost of goods", scenario)
            )
            select_value = [
                f"SUM(first_full_year.value) - ({subquery}) as total",
            ]
            return self.__get_no_base_metrics(
                where_conditions,
                select_value,
                scenario,
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
            subquery = self.__add_having_condition(
                self.__get_subquery_for_submetric("Revenue", ScenarioNames.ACTUALS)
            )
            select_value = [
                f"(1 - (SUM(first_full_year.value) / ({subquery}))) * 100 as total",
            ]
            return self.__get_no_base_metrics(
                where_conditions, select_value, ScenarioNames.ACTUALS
            )
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
            subquery = self.__add_having_condition(
                self.__get_subquery_for_submetric("Headcount", ScenarioNames.ACTUALS)
            )
            select_value = [
                f"(SUM(first_full_year.value) / ({subquery})) * 1000000 as total",
            ]
            return self.__get_no_base_metrics(
                where_conditions,
                select_value,
                ScenarioNames.ACTUALS,
            )
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
            sales_and_marketing = self.__add_having_condition(
                self.__get_subquery_for_submetric(
                    MetricNames.SALES_AND_MARKETING, ScenarioNames.ACTUALS
                )
            )
            research_and_dev = self.__add_having_condition(
                self.__get_subquery_for_submetric(
                    MetricNames.RESEARCH_AND_DEVELOPMENT, ScenarioNames.ACTUALS
                )
            )
            general_and_admin = self.__add_having_condition(
                self.__get_subquery_for_submetric(
                    MetricNames.GENERAL_AND_ADMINISTRATION, ScenarioNames.ACTUALS
                )
            )
            revenue = self.__add_having_condition(
                self.__get_subquery_for_submetric("Revenue", ScenarioNames.ACTUALS)
            )
            sum_factors = f"({sales_and_marketing}) + ({research_and_dev}) + ({general_and_admin})"
            select_value = [
                f" (SUM(first_full_year.value) + {sum_factors}) / ({revenue}) * 100 as total",
            ]
            return self.__get_no_base_metrics(
                where_conditions,
                select_value,
                ScenarioNames.ACTUALS,
            )
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
            subquery = self.__add_having_condition(
                self.__get_subquery_for_submetric("Ebitda", ScenarioNames.ACTUALS)
            )
            select_value = [
                f"(SUM(first_full_year.value) / ({subquery})) as total",
            ]
            return self.__get_no_base_metrics(
                where_conditions, select_value, ScenarioNames.ACTUALS
            )
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
            subquery = self.__add_having_condition(
                self.__get_subquery_for_submetric(
                    "Run rate revenue", ScenarioNames.ACTUALS
                )
            )
            select_value = [
                f"(1 - (SUM(first_full_year.value) / ({subquery}))) * 100 as total",
            ]
            return self.__get_no_base_metrics(
                where_conditions,
                select_value,
                ScenarioNames.ACTUALS,
            )
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
            subquery = self.__add_having_condition(
                self.__get_subquery_for_submetric("Revenue", ScenarioNames.ACTUALS)
            )
            select_value = [
                f"SUM(first_full_year.value) * 100 / ({subquery}) as total",
            ]
            return self.__get_no_base_metrics(
                where_conditions, select_value, ScenarioNames.ACTUALS
            )
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
            subquery = self.__add_having_condition(
                self.__get_subquery_for_submetric(f"{divisor}", ScenarioNames.ACTUALS)
            )
            select_value = [
                f"SUM(first_full_year.value) / ({subquery}) as total",
            ]
            return self.__get_no_base_metrics(
                where_conditions, select_value, ScenarioNames.ACTUALS
            )
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
            filters.pop(f"{TableNames.TAG}.name", None)
            columns = [f"{TableNames.COMPANY}.id", "revenue.*"]
            subquery = self.__get_revenue_subquery()
            query = (
                self.query_builder.add_table_name(
                    f"{TableNames.COMPANY} JOIN LATERAL ( {(subquery)} ) as revenue on true"
                )
                .add_select_conditions(columns)
                .add_join_clause(
                    {
                        f"{TableNames.SCENARIO}": {
                            "from": f"{TableNames.SCENARIO}.company_id",
                            "to": f"{TableNames.COMPANY}.id",
                        },
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
                .add_sql_where_equal_condition(filters)
                .build()
                .get_query()
            )
            result = self.session.execute(query).fetchall()
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
        return dict(
            (metric_alias, metric_name)
            for metric_name, metric_alias in METRICS_CONFIG_NAME.items()
        )

    def get_base_functions_metric(
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
            self.get_base_functions_metric(filters, ScenarioNames.ACTUALS)
        )
        metric_config.update(
            self.get_base_functions_metric(filters, ScenarioNames.BUDGET)
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
