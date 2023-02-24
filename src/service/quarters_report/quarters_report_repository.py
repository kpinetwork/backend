from base_exception import AppError
from app_names import TableNames, ScenarioNames, MetricNames
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
        self.periods = ["Q1", "Q2", "Q3", "Q4"]

    def __get_arguments(
        self,
        filters: dict,
        metric: str = None,
        scenario_type: str = None,
        years: list = [],
        report_type: str = None,
        period: str = None,
    ) -> dict:
        arguments = {"filters": filters}
        if metric:
            arguments["metric"] = metric
        if scenario_type:
            arguments["scenario_type"] = scenario_type
        if years:
            arguments["years"] = years
        if report_type:
            arguments["report_type"] = report_type
        if period:
            arguments["period"] = period
        return arguments

    def __get_metric_names_config(
        self,
    ) -> dict:
        return dict(
            (metric_alias, metric_name)
            for metric_name, metric_alias in METRICS_CONFIG_NAME.items()
        )

    def add_filters(self, **kwargs) -> dict:
        filters = dict()
        for k, v in kwargs.items():
            if k != "size_cohort" and k != "margin_group":
                values = [
                    f"'{element}'" for element in v if element and element.strip()
                ]
                filters[k] = values
        return filters

    def __get_periods_conditions_array(self, index: int = None) -> list:
        periods_list = self.periods if index is None else self.periods[: index + 1]
        return [f"'{period}'" for period in periods_list]

    def __get_tag_join_type(self, where_conditions: dict):
        tag_join_type = (
            self.query_builder.JoinType.JOIN
            if where_conditions.get("tag")
            else self.query_builder.JoinType.LEFT
        )
        return tag_join_type

    def __get_company_tag_join_clause(self):
        return {
            f"{TableNames.COMPANY_TAG}": {
                "from": f"{TableNames.COMPANY_TAG}.company_id",
                "to": f"{TableNames.COMPANY}.id",
            }
        }

    def __get_tag_join_clause(self):
        return {
            f"{TableNames.TAG}": {
                "from": f"{TableNames.TAG}.id",
                "to": f"{TableNames.COMPANY_TAG}.tag_id",
            }
        }

    def __get_base_where_conditions(
        self,
        metric: str,
        scenario_type: str,
        years: list,
        filters: dict,
        report_type: str = None,
        period: str = None,
    ) -> dict:
        from_count = len(scenario_type) + 2
        periods_condition = self.__get_periods_conditions_array()

        if report_type == "year_to_date":
            index = self.periods.index(period)
            periods_condition = self.__get_periods_conditions_array(index)
        where_conditions = {
            f"{TableNames.SCENARIO}.type": f"'{scenario_type}'",
            f"{TableNames.PERIOD}.period_name": periods_condition,
            f"{TableNames.METRIC}.name": f"'{metric}'",
            f"substring({TableNames.SCENARIO}.name from {from_count})::int": years,
        }
        where_conditions.update(filters)

        return where_conditions

    def __get_having_condition(
        self, table_name: str, report_type: str = None, period: str = None
    ) -> str:
        count = str(len(self.periods))
        if report_type == "year_to_date":
            count = str(self.periods.index(period) + 1)
        return f" HAVING count({table_name}.period_name ) = {count} "

    def get_base_query(
        self, select_conditions: list, where_conditions: dict, group_by_conditions: list
    ) -> str:
        tag_join_type = self.__get_tag_join_type(where_conditions)
        return (
            self.query_builder.add_table_name(TableNames.COMPANY)
            .add_select_conditions(select_conditions)
            .add_join_clause(
                self.__get_company_tag_join_clause(),
                tag_join_type,
            )
            .add_join_clause(
                self.__get_tag_join_clause(),
                tag_join_type,
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
            .add_sql_where_equal_condition(where_conditions)
            .add_sql_group_by_condition(group_by_conditions)
            .build()
            .get_query()
        )

    def get_quarters_total_query(
        self,
        metric: str,
        scenario_type: str,
        years: list,
        filters: dict,
        report_type: str = None,
        period: str = None,
    ) -> str:
        where_conditions = self.__get_base_where_conditions(
            metric, scenario_type, years, filters, report_type, period
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
        self,
        metric: str,
        scenario_type: str,
        years: list,
        filters: dict,
        report_type: str = None,
        period: str = None,
    ) -> str:
        where_conditions = self.__get_base_where_conditions(
            metric, scenario_type, years, filters, report_type, period
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
        self,
        metric: str,
        scenario_type: str,
        years: list,
        filters: dict,
        report_type: str = None,
        period: str = None,
    ) -> str:
        table_alias = "full_year"
        where_conditions = self.__get_base_where_conditions(
            metric, scenario_type, years, filters, report_type, period
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
        full_year_table = " ".join(
            [
                full_year_table,
                self.__get_having_condition(TableNames.PERIOD, report_type, period),
            ]
        )

        query = (
            self.query_builder.add_table_name(f"( {full_year_table} ) as {table_alias}")
            .add_select_conditions(
                [
                    f"{table_alias}.scenario",
                    f"AVG({table_alias}.total) as full_year_average",
                ]
            )
            .add_sql_group_by_condition([f"{table_alias}.scenario"])
            .build()
            .get_query()
        )

        return query

    def get_base_metric_records(
        self,
        metric: str,
        scenario_type: str,
        years: list,
        filters: dict,
        report_type: str = None,
        period: str = None,
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
            ]
            where_conditions = self.__get_base_where_conditions(
                metric, scenario_type, years, filters, report_type, period
            )

            full_year_table = self.get_quarters_total_query(
                metric, scenario_type, years, filters, report_type, period
            )
            quarters_averages_table = self.get_averages_by_quarters_query(
                metric, scenario_type, years, filters, report_type, period
            )
            full_year_averages_table = self.get_averages_of_quarters_total_query(
                metric, scenario_type, years, filters, report_type, period
            )
            full_year_join_condition = f"""total_quarters.company_id
            AND {TableNames.SCENARIO}.name = total_quarters.scenario """
            quarters_average_join_condition = f""" average.scenario
            AND {TableNames.PERIOD}.period_name = average.period """

            tag_join_type = self.__get_tag_join_type(where_conditions)
            query = (
                self.query_builder.add_table_name(f"{TableNames.COMPANY}")
                .add_select_conditions(columns)
                .add_join_clause(
                    self.__get_company_tag_join_clause(),
                    tag_join_type,
                )
                .add_join_clause(
                    self.__get_tag_join_clause(),
                    tag_join_type,
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
        self,
        metric: str,
        years: list,
        filters: dict,
        scenario_type: str,
        report_type: str,
        period: str = None,
    ) -> list:
        try:
            periods_condition = self.__get_periods_conditions_array()
            if report_type == "year_to_date":
                period_index = (
                    self.periods.index(period) if period is not None else None
                )
                periods_condition = self.__get_periods_conditions_array(period_index)
            where_conditions = {
                f"{TableNames.PERIOD}.period_name": periods_condition,
                f"{TableNames.METRIC}.name": f"'{metric}'",
                f"substring({TableNames.SCENARIO}.name from '.*([0-9]{{4}})$')::int": years,
            }
            where_conditions.update(filters)
            tag_join_type = self.__get_tag_join_type(where_conditions)
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
                    self.__get_company_tag_join_clause(),
                    tag_join_type,
                )
                .add_join_clause(
                    self.__get_tag_join_clause(),
                    tag_join_type,
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
                .add_sql_where_equal_condition(where_conditions)
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
        self,
        filters: dict,
        scenario_type: str,
        years: list,
        report_type: str = None,
        period: str = None,
    ) -> dict:
        metric_names = self.__get_metric_names_config()

        return {
            f"{scenario_type}-{metric}": {
                "function": self.get_base_metric_records,
                "arguments": self.__get_arguments(
                    filters,
                    metric_names[metric],
                    scenario_type,
                    years,
                    report_type,
                    period,
                ),
            }
            for metric in metric_names
        }

    def __get_base_table_for_calculated_metrics(
        self, select_value: list, main_table: str
    ):
        table_alias = "main_table"
        conditions = [
            f"{table_alias}.id",
            f"{table_alias}.scenario",
            f"{table_alias}.metric",
            f"{table_alias}.year",
            f"{table_alias}.period_name",
        ]
        select_conditions = conditions.copy()
        select_conditions.extend(select_value)
        conditions.extend([f"{table_alias}.value"])
        query = (
            self.query_builder.add_table_name(f"({main_table}) as main_table")
            .add_select_conditions(select_conditions)
            .add_sql_group_by_condition(conditions)
            .build()
            .get_query()
        )
        return query

    def __get_full_year_table_calculated_metrics(self, select_value, main_table):
        conditions = ["full_year.id", "full_year.scenario", "full_year.year"]
        select_conditions = conditions.copy()
        select_conditions.extend(
            [
                "COUNT(full_year.period_name) as quarters_count",
                "SUM(full_year.value) as full_year",
            ]
        )
        base_table = self.__get_base_table_for_calculated_metrics(
            select_value, main_table
        )
        query = (
            self.query_builder.add_table_name(f"({base_table}) as full_year")
            .add_select_conditions(select_conditions)
            .add_sql_group_by_condition(conditions)
            .build()
            .get_query()
        )
        return query

    def __get_quarters_average_table_calculated_metrics(self, select_value, main_table):
        conditions = ["quarters_average.scenario", "quarters_average.period_name"]
        select_conditions = conditions.copy()
        select_conditions.extend(["AVG(quarters_average.value) as average"])
        base_table = self.__get_base_table_for_calculated_metrics(
            select_value, main_table
        )
        query = (
            self.query_builder.add_table_name(f"({base_table}) as quarters_average")
            .add_select_conditions(select_conditions)
            .add_sql_group_by_condition(conditions)
            .build()
            .get_query()
        )
        return query

    def __get_full_year_average_base_query(
        self, base_table, select_conditions, conditions
    ) -> str:
        return (
            self.query_builder.add_table_name(f"({base_table}) as sum_quarters")
            .add_select_conditions(select_conditions)
            .add_sql_group_by_condition(conditions)
            .build()
            .get_query()
        )

    def __get_full_year_avg_subquery(
        self, select_value, main_table, report_type: str = None, period: str = None
    ):
        conditions = ["sum_quarters.scenario"]
        select_conditions = conditions.copy()
        select_conditions.extend(["SUM(sum_quarters.value) as total"])
        conditions.extend(["sum_quarters.id"])
        base_table = self.__get_base_table_for_calculated_metrics(
            select_value, main_table
        )
        query = self.__get_full_year_average_base_query(
            base_table, select_conditions, conditions
        )
        having_condition = self.__get_having_condition(
            "sum_quarters", report_type, period
        )
        return query + having_condition

    def __get_full_year_table_base_query(
        self, sum_table, select_conditions, conditions
    ):
        return (
            self.query_builder.add_table_name(f"({sum_table}) as full_year")
            .add_select_conditions(select_conditions)
            .add_sql_group_by_condition(conditions)
            .build()
            .get_query()
        )

    def __get_full_year_table__calculated_metrics(
        self, select_value, main_table, report_type: str = None, period: str = None
    ):
        conditions = ["full_year.scenario"]
        select_conditions = conditions.copy()
        select_conditions.extend(["AVG(full_year.total) as full_year_average"])
        sum_table = self.__get_full_year_avg_subquery(
            select_value, main_table, report_type, period
        )
        query = self.__get_full_year_table_base_query(
            sum_table, select_conditions, conditions
        )
        return query

    def get_calculated_metrics_with_base_scenarios(
        self,
        select_value: list,
        scenario: str,
        metric: str,
        years: list,
        filters: dict,
        report_type: str = None,
        period: str = None,
    ):
        try:
            table_alias = "main_table"
            conditions = [
                f"{table_alias}.id",
                f"{table_alias}.name",
                f"{table_alias}.scenario",
                f"{table_alias}.metric",
                f"{table_alias}.year",
                f"{table_alias}.period_name",
                "total_quarters.full_year",
                "total_quarters.quarters_count",
                "average.average",
                "full_year_average.full_year_average",
            ]
            select_conditions = conditions.copy()
            select_conditions.extend(select_value)
            conditions.extend([f"{table_alias}.value"])
            average_quarters_table_join_condition = """
            average.scenario AND
            main_table.period_name = average.period_name"""
            full_year_table_join_condition = """
            total_quarters.id AND
            main_table.scenario = total_quarters.scenario
            """
            scenario_condition = {f"{TableNames.SCENARIO}.type": f"'{scenario}'"}
            main_table = self.get_actuals_plus_main_table_subquery(
                metric, years, filters, report_type, period, scenario_condition
            )
            full_year_table = self.__get_full_year_table_calculated_metrics(
                select_value, main_table
            )

            average_quarters_table = (
                self.__get_quarters_average_table_calculated_metrics(
                    select_value, main_table
                )
            )

            average_full_year_table = self.__get_full_year_table__calculated_metrics(
                select_value, main_table, report_type, period
            )
            query = (
                self.query_builder.add_table_name(f"({main_table}) as main_table")
                .add_select_conditions(select_conditions)
                .add_join_clause(
                    {
                        f"({full_year_table}) total_quarters": {
                            "from": f"{table_alias}.id",
                            "to": full_year_table_join_condition,
                        }
                    },
                )
                .add_join_clause(
                    {
                        f"({average_quarters_table}) average": {
                            "from": f"{table_alias}.scenario",
                            "to": average_quarters_table_join_condition,
                        }
                    },
                )
                .add_join_clause(
                    {
                        f"({average_full_year_table}) full_year_average": {
                            "from": f"{table_alias}.scenario",
                            "to": "full_year_average.scenario",
                        }
                    },
                    self.query_builder.JoinType.LEFT,
                )
                .add_sql_group_by_condition(conditions)
                .build()
                .get_query()
            )
            result = self.session.execute(query).fetchall()
            return self.response_sql.process_query_list_results(result)
        except Exception as error:
            self.logger.info(error)
            return []

    # queries to get actuals + budget calculated metrics
    def __get_no_base_metrics(
        self,
        select_value_condition: list,
        metric: str,
        years: list,
        report_type: str,
        period: str,
        filters: dict,
    ) -> list:
        try:
            table_alias = "main_table"
            columns = [
                f"{table_alias}.id",
                f"{table_alias}.name",
                f"{table_alias}.scenario",
                f"{table_alias}.metric",
                f"{table_alias}.year",
                f"{table_alias}.period_name",
            ]
            select_options = columns.copy()
            select_options.extend(select_value_condition)
            columns.append(
                f"{table_alias}.value",
            )
            table = self.get_actuals_plus_main_table_subquery(
                metric, years, filters, report_type, period
            )
            query = (
                self.query_builder.add_table_name(f"( {table} ) as {table_alias}")
                .add_select_conditions(select_options)
                .add_sql_group_by_condition(columns)
                .build()
                .get_query()
            )
            result = self.session.execute(query).fetchall()
            return self.response_sql.process_query_list_results(result)
        except Exception as error:
            self.logger.info(error)
            raise error

    # get main table to main metric calculated metric
    def get_actuals_plus_main_table_subquery(
        self,
        metric: str,
        years: list,
        filters: dict,
        report_type: str,
        period: str = None,
        scenario_condition: dict = dict(),
    ) -> list:
        periods_condition = self.__get_periods_conditions_array()
        if report_type == "year_to_date":
            period_index = self.periods.index(period) if period is not None else None
            periods_condition = self.__get_periods_conditions_array(period_index)
        where_conditions = {
            f"{TableNames.PERIOD}.period_name": periods_condition,
            f"{TableNames.METRIC}.name": f"'{metric}'",
            f"substring({TableNames.SCENARIO}.name from '.*([0-9]{{4}})$')::int": years,
        }
        where_conditions.update(filters)
        if scenario_condition:
            where_conditions.update(scenario_condition)

        tag_join_type = self.__get_tag_join_type(where_conditions)
        query = (
            self.query_builder.add_table_name(TableNames.COMPANY)
            .add_select_conditions(
                [
                    f"{TableNames.COMPANY}.id",
                    f"{TableNames.COMPANY}.name",
                    f"{TableNames.SCENARIO}.name as scenario",
                    f"{TableNames.METRIC}.name as metric",
                    f" substring({TableNames.SCENARIO}.name from '.*([0-9]{{4}})$')::int as year",
                    f"{TableNames.PERIOD}.period_name",
                    f"{TableNames.METRIC}.value",
                ]
            )
            .add_join_clause(
                self.__get_company_tag_join_clause(),
                tag_join_type,
            )
            .add_join_clause(
                self.__get_tag_join_clause(),
                tag_join_type,
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
            .add_sql_where_equal_condition(where_conditions)
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
        return query

    # submetric subquery calculated metric
    def __get_subquery_for_submetric(
        self,
        metric: str,
    ) -> str:

        return (
            self.query_builder.add_table_name(TableNames.COMPANY)
            .add_select_conditions(
                [
                    f"NULLIF ({TableNames.METRIC}.value,0)",
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
                    f"{TableNames.COMPANY}.id": "main_table.id",
                    f"{TableNames.METRIC}.name": f"'{metric}'",
                    f"{TableNames.PERIOD}.period_name": "main_table.period_name",
                    f"{TableNames.SCENARIO}.name": "main_table.scenario",
                }
            )
            .add_sql_group_by_condition(
                [
                    f"{TableNames.METRIC}.value",
                ]
            )
            .build()
            .get_query()
        )

    def get_gross_profit(
        self,
        years: list,
        filters: dict,
        scenario_type: str = "actuals_budget",
        report_type: str = None,
        period: str = None,
    ) -> list:
        try:
            subquery = self.__get_subquery_for_submetric("Cost of goods")
            select_value = [
                f"main_table.value - ({subquery}) as value",
            ]
            if scenario_type == "actuals_budget":
                return self.__get_no_base_metrics(
                    select_value, "Revenue", years, report_type, period, filters
                )
            return self.get_calculated_metrics_with_base_scenarios(
                select_value,
                scenario_type,
                "Revenue",
                years,
                filters,
                report_type,
                period,
            )
        except Exception as error:
            self.logger.info(error)
            return []

    def get_gross_margin(
        self,
        years: list,
        filters: dict,
        scenario_type: str = "actuals_budget",
        report_type: str = None,
        period: str = None,
    ) -> list:
        try:
            subquery = self.__get_subquery_for_submetric("Revenue")
            select_value = [
                f"(1 - (main_table.value / ({subquery}))) * 100 as value",
            ]
            if scenario_type == "actuals_budget":
                return self.__get_no_base_metrics(
                    select_value, "Cost_of_goods", years, report_type, period, filters
                )
            return self.get_calculated_metrics_with_base_scenarios(
                select_value,
                scenario_type,
                "Cost of goods",
                years,
                filters,
                report_type,
                period,
            )
        except Exception as error:
            self.logger.info(error)
            return []

    def get_revenue_per_employee(
        self,
        years: list,
        filters: dict,
        scenario_type: str = "actuals_budget",
        report_type: str = None,
        period: str = None,
    ) -> list:
        try:
            metric = "Run rate revenue"
            subquery = self.__get_subquery_for_submetric("Headcount")
            select_value = [
                f"(main_table.value / ({subquery})) * 1000000 as value",
            ]
            if scenario_type == "actuals_budget":
                return self.__get_no_base_metrics(
                    select_value,
                    metric,
                    years,
                    report_type,
                    period,
                    filters,
                )
            return self.get_calculated_metrics_with_base_scenarios(
                select_value,
                scenario_type,
                metric,
                years,
                filters,
                report_type,
                period,
            )
        except Exception as error:
            self.logger.info(error)
            return []

    def get_opex_as_revenue(
        self,
        years: list,
        filters: dict,
        scenario_type: str = "actuals_budget",
        report_type: str = None,
        period: str = None,
    ) -> list:
        try:
            sales_and_marketing = self.__get_subquery_for_submetric(
                MetricNames.SALES_AND_MARKETING
            )
            research_and_dev = self.__get_subquery_for_submetric(
                MetricNames.RESEARCH_AND_DEVELOPMENT
            )
            general_and_admin = self.__get_subquery_for_submetric(
                MetricNames.GENERAL_AND_ADMINISTRATION
            )
            revenue = self.__get_subquery_for_submetric("Revenue")
            sum_factors = f"({sales_and_marketing}) + ({research_and_dev}) + ({general_and_admin})"
            select_value = [
                f" (main_table.value + {sum_factors}) / ({revenue}) * 100 as value",
            ]
            if scenario_type == "actuals_budget":
                return self.__get_no_base_metrics(
                    select_value,
                    "Other operating expenses",
                    years,
                    report_type,
                    period,
                    filters,
                )
            return self.get_calculated_metrics_with_base_scenarios(
                select_value,
                scenario_type,
                "Other operating expenses",
                years,
                filters,
                report_type,
                period,
            )
        except Exception as error:
            self.logger.info(error)
            return []

    def get_debt_ebitda(
        self,
        years: list,
        filters: dict,
        scenario_type: str = "actuals_budget",
        report_type: str = None,
        period: str = None,
    ) -> list:
        try:
            subquery = self.__get_subquery_for_submetric("Ebitda")
            select_value = [
                f"(main_table.value / ({subquery})) as value",
            ]
            if scenario_type == "actuals_budget":
                return self.__get_no_base_metrics(
                    select_value, "Long term debt", years, report_type, period, filters
                )
            return self.get_calculated_metrics_with_base_scenarios(
                select_value,
                scenario_type,
                "Long term debt",
                years,
                filters,
                report_type,
                period,
            )
        except Exception as error:
            self.logger.info(error)
            return []

    def get_gross_retention(
        self,
        years: list,
        filters: dict,
        scenario_type: str = "actuals_budget",
        report_type: str = None,
        period: str = None,
    ) -> list:
        try:
            subquery = self.__get_subquery_for_submetric("Run rate revenue")
            select_value = [
                f"(1 - (main_table.value / ({subquery}))) * 100 as value",
            ]
            if scenario_type == "actuals_budget":
                return self.__get_no_base_metrics(
                    select_value,
                    "Losses and downgrades",
                    years,
                    report_type,
                    period,
                    filters,
                )
            return self.get_calculated_metrics_with_base_scenarios(
                select_value,
                scenario_type,
                "Losses and downgrades",
                years,
                filters,
                report_type,
                period,
            )
        except Exception as error:
            self.logger.info(error)
            return []

    def get_metric_as_percentage_of_revenue(
        self,
        years: list,
        metric: str,
        filters: dict,
        scenario_type: str = "actuals_budget",
        report_type: str = None,
        period: str = None,
    ) -> list:
        try:
            subquery = self.__get_subquery_for_submetric("Revenue")
            select_value = [
                f"main_table.value * 100 / ({subquery}) as value",
            ]
            if scenario_type == "actuals_budget":
                return self.__get_no_base_metrics(
                    select_value, metric, years, report_type, period, filters
                )
            return self.get_calculated_metrics_with_base_scenarios(
                select_value, scenario_type, metric, years, filters, report_type, period
            )
        except Exception as error:
            self.logger.info(error)
            return []

    def get_metric_ratio(
        self,
        years: list,
        dividend: str,
        divisor: str,
        filters: dict,
        scenario_type: str = "actuals_budget",
        report_type: str = None,
        period: str = None,
    ) -> list:
        try:
            subquery = self.__get_subquery_for_submetric(divisor)
            select_value = [
                f"main_table.value / ({subquery}) as value",
            ]
            if scenario_type == "actuals_budget":
                return self.__get_no_base_metrics(
                    select_value, dividend, years, report_type, period, filters
                )
            return self.get_calculated_metrics_with_base_scenarios(
                select_value,
                scenario_type,
                dividend,
                years,
                filters,
                report_type,
                period,
            )
        except Exception as error:
            self.logger.info(error)
            return []

    def get_actuals_vs_budget_metric(
        self,
        years: list,
        metric: str,
        filters: dict,
        scenario_type: str = "actuals_budget",
        report_type: str = None,
        period: str = None,
    ) -> list:
        try:
            subquery = self.__get_subquery_for_submetric("Revenue")
            select_value = [
                f"main_table.value / ({subquery}) as value",
            ]
            if scenario_type == "actuals_budget":
                return []
            return self.get_calculated_metrics_with_base_scenarios(
                select_value,
                "Budget",
                metric,
                years,
                filters,
                report_type,
                period,
            )
        except Exception as error:
            self.logger.info(error)
            return []

    def get_ebitda_margin_metric(
        self,
        years: list,
        filters: dict,
        scenario_type: str = "actuals_budget",
        report_type: str = None,
        period: str = None,
    ) -> list:
        return self.get_metric_as_percentage_of_revenue(
            years, "Ebitda", filters, scenario_type, report_type, period
        )

    def __get_ratio_arguments(
        self,
        years: list,
        filters: dict,
        scenario_type: str = None,
        dividend: str = None,
        divisor: str = None,
        report_type: str = None,
        period: str = None,
    ) -> dict:
        arguments = {"filters": filters}
        if dividend:
            arguments["dividend"] = dividend
        if divisor:
            arguments["divisor"] = divisor
        if years:
            arguments["years"] = years
        if scenario_type:
            arguments["scenario_type"] = scenario_type
        if report_type:
            arguments["report_type"] = report_type
        if period:
            arguments["period"] = period
        return arguments

    def get_actuals_plus_budget_base_functions_metric(
        self,
        filters: dict,
        years: list,
        report_type: str = None,
        period: str = None,
        scenario_type: str = "actuals_budget",
    ) -> dict:
        metric_names = self.__get_metric_names_config()

        return {
            f"{metric}": {
                "function": self.get_actuals_plus_budget_metrics_query,
                "arguments": self.__get_arguments(
                    metric=metric_names[metric],
                    years=years,
                    filters=filters,
                    scenario_type=scenario_type,
                    report_type=report_type,
                    period=period,
                ),
            }
            for metric in metric_names
        }

    def __get_gross_profit_functions_metric(
        self, years: list, filters: dict, report_type: str, period: str
    ) -> dict:
        return {
            "gross_profit": {
                "function": self.get_gross_profit,
                "arguments": self.__get_arguments(
                    years=years, filters=filters, report_type=report_type, period=period
                ),
            }
        }

    def __get_actuals_vs_budget_functions_metric(
        self,
        years: list,
        filters: dict,
        scenario_type: str,
        report_type: str,
        period: str,
    ) -> dict:
        return {
            "revenue_vs_budget": {
                "function": self.get_actuals_vs_budget_metric,
                "arguments": self.__get_arguments(
                    years=years,
                    filters=filters,
                    report_type=report_type,
                    period=period,
                    scenario_type=scenario_type,
                    metric="Revenue",
                ),
            },
            "ebitda_vs_budget": {
                "function": self.get_actuals_vs_budget_metric,
                "arguments": self.__get_arguments(
                    years=years,
                    filters=filters,
                    report_type=report_type,
                    period=period,
                    scenario_type=scenario_type,
                    metric="Ebitda",
                ),
            },
        }

    def get_actuals_plus_budget_functions_metric(
        self, years: list, filters: dict, report_type: str = None, period: str = None
    ) -> dict:
        metric_config = {
            "ebitda_margin": {
                "function": self.get_ebitda_margin_metric,
                "arguments": self.__get_arguments(
                    years=years, filters=filters, report_type=report_type, period=period
                ),
            },
            "gross_margin": {
                "function": self.get_gross_margin,
                "arguments": self.__get_arguments(
                    years=years, filters=filters, report_type=report_type, period=period
                ),
            },
            "sales_and_marketing": {
                "function": self.get_metric_as_percentage_of_revenue,
                "arguments": self.__get_arguments(
                    years=years,
                    metric=MetricNames.SALES_AND_MARKETING,
                    filters=filters,
                    report_type=report_type,
                    period=period,
                ),
            },
            "general_and_admin": {
                "function": self.get_metric_as_percentage_of_revenue,
                "arguments": self.__get_arguments(
                    years=years,
                    filters=filters,
                    metric=MetricNames.GENERAL_AND_ADMINISTRATION,
                    report_type=report_type,
                    period=period,
                ),
            },
            "research_and_development": {
                "function": self.get_metric_as_percentage_of_revenue,
                "arguments": self.__get_arguments(
                    years=years,
                    metric=MetricNames.RESEARCH_AND_DEVELOPMENT,
                    filters=filters,
                    report_type=report_type,
                    period=period,
                ),
            },
            "clv_cac_ratio": {
                "function": self.get_metric_ratio,
                "arguments": self.__get_ratio_arguments(
                    years,
                    filters,
                    dividend="CLV",
                    divisor="CAC",
                    report_type=report_type,
                    period=period,
                ),
            },
            "cac_ratio": {
                "function": self.get_metric_ratio,
                "arguments": self.__get_ratio_arguments(
                    years,
                    filters,
                    dividend="CAC",
                    divisor="CAV",
                    report_type=report_type,
                    period=period,
                ),
            },
            "revenue_per_employee": {
                "function": self.get_revenue_per_employee,
                "arguments": self.__get_arguments(
                    years=years, filters=filters, report_type=report_type, period=period
                ),
            },
            "opex_as_revenue": {
                "function": self.get_opex_as_revenue,
                "arguments": self.__get_arguments(
                    years=years, filters=filters, report_type=report_type, period=period
                ),
            },
            "debt_ebitda": {
                "function": self.get_debt_ebitda,
                "arguments": self.__get_arguments(
                    years=years, filters=filters, report_type=report_type, period=period
                ),
            },
        }
        metric_config.update(
            self.get_actuals_plus_budget_base_functions_metric(
                years=years, filters=filters, report_type=report_type, period=period
            )
        )
        metric_config.update(
            self.__get_gross_profit_functions_metric(
                years, filters, report_type=report_type, period=period
            )
        )
        # metric_config.update(self.__get_actuals_vs_budget_functions_metric(years, filters))

        return metric_config

    def get_quarters_year_to_year_records(
        self,
        report_type: str,
        metric: str,
        scenario_type: str,
        years: list,
        period: str,
        filters: dict,
    ) -> list:
        functions_metric = self.get_actuals_plus_budget_functions_metric(
            years, filters, report_type, period
        )
        metric_config = functions_metric.get(metric)
        if not metric_config:
            raise AppError("Metric not found")

        function = metric_config["function"]
        return function(**metric_config["arguments"])

    def get_functions_metric(
        self,
        scenario: str,
        years: list,
        filters: dict,
        report_type: str = None,
        period: str = None,
    ) -> dict:
        metric_config = {
            "ebitda_margin": {
                "function": self.get_ebitda_margin_metric,
                "arguments": self.__get_arguments(
                    filters,
                    scenario_type=scenario,
                    years=years,
                    report_type=report_type,
                    period=period,
                ),
            },
            "gross_margin": {
                "function": self.get_gross_margin,
                "arguments": self.__get_arguments(
                    filters,
                    scenario_type=scenario,
                    years=years,
                    report_type=report_type,
                    period=period,
                ),
            },
            "sales_and_marketing": {
                "function": self.get_metric_as_percentage_of_revenue,
                "arguments": self.__get_arguments(
                    filters,
                    years=years,
                    scenario_type=scenario,
                    metric=MetricNames.SALES_AND_MARKETING,
                    report_type=report_type,
                    period=period,
                ),
            },
            "general_and_admin": {
                "function": self.get_metric_as_percentage_of_revenue,
                "arguments": self.__get_arguments(
                    filters,
                    years=years,
                    scenario_type=scenario,
                    metric=MetricNames.GENERAL_AND_ADMINISTRATION,
                    report_type=report_type,
                    period=period,
                ),
            },
            "research_and_development": {
                "function": self.get_metric_as_percentage_of_revenue,
                "arguments": self.__get_arguments(
                    filters,
                    years=years,
                    scenario_type=scenario,
                    metric=MetricNames.RESEARCH_AND_DEVELOPMENT,
                    report_type=report_type,
                    period=period,
                ),
            },
            "clv_cac_ratio": {
                "function": self.get_metric_ratio,
                "arguments": self.__get_ratio_arguments(
                    years,
                    filters,
                    scenario_type=scenario,
                    dividend="CLV",
                    divisor="CAC",
                    report_type=report_type,
                    period=period,
                ),
            },
            "cac_ratio": {
                "function": self.get_metric_ratio,
                "arguments": self.__get_ratio_arguments(
                    years,
                    filters,
                    scenario_type=scenario,
                    dividend="CAC",
                    divisor="CAV",
                    report_type=report_type,
                    period=period,
                ),
            },
            "opex_as_revenue": {
                "function": self.get_opex_as_revenue,
                "arguments": self.__get_arguments(
                    years=years,
                    filters=filters,
                    scenario_type=scenario,
                    report_type=report_type,
                    period=period,
                ),
            },
            "revenue_per_employee": {
                "function": self.get_revenue_per_employee,
                "arguments": self.__get_arguments(
                    years=years,
                    filters=filters,
                    scenario_type=scenario,
                    report_type=report_type,
                    period=period,
                ),
            },
            "debt_ebitda": {
                "function": self.get_debt_ebitda,
                "arguments": self.__get_arguments(
                    years=years,
                    filters=filters,
                    scenario_type=scenario,
                    report_type=report_type,
                    period=period,
                ),
            },
            "gross_profit": {
                "function": self.get_gross_profit,
                "arguments": self.__get_arguments(
                    years=years,
                    filters=filters,
                    scenario_type=scenario,
                    report_type=report_type,
                    period=period,
                ),
            },
        }
        metric_config.update(
            self.get_base_functions_metric(
                filters, ScenarioNames.ACTUALS, years, report_type, period
            )
        )
        metric_config.update(
            self.get_base_functions_metric(
                filters, ScenarioNames.BUDGET, years, report_type, period
            )
        )
        metric_config.update(
            self.__get_actuals_vs_budget_functions_metric(
                years, filters, scenario, report_type, period
            )
        )
        return metric_config

    def get_metric_records_with_base_scenarios(
        self,
        metric: str,
        scenario_type: str,
        years: list,
        filters: dict,
        report_type: str = None,
        period: str = None,
    ) -> list:
        functions_metric = self.get_functions_metric(
            scenario_type, years, filters, report_type, period
        )
        metric_names = list(self.__get_metric_names_config().keys())
        metric_name = f"{scenario_type}-{metric}" if metric in metric_names else metric
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
        period: str,
        filters: dict,
    ) -> list:
        return self.get_metric_records_with_base_scenarios(
            metric, scenario_type, years, filters, report_type, period
        )
