from app_names import TableNames
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL


class RangesRepository:
    def __init__(
        self, session, query_builder: QuerySQLBuilder, response_sql: ResponseSQL, logger
    ) -> None:
        self.logger = logger
        self.session = session
        self.query_builder = query_builder
        self.response_sql = response_sql

    def get_total_number_of_ranges(self) -> dict:
        try:
            query = (
                self.query_builder.add_table_name(TableNames.RANGE)
                .add_select_conditions(["COUNT(*)"])
                .add_sql_where_equal_condition(
                    {f"not {TableNames.RANGE}.type": f"'{'growth'}'"}
                )
                .build()
                .get_query()
            )
            result = self.session.execute(query).fetchall()
            return self.response_sql.process_query_result(result)
        except Exception as error:
            self.logger.error(error)
            raise error

    def get_ranges(self, offset: int = 0, max_count: int = None) -> list:
        try:
            query = (
                self.query_builder.add_table_name(TableNames.RANGE)
                .add_select_conditions()
                .add_sql_where_equal_condition(
                    {f"not {TableNames.RANGE}.type": f"'{'growth'}'"}
                )
                .add_sql_order_by_condition(
                    ["type, max_value"], self.query_builder.Order.ASC
                )
                .add_sql_offset_condition(offset)
                .add_sql_limit_condition(max_count)
                .build()
                .get_query()
            )

            results = self.session.execute(query).fetchall()
            return self.response_sql.process_query_list_results(results)
        except Exception as error:
            self.logger.error(error)
            return []
