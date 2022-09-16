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

    def add_company_filters(self, **kwargs) -> dict:
        filters = dict()
        for k, v in kwargs.items():
            if k != "size_cohort" and k != "margin_group":
                values = [
                    f"'{element}'" for element in v if element and element.strip()
                ]
                filters[f"{TableNames.COMPANY}.{k}"] = values
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

    def __get_scenario_metric_field(self, record: dict, year: int) -> dict:
        if record.get("metric") in METRICS_CONFIG_NAME:
            record_year = record.get("year", year) - year
            metric_name = self.__get_metric_name_year(
                record.get("metric"), record.get("scenario"), record_year
            )
            return {metric_name: record.get("value")}
        return dict()

    def __get_scenario_values(
        self, scenario: str, years: list, filters: dict, metrics: list = []
    ) -> dict:
        try:
            filters.update(
                {
                    f"{TableNames.SCENARIO}.name": self.__get_scenario_name_with_year(
                        scenario, years
                    )
                }
            )
            if metrics:
                filters.update(
                    {f"{TableNames.METRIC}.name": self.__get_sql_value_names(metrics)}
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
                .add_sql_where_equal_condition(filters)
                .build()
                .get_query()
            )

            scenario_results = self.session.execute(query).fetchall()
            return self.response_sql.process_query_list_results(scenario_results)
        except Exception as error:
            self.logger.info(error)
            raise error

    def process_scenario_values(
        self, year: int, records: list, need_company_fields: bool = False
    ) -> dict:
        data = defaultdict(dict)
        for record in records:
            self.__process_company_fields(
                data[record["id"]], record, need_company_fields
            )
            data[record["id"]].update(self.__get_scenario_metric_field(record, year))
        return data

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
