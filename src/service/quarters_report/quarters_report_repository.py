from base_exception import AppError
from app_names import TableNames, ScenarioNames
from base_metrics_config_name import METRICS_CONFIG_NAME
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL


class QuartersReportRepository:
    def __init__(
        self, session, query_builder: QuerySQLBuilder, response_sql: ResponseSQL, logger
    ):
        self.session = session
        self.query_builder = query_builder
        self.response_sql = response_sql
        self.logger = logger

    def __get_arguments(
        self,
        filters: dict,
        metric: str = None,
        scenario_type: str = None,
        years: list = [],
    ) -> dict:
        arguments = {"filters": filters}
        if metric:
            arguments["metric"] = metric
        if scenario_type:
            arguments["scenario_type"] = scenario_type
        if years:
            arguments["years"] = years
        return arguments

    def __get_metric_names_config(
        self,
    ) -> dict:  # esta tambien esta en el metric report repository
        return dict(
            (metric_alias, metric_name)
            for metric_name, metric_alias in METRICS_CONFIG_NAME.items()
        )

    # def add_filters(self, **kwargs) -> dict: #esta existe en el metric report repository
    #     filters = dict()
    #     for k, v in kwargs.items():
    #         if k != "size_cohort" and k != "margin_group":
    #             values = [
    #                 f"'{element}'" for element in v if element and element.strip()
    #             ]
    #             filters[k] = values
    #     return filters

    def __get_base_where_conditions(
        self, metric: str, scenario_type: str, years: list, filters: dict
    ) -> dict:
        from_count = len(scenario_type) + 2
        where_conditions = {
            f"{TableNames.SCENARIO}.type": f"'{scenario_type}'",
            f"{TableNames.PERIOD}.period_name": ["'Q1'", "'Q2'", "'Q3'", "'Q4'"],
            f"{TableNames.METRIC}.name": f"'{metric}'",
            f"substring({TableNames.SCENARIO}.name from {from_count})::int": years,
        }
        where_conditions.update(filters)
        return where_conditions

    def __get_having_condition(self) -> str:
        return f" HAVING count({TableNames.PERIOD}.period_name ) = 4 "

    def get_base_query(
        self, select_conditions: list, where_conditions: dict, group_by_conditions: list
    ) -> str:
        return (
            self.query_builder.add_table_name(TableNames.COMPANY)
            .add_select_conditions(select_conditions)
            .add_join_clause(
                {
                    f"{TableNames.SCENARIO}": {
                        "from": f"{TableNames.SCENARIO}.company_id",
                        "to": f"{TableNames.COMPANY}.id",
                    }
                },
            )
            .add_join_clause(
                {
                    f"{TableNames.PERIOD}": {
                        "from": f"{TableNames.PERIOD}.id",
                        "to": f"{TableNames.SCENARIO}.period_id",
                    }
                },
            )
            .add_join_clause(
                {
                    f"{TableNames.SCENARIO_METRIC}": {
                        "from": f"{TableNames.SCENARIO_METRIC}.scenario_id",
                        "to": f"{TableNames.SCENARIO}.id",
                    }
                },
            )
            .add_join_clause(
                {
                    f"{TableNames.METRIC}": {
                        "from": f"{TableNames.METRIC}.id",
                        "to": f"{TableNames.SCENARIO_METRIC}.metric_id",
                    }
                },
            )
            .add_sql_where_equal_condition(where_conditions)
            .add_sql_group_by_condition(group_by_conditions)
            .build()
            .get_query()
        )

    def get_quarters_total_query(
        self, metric: str, scenario_type: str, years: list, filters: dict
    ) -> str:
        where_conditions = self.__get_base_where_conditions(
            metric, scenario_type, years, filters
        )
        select_conditions = [
            f"{TableNames.COMPANY}.id as company_id",
            f"{TableNames.SCENARIO}.name as scenario",
            f"SUM({TableNames.METRIC}.value) as full_year",
            f"COUNT({TableNames.PERIOD}.period_name) as quarters_count",
        ]
        group_by_conditions = [
            f"{TableNames.COMPANY}.id",
            f"{TableNames.SCENARIO}.name",
        ]

        return self.get_base_query(
            select_conditions, where_conditions, group_by_conditions
        )

    def get_averages_by_quarters_query(
        self, metric: str, scenario_type: str, years: list, filters: dict
    ) -> str:
        where_conditions = self.__get_base_where_conditions(
            metric, scenario_type, years, filters
        )
        select_conditions = [
            f"{TableNames.SCENARIO}.name as scenario",
            f"{TableNames.PERIOD}.period_name as period",
            f"AVG({TableNames.METRIC}.value) as average",
        ]
        group_by_conditions = [
            f"{TableNames.SCENARIO}.name",
            f"{TableNames.PERIOD}.period_name",
        ]

        return self.get_base_query(
            select_conditions, where_conditions, group_by_conditions
        )

    def get_averages_of_quarters_total_query(
        self, metric: str, scenario_type: str, years: list, filters: dict
    ) -> str:
        where_conditions = self.__get_base_where_conditions(
            metric, scenario_type, years, filters
        )
        select_conditions = [
            f"{TableNames.SCENARIO}.name as scenario",
            f"SUM({TableNames.METRIC}.value) as total",
        ]
        group_by_conditions = [
            f"{TableNames.COMPANY}.id",
            f"{TableNames.SCENARIO}.name",
        ]
        full_year_table = self.get_base_query(
            select_conditions, where_conditions, group_by_conditions
        )
        full_year_table = " ".join([full_year_table, self.__get_having_condition()])

        query = (
            self.query_builder.add_table_name(f"( {full_year_table} ) as full_year")
            .add_select_conditions(
                ["full_year.scenario", "AVG(full_year.total) as full_year_average"]
            )
            .add_sql_group_by_condition(["full_year.scenario"])
            .build()
            .get_query()
        )

        return query

    def __get_divisor_subquery_for_years_comparison(
        self, scenario_type: str, metric: str
    ) -> str:
        select_conditions = [
            f"{TableNames.COMPANY}.id",
            f"SUM({TableNames.METRIC}.value) as value",
            "main_table.year as divisor_year",
        ]
        where_conditions = {
            f"{TableNames.SCENARIO}.name": f"concat('{scenario_type}-', main_table.year -1)",
            f"{TableNames.PERIOD}.period_name": ["'Q1'", "'Q2'", "'Q3'", "'Q4'"],
            f"{TableNames.METRIC}.name": f"'{metric}'",
        }
        group_by_conditions = [
            f"{TableNames.COMPANY}.id",
            f"{TableNames.SCENARIO}.name",
        ]
        return self.get_base_query(
            select_conditions, where_conditions, group_by_conditions
        )

    def __get_divisor_table_for_year_comparison(self, scenario_type, metric) -> str:
        divisor_subquery = self.__get_divisor_subquery_for_years_comparison(
            scenario_type, metric
        )
        return (
            self.query_builder.add_table_name(
                f"( {divisor_subquery} ) as divisor_table"
            )
            .add_select_conditions(["divisor_table.value"])
            .add_sql_where_equal_condition({"divisor_table.id": "main_table.id"})
            .build()
            .get_query()
        )

    def __get_dividend_table_for_years_comparison(
        self, scenario_type: str, metric: str, years: list, filters: dict
    ) -> str:
        from_count = len(scenario_type) + 2
        select_conditions = [
            f"{TableNames.COMPANY}.id",
            f"{TableNames.SCENARIO}.name as scenario",
            f"substring({TableNames.SCENARIO}.name from {from_count})::int as year",
            f"{TableNames.METRIC}.name",
            f"SUM({TableNames.METRIC}.value) as value",
        ]
        where_conditions = self.__get_base_where_conditions(
            metric, scenario_type, years, filters
        )
        group_by_conditions = [
            f"{TableNames.COMPANY}.id",
            f"{TableNames.SCENARIO}.name",
            f"{TableNames.METRIC}.name",
        ]
        dividend_table = self.get_base_query(
            select_conditions, where_conditions, group_by_conditions
        )
        dividend_table = " ".join([dividend_table, self.__get_having_condition()])
        return dividend_table

    def get_quarter_comparison_by_year_query(
        self, metric: str, scenario_type: str, years: list, filters: dict
    ) -> str:
        divisor_table = self.__get_divisor_table_for_year_comparison(
            scenario_type, metric
        )
        dividend_table = self.__get_dividend_table_for_years_comparison(
            scenario_type, metric, years, filters
        )
        query = (
            self.query_builder.add_table_name(f"( {dividend_table} ) as main_table")
            .add_select_conditions(
                [
                    "main_table.id",
                    "main_table.scenario",
                    "main_table.year",
                    f"( SUM(main_table.value) / ( {divisor_table})) as percentage",
                ]
            )
            .add_sql_group_by_condition(
                ["main_table.id", "main_table.scenario", "main_table.year"]
            )
            .build()
            .get_query()
        )

        return query

    def get_base_metric_records(
        self, metric: str, scenario_type: str, years: list, filters: dict
    ) -> list:
        try:
            from_count = len(scenario_type) + 2
            columns = [
                f"{TableNames.COMPANY}.id",
                f"{TableNames.COMPANY}.name",
                f"{TableNames.SCENARIO}.name as scenario",
                f"{TableNames.METRIC}.name as metric",
                f"{TableNames.PERIOD}.period_name",
                f"{TableNames.METRIC}.value",
                f"substring({TableNames.SCENARIO}.name from {from_count})::int as year",
                "total_quarters.full_year",
                "average.average",
                "full_year_average.full_year_average",
                "total_quarters.quarters_count",
                "comparison.percentage",
            ]
            where_conditions = self.__get_base_where_conditions(
                metric, scenario_type, years, filters
            )

            full_year_table = self.get_quarters_total_query(
                metric, scenario_type, years, filters
            )
            quarters_averages_table = self.get_averages_by_quarters_query(
                metric, scenario_type, years, filters
            )
            full_year_averages_table = self.get_averages_of_quarters_total_query(
                metric, scenario_type, years, filters
            )
            comparison_table = self.get_quarter_comparison_by_year_query(
                metric, scenario_type, years, filters
            )
            full_year_join_condition = f"""total_quarters.company_id
            AND {TableNames.SCENARIO}.name = total_quarters.scenario """
            quarters_average_join_condition = f""" average.scenario
            AND {TableNames.PERIOD}.period_name = average.period """
            comparison_join_condition = f"""comparison.id
            AND {TableNames.SCENARIO}.name = comparison.scenario"""

            query = (
                self.query_builder.add_table_name(f"{TableNames.COMPANY}")
                .add_select_conditions(columns)
                .add_join_clause(
                    {
                        f"{TableNames.SCENARIO}": {
                            "from": f"{TableNames.SCENARIO}.company_id",
                            "to": f"{TableNames.COMPANY}.id",
                        }
                    },
                )
                .add_join_clause(
                    {
                        f"{TableNames.PERIOD}": {
                            "from": f"{TableNames.PERIOD}.id",
                            "to": f"{TableNames.SCENARIO}.period_id",
                        }
                    },
                )
                .add_join_clause(
                    {
                        f"{TableNames.SCENARIO_METRIC}": {
                            "from": f"{TableNames.SCENARIO_METRIC}.scenario_id",
                            "to": f"{TableNames.SCENARIO}.id",
                        }
                    },
                )
                .add_join_clause(
                    {
                        f"{TableNames.METRIC}": {
                            "from": f"{TableNames.METRIC}.id",
                            "to": f"{TableNames.SCENARIO_METRIC}.metric_id",
                        }
                    },
                )
                .add_join_clause(
                    {
                        f"( {full_year_table} ) total_quarters": {
                            "from": f"{TableNames.COMPANY}.id",
                            "to": full_year_join_condition,
                        }
                    }
                )
                .add_join_clause(
                    {
                        f"( {quarters_averages_table} ) average": {
                            "from": f"{TableNames.SCENARIO}.name",
                            "to": quarters_average_join_condition,
                        }
                    }
                )
                .add_join_clause(
                    {
                        f"( {full_year_averages_table} ) full_year_average": {
                            "from": f"{TableNames.SCENARIO}.name",
                            "to": "full_year_average.scenario",
                        }
                    },
                    self.query_builder.JoinType.LEFT,
                )
                .add_join_clause(
                    {
                        f"( {comparison_table} ) comparison": {
                            "from": f"{TableNames.COMPANY}.id",
                            "to": comparison_join_condition,
                        }
                    },
                    self.query_builder.JoinType.LEFT,
                )
                .add_sql_where_equal_condition(where_conditions)
                .add_sql_order_by_condition(
                    [f"{TableNames.COMPANY}.name", f"{TableNames.SCENARIO}.name"],
                    self.query_builder.Order.ASC,
                )
                .build()
                .get_query()
            )
            result = self.session.execute(query).fetchall()
            return self.response_sql.process_query_list_results(result)

        except Exception as error:
            self.logger.error(error)
            return []

    def get_actuals_plus_budget_metrics_query(
        self, metric: str, years: list, filters: dict
    ) -> list:
        try:
            query = (
                self.query_builder.add_table_name(TableNames.COMPANY)
                .add_select_conditions(
                    [
                        f"{TableNames.COMPANY}.id",
                        f"{TableNames.COMPANY}.name",
                        f"{TableNames.SCENARIO}.name as scenario",
                        f"{TableNames.METRIC}.name as metric",
                        f"{TableNames.PERIOD}.period_name",
                        f"{TableNames.METRIC}.value",
                    ]
                )
                .add_join_clause(
                    {
                        f"{TableNames.SCENARIO}": {
                            "from": f"{TableNames.SCENARIO}.company_id",
                            "to": f"{TableNames.COMPANY}.id",
                        }
                    },
                )
                .add_join_clause(
                    {
                        f"{TableNames.PERIOD}": {
                            "from": f"{TableNames.PERIOD}.id",
                            "to": f"{TableNames.SCENARIO}.period_id",
                        }
                    },
                )
                .add_join_clause(
                    {
                        f"{TableNames.SCENARIO_METRIC}": {
                            "from": f"{TableNames.SCENARIO_METRIC}.scenario_id",
                            "to": f"{TableNames.SCENARIO}.id",
                        }
                    },
                )
                .add_join_clause(
                    {
                        f"{TableNames.METRIC}": {
                            "from": f"{TableNames.METRIC}.id",
                            "to": f"{TableNames.SCENARIO_METRIC}.metric_id",
                        }
                    },
                )
                .add_sql_where_equal_condition(
                    {
                        f"{TableNames.PERIOD}.period_name": [
                            "'Q1'",
                            "'Q2'",
                            "'Q3'",
                            "'Q4'",
                        ],
                        f"{TableNames.METRIC}.name": f"'{metric}'",
                        f"substring({TableNames.SCENARIO}.name from '.*([0-9]{{4}})$')::int": years,
                    }
                )
                .add_sql_group_by_condition(
                    [
                        f"{TableNames.COMPANY}.id",
                        f"{TableNames.SCENARIO}.name",
                        f"{TableNames.METRIC}.name",
                        f"{TableNames.PERIOD}.period_name",
                        f"{TableNames.METRIC}.value",
                    ]
                )
                .build()
                .get_query()
            )
            scenario_results = self.session.execute(query).fetchall()
            return self.response_sql.process_query_list_results(scenario_results)
        except Exception as error:
            self.logger.info(error)
            return []

    def get_base_functions_metric(
        self, filters: dict, scenario_type: str, years: list
    ) -> dict:
        metric_names = self.__get_metric_names_config()

        return {
            f"{scenario_type}-{metric}": {
                "function": self.get_base_metric_records,
                "arguments": self.__get_arguments(
                    filters, metric_names[metric], scenario_type, years
                ),
            }
            for metric in metric_names
        }

    def get_functions_metric(self, years: list, filters: dict) -> dict:
        metric_config = dict()
        metric_config.update(
            self.get_base_functions_metric(filters, ScenarioNames.ACTUALS, years)
        )
        metric_config.update(
            self.get_base_functions_metric(filters, ScenarioNames.BUDGET, years)
        )
        return metric_config

    def get_metric_records_with_base_scenarios(
        self, metric: str, scenario_type: str, years: list, filters: dict
    ) -> list:
        functions_metric = self.get_functions_metric(years, filters)
        metric_name = f"{scenario_type}-{metric}"
        print(metric_name)
        metric_config = functions_metric.get(metric_name)
        if not metric_config:
            raise AppError("Metric not found")

        function = metric_config["function"]
        return function(**metric_config["arguments"])

    def get_metric_records_by_quarters(
        self,
        report_type: str,
        metric: str,
        scenario_type: str,
        years: list,
        filters: dict,
    ) -> list:
        return self.get_metric_records_with_base_scenarios(
            metric, scenario_type, years, filters
        )
