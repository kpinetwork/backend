from app_names import TableNames
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL


class TagsRepository:
    def __init__(
        self, session, query_builder: QuerySQLBuilder, response_sql: ResponseSQL, logger
    ) -> None:
        self.logger = logger
        self.session = session
        self.query_builder = query_builder
        self.response_sql = response_sql

    def get_total_number_of_tags(self) -> dict:
        try:
            query = (
                self.query_builder.add_table_name(TableNames.TAG)
                .add_select_conditions(["COUNT(*)"])
                .build()
                .get_query()
            )

            result = self.session.execute(query).fetchall()
            return self.response_sql.process_query_result(result)
        except Exception as error:
            self.logger.error(error)
            raise error

    def __get_subquery_tag(self, offset, max_count) -> str:
        return (
            self.query_builder.add_table_name(TableNames.TAG)
            .add_select_conditions([f"{TableNames.TAG}.id"])
            .add_sql_order_by_condition(["id"], self.query_builder.Order.ASC)
            .add_sql_offset_condition(offset)
            .add_sql_limit_condition(max_count)
            .build()
            .get_query()
        )

    def get_tags_with_companies(self, offset=0, max_count=None) -> list:
        try:
            select_options = [
                f"{TableNames.TAG}.*",
                f"{TableNames.COMPANY}.id as company_id",
                f"{TableNames.COMPANY}.name as company_name",
            ]
            subquery = self.__get_subquery_tag(offset, max_count)
            where_conditions = {
                f"{TableNames.TAG}.id": [f"{subquery}"],
            }
            query = (
                self.query_builder.add_table_name(TableNames.TAG)
                .add_select_conditions(select_options)
                .add_join_clause(
                    {
                        f"{TableNames.COMPANY_TAG}": {
                            "from": f"{TableNames.TAG}.id",
                            "to": f"{TableNames.COMPANY_TAG}.tag_id",
                        }
                    }
                )
                .add_join_clause(
                    {
                        f"{TableNames.COMPANY}": {
                            "from": f"{TableNames.COMPANY_TAG}.company_id",
                            "to": f"{TableNames.COMPANY}.id",
                        }
                    }
                )
                .add_sql_where_equal_condition(where_conditions)
                .add_sql_order_by_condition(["name"], self.query_builder.Order.ASC)
                .build()
                .get_query()
            )

            results = self.session.execute(query).fetchall()
            return self.response_sql.process_query_list_results(results)
        except Exception as error:
            self.logger.error(error)
            return []

    def get_tags(self, offset=0, max_count=None) -> list:
        try:
            query = (
                self.query_builder.add_table_name(TableNames.TAG)
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
