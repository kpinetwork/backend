from collections import defaultdict
from base_metrics_config_name import METRICS_CONFIG_NAME
from app_names import TableNames, MetricNames
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL
from sqlalchemy.orm import Session


class BaseMetricsRepository:
    def __init__(
        self,
        logger,
        session: Session,
        query_builder: QuerySQLBuilder,
        response_sql: ResponseSQL,
    ) -> None:
        self.session = session
        self.query_builder = query_builder
        self.response_sql = response_sql
        self.logger = logger
        self.fields = ["id", "name", "sector", "vertical", "inves_profile_name"]

    def add_filters(self, **kwargs) -> dict:
        filters = dict()
        for k, v in kwargs.items():
            if k != "size_cohort" and k != "margin_group":
                values = [
                    f"'{element}'" for element in v if element and element.strip()
                ]
                filters[k] = values
        return filters

    def __get_scenario_name_with_year(self, scenario: str, years: list) -> list:
        return [f"'{scenario}-{year}'" for year in years]

    def __get_sql_value_names(self, values: list) -> list:
        return [f"'{value}'" for value in values]

    def __get_metric_name_year(self, metric: str, scenario: str, year: int) -> str:
        name = f"{scenario.lower()}_{METRICS_CONFIG_NAME[metric]}"
        if year < 0:
            return f"prior_{name}"
        if year > 0:
            return f"next_{name}"
        return name

    def __process_company_fields(
        self, record: dict, company_data: dict, need_company_fields: bool
    ) -> None:
        if need_company_fields and "name" not in record:
            record.update(
                {
                    field: value
                    for field, value in company_data.items()
                    if field in self.fields
                }
            )

    def __is_full_year(self, record: dict) -> bool:
        return (
            record.get("count_period") == 1 and record.get("period") == "Full-year"
        ) or (record.get("count_period") == 4 and record.get("period") == "Quarters")

    def __get_scenario_metric_field(self, record: dict, year: int) -> dict:
        if record.get("metric") in METRICS_CONFIG_NAME and self.__is_full_year(record):
            record_year = record.get("year", year) - year
            metric_name = self.__get_metric_name_year(
                record.get("metric"), record.get("scenario"), record_year
            )
            if record.get("period") == "Quarters" and record.get("count_period") == 4:
                return {f"{metric_name}_quarters": record.get("total")}
            return {metric_name: record.get("total")}
        return dict()

    def __get_case_for_time_periods(self) -> str:
        return """
        CASE
            WHEN {period_table}.period_name = 'Full-year' THEN 'Full-year'
            ELSE 'Quarters'
        END AS period
        """.format(
            period_table=TableNames.PERIOD
        )

    def __get_scenario_values_subquery(
        self, scenario: str, years: list, filters: dict, metrics: list = []
    ) -> str:
        filters.update(
            {
                f"{TableNames.SCENARIO}.name": self.__get_scenario_name_with_year(
                    scenario, years
                ),
                f"{TableNames.COMPANY}.is_public": True,
            }
        )
        if metrics:
            filters.update(
                {f"{TableNames.METRIC}.name": self.__get_sql_value_names(metrics)}
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
                    self.__get_case_for_time_periods(),
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
            + f"""AND {TableNames.PERIOD}.period_name = 'Full-year'
            OR {TableNames.PERIOD}.period_name IN ('Q1', 'Q2', 'Q3', 'Q4')"""
            + query[index:]
        )
        return new_query

    def __get_scenario_values_by_period_subquery(
        self, scenario: str, years: list, filters: dict, metrics: list = []
    ) -> str:
        subquery = self.__get_scenario_values_subquery(
            scenario, years, filters, metrics
        )
        return self.__add_period_name_where_condition(subquery)

    def __get_scenario_values(
        self, scenario: str, years: list, filters: dict, metrics: list = []
    ) -> dict:
        try:
            columns = [
                "full_year.id",
                "full_year.name",
                "full_year.sector",
                "full_year.vertical",
                "full_year.inves_profile_name",
                "full_year.scenario",
                "full_year.year",
                "full_year.metric",
                "full_year.period",
            ]
            select_condition = columns.copy()
            select_condition.extend(
                [
                    "SUM (full_year.value) as total",
                    "COUNT(full_year.period) as count_period",
                ]
            )
            table = self.__get_scenario_values_by_period_subquery(
                scenario, years, filters, metrics
            )
            query = (
                self.query_builder.add_table_name(f"( {table} ) as full_year")
                .add_select_conditions(select_condition)
                .add_sql_where_equal_condition(
                    {"period": ["'Full-year'", "'Quarters'"]}
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

    def __find_substring(self, substring, string_list):
        return [s for s in string_list if substring in s]

    def __update_with_quarter_or_full_year_metric(self, company_data: dict) -> None:
        metrics = company_data.keys()
        metrics_with_quarters = self.__find_substring("quarter", metrics)
        for metric in metrics_with_quarters:
            metric_name = metric.split("_quarter")[0]
            quarter_metric = company_data.pop(metric)
            if metric_name not in metrics:
                company_data.update({metric_name: quarter_metric})

    def process_scenario_values(
        self, year: int, records: list, need_company_fields: bool = False
    ) -> dict:
        data = defaultdict(dict)
        for record in records:
            company_data = data[record["id"]]
            self.__process_company_fields(
                data[record["id"]], record, need_company_fields
            )
            data[record["id"]].update(self.__get_scenario_metric_field(record, year))
            self.__update_with_quarter_or_full_year_metric(company_data)
        return dict(data)

    def get_budget_values(
        self, base_year: int, years: list, filters: dict, metrics: list = []
    ) -> dict:
        return self.process_scenario_values(
            base_year,
            self.__get_scenario_values("Budget", years, filters, metrics),
            True,
        )

    def get_actuals_values(self, year: int, filters: dict, metrics: list = []) -> dict:
        return self.process_scenario_values(
            year, self.__get_scenario_values("Actuals", [year], filters, metrics), True
        )

    def get_prior_year_revenue_values(self, base_year: int, filters) -> dict:
        metrics = [
            MetricNames.REVENUE,
            MetricNames.RUN_RATE_REVENUE,
            MetricNames.NEW_BOOKINGS,
        ]
        return self.process_scenario_values(
            base_year,
            self.__get_scenario_values("Actuals", [base_year - 1], filters, metrics),
            False,
        )
