from uuid import uuid4
from decimal import Decimal
from datetime import datetime
from base_exception import AppError
from app_names import TableNames, ScenarioNames, MetricNames


class ScenarioService:
    def __init__(self, session, query_builder, logger):
        self.session = session
        self.query_builder = query_builder
        self.logger = logger

    def __get_name_values_from_dict(self, **data) -> tuple:
        names = [*data]
        values = []

        for name in names:
            value = data[name]
            if isinstance(value, str):
                values.append(f"'{value}'")
            else:
                values.append(str(value))
        return (names, values)

    def __get_insert_query(self, table: str, **data) -> str:
        names, values = self.__get_name_values_from_dict(**data)
        return """
            INSERT INTO {table} ({fields})
            VALUES ({values});
        """.format(
            table=table, fields=",".join(names), values=",".join(values)
        )

    def __insert_query_time_period(self, year: int, period_id: str) -> str:
        return self.__get_insert_query(
            "time_period",
            id=period_id,
            start_at=f"{year}-01-01",
            end_at=f"{year}-12-31",
        )

    def __insert_query_metric(
        self,
        metric_id: str,
        metric: str,
        value: float,
        period_id: str,
        company_id: str,
        data_type: str = "currency",
    ) -> str:
        query = self.__get_insert_query(
            "metric",
            id=metric_id,
            name=metric,
            value=value,
            type="standard",
            data_type=data_type,
            period_id=period_id,
            company_id=company_id,
        )
        if data_type == "currency":
            currency_query = self.__get_insert_query(
                "currency_metric",
                id=str(uuid4()),
                currency_iso_code="USD",
                metric_id=metric_id,
            )
            query = """
            {metric_query}
            {currency}
            """.format(
                metric_query=query, currency=currency_query
            )

        return query

    def __insert_query_scenario(
        self,
        scenario_id: str,
        scenario: str,
        year: int,
        period_id: str,
        company_id: str,
    ) -> str:
        return self.__get_insert_query(
            "financial_scenario",
            id=scenario_id,
            name=f"{scenario}-{year}",
            currency="USD",
            type=scenario,
            period_id=period_id,
            company_id=company_id,
        )

    def __insert_query_scenario_metric(self, scenario_id: str, metric_id: str) -> str:
        return self.__get_insert_query(
            "scenario_metric",
            id=str(uuid4()),
            scenario_id=scenario_id,
            metric_id=metric_id,
        )

    def __is_valid_number(self, number) -> bool:
        return number is not None and isinstance(number, (int, float, Decimal))

    def __verify_company_id(self, company_id: str) -> None:
        query = (
            self.query_builder.add_table_name(TableNames.COMPANY)
            .add_sql_where_equal_condition({"id": f"'{company_id}'"})
            .build()
            .get_query()
        )

        result = self.session.execute(query).fetchall()
        if not result:
            raise AppError("Company doesn't exist")

    def __verify_company_scenario(
        self, company_id: str, scenario_name: str, metric: str
    ) -> None:
        query = (
            self.query_builder.add_table_name(TableNames.SCENARIO)
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
                    f"{TableNames.SCENARIO}.company_id": f"'{company_id}'",
                    f"{TableNames.SCENARIO}.name": f"'{scenario_name}'",
                    f"{TableNames.METRIC}.name": f"'{metric}'",
                }
            )
            .build()
            .get_query()
        )
        result = self.session.execute(query).fetchall()
        if result:
            raise AppError("Scenario already exists")

    def __verify_names(self, scenario: str, metric: str) -> None:
        if scenario not in ScenarioNames._value2member_map_:
            raise AppError("Invalid scenario type")
        if metric not in MetricNames._value2member_map_:
            raise AppError("Invalid metric name")

    def __verify_numbers(self, year: int, value: float, scenario: str) -> None:
        if not isinstance(year, int) or len(str(year)) != 4:
            raise AppError("Invalid year")
        if not self.__is_valid_number(value):
            raise AppError("Invalid value, must be a number")
        current_year = datetime.now().year
        if scenario == ScenarioNames.ACTUALS and year > (current_year + 1):
            raise AppError(
                "The actual scenario year cannot be greater than the current year"
            )

    def __verify_company_data(
        self, company_id: str, scenario: str, year: int, metric: str, value: float
    ) -> None:
        self.__verify_names(scenario, metric)
        self.__verify_numbers(year, value, scenario)
        self.__verify_company_id(company_id)
        self.__verify_company_scenario(company_id, f"{scenario}-{year}", metric)

    def __get_query_for_new_scenario(
        self,
        period_query: str,
        metric_query: str,
        scenario_query: str,
        scenario_metric_query: str,
    ) -> str:
        return """
        BEGIN;
        {period}
        {metric}
        {scenario}
        {scenario_metric}
        COMMIT;
        """.format(
            period=period_query,
            metric=metric_query,
            scenario=scenario_query,
            scenario_metric=scenario_metric_query,
        )

    def add_company_scenario(
        self, company_id: str, scenario: str, year: int, metric: str, value: float
    ) -> dict:
        try:
            self.__verify_company_data(company_id, scenario, year, metric, value)
            period_id = str(uuid4())
            metric_id = str(uuid4())
            scenario_id = str(uuid4())

            period_query = self.__insert_query_time_period(year, period_id)
            metric_query = self.__insert_query_metric(
                metric_id, metric, value, period_id, company_id
            )
            scenario_query = self.__insert_query_scenario(
                scenario_id, scenario, year, period_id, company_id
            )
            scenario_metric_query = self.__insert_query_scenario_metric(
                scenario_id, metric_id
            )

            query = self.__get_query_for_new_scenario(
                period_query, metric_query, scenario_query, scenario_metric_query
            )

            self.session.execute(query)
            return {
                "id": scenario_id,
                "name": f"{scenario}-{year}",
                "metric_id": metric_id,
            }
        except Exception as error:
            self.logger.info(error)
            raise AppError(f"Cannot add new scenario: {error}")
