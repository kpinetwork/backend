from src.utils.query_builder import QuerySQLBuilder
class MetricsService:
    def __init__(self, session, query_builder, logger, response_sql):
        self.session = session
        self.table_name = "metric"
        self.query_builder = QuerySQLBuilder()
        self.response_sql = response_sql
        self.logger = logger
        pass

    def get_metric_by_company_id(self, company_id: str) -> dict:
        try:
            if company_id and company_id.strip():
                columns = [
                    f"{self.table_name}.id",
                    f"{self.table_name}.name",
                    f"{self.table_name}.value",
                    f"{self.table_name}.type",
                    f"{self.table_name}.data_type",
                    f"{self.table_name}.period_id",
                    "time_period.start_at",
                    "time_period.end_at",
                ]

                query = (
                    self.query_builder.add_table_name(self.table_name)
                    .add_select_conditions(columns)
                    .add_join_clause(
                        {
                            "time_period": {
                                "from": "time_period.id",
                                "to": f"{self.table_name}.period_id",
                            }
                        }
                    )
                    .add_sql_where_equal_condition(
                        {f"{self.table_name}.company_id": f"'{company_id}'"}
                    )
                    .add_sql_order_by_condition(
                        "time_period.start_at", self.query_builder.Order.DESC
                    )
                    .build()
                    .get_query()
                )
                result = self.session.execute(query).fetchall()
                self.session.commit()

                return self.response_sql.process_query_list_results(result)
            return dict()

        except Exception as error:
            self.logger.info(error)
            raise error

    def get_metrics(self, offset=0, max_count=20) -> list:
        try:
            query = (
                self.query_builder.add_table_name(self.table_name)
                .add_sql_offset_condition(offset)
                .add_sql_limit_condition(max_count)
                .build()
                .get_query()
            )

            results = self.session.execute(query).fetchall()
            self.session.commit()

            return self.response_sql.process_query_list_results(results)

        except Exception as error:
            self.logger.info(error)
            raise error

    def get_average_metrics(self, name: str, company_id: str) -> int:
        try:
            if name and name.strip() and company_id and company_id.strip():
                query = (
                    self.query_builder.add_table_name(self.table_name)
                    .add_select_conditions(["AVG(value) as average"])
                    .add_sql_where_equal_condition({"name": f"'{name}'", "company_id": f"'{company_id}'"})
                    .build()
                    .get_query()
                )   

                result = self.session.execute(query).fetchall()
                self.session.commit()

                return self.response_sql.process_query_average_result(result)
            return dict()

        except Exception as error:
            self.logger.info(error)
            raise error


