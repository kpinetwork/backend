from app_names import TableNames


class TagsRepository:
    def __init__(self, session, query_builder, response_sql, logger) -> None:
        self.logger = logger
        self.session = session
        self.query_builder = query_builder
        self.response_sql = response_sql

    def get_total_number_of_tags(self) -> dict:
        try:
            query = (
                self.query_builder.add_table_name(TableNames.TAGS)
                .add_select_conditions(["COUNT(*)"])
                .build()
                .get_query()
            )

            result = self.session.execute(query).fetchall()
            return self.response_sql.process_query_result(result)

        except Exception as error:
            self.logger.info(error)
            raise error

    def get_tags(self, offset=0, max_count=None) -> list:
        try:
            query = (
                self.query_builder.add_table_name(TableNames.TAGS)
                .add_sql_order_by_condition(["name"], self.query_builder.Order.ASC)
                .add_sql_offset_condition(offset)
                .add_sql_limit_condition(max_count)
                .build()
                .get_query()
            )

            results = self.session.execute(query).fetchall()
            return self.response_sql.process_query_list_results(results)
        except Exception as error:
            self.logger.info(error)
            return []
