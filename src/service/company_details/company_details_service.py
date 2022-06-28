from typing import Union
from base_exception import AppError
from app_names import TableNames


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

    def get_company_scenarios(self, company_id: str, offset: int, limit: int) -> list:
        try:
            columns = [
                f"{TableNames.SCENARIO}.id as scenario_id",
                f"{TableNames.SCENARIO}.type as scenario",
                "extract(year from start_at)::int as year",
                f"{TableNames.METRIC}.id as metric_id",
                f"{TableNames.METRIC}.name as metric",
                f"{TableNames.METRIC}.value",
            ]
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
                .add_sql_where_equal_condition(
                    {f"{TableNames.SCENARIO}.company_id": f"'{company_id}'"}
                )
                .add_sql_order_by_condition(
                    [
                        f"{TableNames.SCENARIO}.id",
                        f"{TableNames.SCENARIO}.type",
                        f"{TableNames.METRIC}.name",
                        "start_at",
                        f"{TableNames.METRIC}.value",
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
        self, company_id: str, offset: int = 0, limit: int = 20
    ) -> dict:
        if not (company_id and company_id.strip()):
            raise AppError("Invalid company id")

        company = self.get_company_description(company_id)
        if not company:
            raise AppError("Company not found")

        company.update(self.get_company_profiles(company_id))

        company["scenarios"] = {
            "total": self.get_total_number_of_scenarios(company_id),
            "metrics": self.get_company_scenarios(company_id, offset, limit),
        }

        return company
