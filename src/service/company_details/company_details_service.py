from typing import Union
from base_exception import AppError
from app_names import TableNames, ScenarioNames


class CompanyDetails:
    def __init__(
        self, session, query_builder, response_sql, calculator, profile_range, logger
    ) -> None:
        self.logger = logger
        self.session = session
        self.calculator = calculator
        self.response_sql = response_sql
        self.query_builder = query_builder
        self.profile_range = profile_range
        self.table = TableNames.COMPANY

    def get_company_description(self, company_id: str) -> dict:
        try:
            query = (
                self.query_builder.add_table_name(self.table)
                .add_sql_where_equal_condition({f"{self.table}.id": f"'{company_id}'"})
                .build()
                .get_query()
            )
            result = self.session.execute(query).fetchall()
            return self.response_sql.process_query_result(result)
        except Exception as error:
            self.logger.info(error)
            return dict()

    def get_profile_records(self, company_id: str) -> Union[tuple, None]:
        try:
            columns = [f"{TableNames.METRIC}.value", f"{TableNames.SCENARIO}.name"]
            query = (
                self.query_builder.add_table_name(TableNames.SCENARIO)
                .add_select_conditions(columns)
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
                        f"{TableNames.SCENARIO}.type": "'Actuals'",
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
            result = self.session.execute(query).fetchall()
            return self.response_sql.process_revenue_profile_results(result)
        except Exception as error:
            self.logger.info(error)
            return None

    def get_company_profiles(self, company_id: str) -> dict:
        try:
            records = self.get_profile_records(company_id)
            if not records:
                raise AppError("Cannot get records for profile")
            actuals, prior = records
            growth = self.calculator.calculate_growth_rate(actuals, prior, False)
            size_ranges = self.profile_range.get_profile_ranges("size profile")
            growth_ranges = self.profile_range.get_profile_ranges("growth profile")

            return {
                "size_cohort": self.profile_range.get_range_from_value(
                    actuals, ranges=size_ranges
                ),
                "margin_group": self.profile_range.get_range_from_value(
                    growth, ranges=growth_ranges
                ),
            }
        except Exception as error:
            self.logger.info(error)
            return {"size_cohort": "NA", "margin_group": "NA"}

    def get_total_number_of_scenarios(self, company_id: str) -> Union[int, None]:
        try:
            query = (
                self.query_builder.add_table_name(TableNames.SCENARIO)
                .add_select_conditions(["COUNT(*)"])
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
                    {f"{TableNames.SCENARIO}.company_id": f"'{company_id}'"}
                )
                .build()
                .get_query()
            )
            result = self.session.execute(query).fetchall()
            return self.response_sql.process_query_result(result).get("count")
        except Exception as error:
            self.logger.info(error)
            return None

    def convert_metric_values(self, records: list) -> list:
        for metric in records:
            value = metric.get("value")
            metric["value"] = (
                float(value) if self.calculator.is_valid_number(value) else "NA"
            )

    def __get_case_order(self, ordered: bool) -> str:
        scenarios = list(ScenarioNames)
        if not ordered:
            scenarios.sort(reverse=True)

        return f"""
                CASE
                WHEN {TableNames.SCENARIO}.type='{scenarios[0]}' then 0
                WHEN {TableNames.SCENARIO}.type='{scenarios[1]}' then 1
                ELSE 2 end
                """

    def get_company_scenarios(
        self, company_id: str, offset: int, limit: int, ordered: bool
    ) -> list:
        try:
            columns = [
                f"{TableNames.SCENARIO}.id as scenario_id",
                f"{TableNames.SCENARIO}.type as scenario",
                "extract(year from start_at)::int as year",
                f"{TableNames.PERIOD}.period_name as period_name",
                f"{TableNames.METRIC}.id as metric_id",
                f"{TableNames.METRIC}.name as metric",
                f"{TableNames.METRIC}.value",
            ]
            case_query = self.__get_case_order(ordered)

            query = (
                self.query_builder.add_table_name(TableNames.SCENARIO)
                .add_select_conditions(columns)
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
                .add_join_clause(
                    {
                        f"{TableNames.PERIOD}": {
                            "from": f"{TableNames.PERIOD}.id",
                            "to": f"{TableNames.METRIC}.period_id",
                        }
                    }
                )
                .add_join_clause(
                    {
                        f"{TableNames.METRIC_SORT}": {
                            "from": f"{TableNames.METRIC_SORT}.name",
                            "to": f"{TableNames.METRIC}.name",
                        }
                    }
                )
                .add_sql_where_equal_condition(
                    {f"{TableNames.SCENARIO}.company_id": f"'{company_id}'"}
                )
                .add_sql_order_by_condition(
                    [
                        case_query,
                        f"{TableNames.SCENARIO}.type",
                        "year",
                        f"{TableNames.METRIC_SORT}.group_sort_value",
                        f"{TableNames.METRIC_SORT}.sort_value",
                    ],
                    self.query_builder.Order.ASC,
                )
                .add_sql_offset_condition(offset)
                .add_sql_limit_condition(limit)
                .build()
                .get_query()
            )

            result = self.session.execute(query).fetchall()
            records = self.response_sql.process_query_list_results(result)
            self.convert_metric_values(records)
            return records
        except Exception as error:
            self.logger.info(error)
            return []

    def get_company_details(
        self, company_id: str, offset: int = 0, limit: int = 20, ordered: bool = True
    ) -> dict:
        if not (company_id and company_id.strip()):
            raise AppError("Invalid company id")

        company = self.get_company_description(company_id)
        if not company:
            raise AppError("Company not found")

        company.update(self.get_company_profiles(company_id))

        company["scenarios"] = {
            "total": self.get_total_number_of_scenarios(company_id),
            "metrics": self.get_company_scenarios(company_id, offset, limit, ordered),
        }

        return company

    def __get_company_scenarios_ids(self, company_id: str) -> list:
        try:
            query = (
                self.query_builder.add_table_name(TableNames.SCENARIO)
                .add_select_conditions(
                    [
                        f"{TableNames.SCENARIO}.id as scenario",
                        f"{TableNames.METRIC}.id as metric",
                        f"{TableNames.METRIC}.period_id as period",
                    ]
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
                    {f"{TableNames.SCENARIO}.company_id": f"'{company_id}'"}
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

    def __get_ids_list(self, records: list, field: str) -> list:
        return [f"'{record.get(field)}'" for record in records if record.get(field)]

    def __get_company_investments_ids(self, company_id) -> list:
        try:
            query = (
                self.query_builder.add_table_name(TableNames.INVESTMENT)
                .add_select_conditions(["id as invest"])
                .add_sql_where_equal_condition(
                    {f"{TableNames.INVESTMENT}.company_id": f"'{company_id}'"}
                )
                .build()
                .get_query()
            )
            result = self.session.execute(query).fetchall()
            return self.response_sql.process_query_list_results(result)
        except Exception as error:
            self.logger.info(error)
            return []

    def __get_ids(self, company_id: str) -> dict:
        records = self.__get_company_scenarios_ids(company_id)
        invests = self.__get_company_investments_ids(company_id)
        metrics = self.__get_ids_list(records, "metric")
        periods = self.__get_ids_list(records, "period")
        scenarios = self.__get_ids_list(records, "scenario")
        investments = self.__get_ids_list(invests, "invest")

        return {
            f"{TableNames.METRIC}": metrics,
            f"{TableNames.SCENARIO}": scenarios,
            f"{TableNames.PERIOD}": periods,
            f"{TableNames.INVESTMENT}": investments,
        }

    def __get_delete_list_query(self, table: str, table_field: str, ids: list) -> str:
        if not ids:
            return ""

        return """
        DELETE FROM {table}
        WHERE {table}.{field} IN ({values});
        """.format(
            table=table, field=table_field, values=",".join(ids)
        )

    def __get_delete_company_query(self, base_ids: dict, company_id: str) -> str:
        scenarios = base_ids.get(TableNames.SCENARIO)
        metrics = base_ids.get(TableNames.METRIC)
        periods = base_ids.get(TableNames.PERIOD)
        investments = base_ids.get(TableNames.INVESTMENT)

        return """
            {scenario_metric_query}
            {currency_query}
            {metric_query}
            {scenario_query}
            {period_query}
            {investor_query}
            {invest_query}
            {company_tag_query}
            DELETE FROM {company} WHERE {company}.id = '{id}';
        """.format(
            scenario_metric_query=self.__get_delete_list_query(
                TableNames.SCENARIO_METRIC, "scenario_id", scenarios
            ),
            currency_query=self.__get_delete_list_query(
                TableNames.CURRENCY_METRIC, "metric_id", metrics
            ),
            scenario_query=self.__get_delete_list_query(
                TableNames.SCENARIO, "id", scenarios
            ),
            investor_query=self.__get_delete_list_query(
                TableNames.INVESTOR, "investment_id", investments
            ),
            invest_query=self.__get_delete_list_query(
                TableNames.INVESTMENT, "id", investments
            ),
            metric_query=self.__get_delete_list_query(TableNames.METRIC, "id", metrics),
            period_query=self.__get_delete_list_query(TableNames.PERIOD, "id", periods),
            company_tag_query=self.__get_delete_list_query(
                TableNames.COMPANY_TAG, "company_id", [f"'{company_id}'"]
            ),
            company=TableNames.COMPANY,
            id=company_id,
        )

    def __verify_company_exist(self, company_id: str) -> None:
        try:
            if not company_id or not company_id.strip():
                raise AppError("Invalid company id")
            query = (
                self.query_builder.add_table_name(self.table)
                .add_sql_where_equal_condition({"id": f"'{company_id}'"})
                .build()
                .get_query()
            )
            result = self.session.execute(query).fetchall()
            if not result:
                raise AppError("Company not found")
        except AppError as error:
            raise error
        except Exception as error:
            self.logger.info(error)
            raise error

    def delete_company(self, company_id: str) -> bool:
        try:
            self.__verify_company_exist(company_id)
            base_ids = self.__get_ids(company_id)

            query = self.__get_delete_company_query(base_ids, company_id)

            self.session.execute(query)
            self.session.commit()
            return True
        except AppError as error:
            self.logger.info(error)
            raise error
        except Exception as error:
            self.session.rollback()
            self.logger.info(error)
            return False
