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

    def __get_subquery_tag(self, offset: int, max_count: int) -> str:
        return (
            self.query_builder.add_table_name(TableNames.TAG)
            .add_select_conditions([f"{TableNames.TAG}.id"])
            .add_sql_order_by_condition(["name"], self.query_builder.Order.ASC)
            .add_sql_offset_condition(offset)
            .add_sql_limit_condition(max_count)
            .build()
            .get_query()
        )

    def get_tags_with_companies(self, offset: int = 0, max_count: int = None) -> list:
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
                    },
                    self.query_builder.JoinType.LEFT,
                )
                .add_join_clause(
                    {
                        f"{TableNames.COMPANY}": {
                            "from": f"{TableNames.COMPANY_TAG}.company_id",
                            "to": f"{TableNames.COMPANY}.id",
                        }
                    },
                    self.query_builder.JoinType.LEFT,
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

    def get_tags(self, offset: int = 0, max_count: int = None) -> list:
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
            self.logger.error(error)
            return []

    def __get_str_sql_list(self, records: list) -> list:
        return [
            f"'{record}'"
            for record in records
            if record and isinstance(record, str) and record.strip()
        ]

    def __get_queries_to_delete_tag(self, tag_ids: list) -> str:
        return """
        DELETE FROM {company_tag_table}
        WHERE {company_tag_table}.tag_id IN ({tag_ids});
        DELETE FROM {tag_table}
        WHERE {tag_table}.id IN ({tag_ids});
        """.format(
            company_tag_table=TableNames.COMPANY_TAG,
            tag_table=TableNames.TAG,
            tag_ids=",".join(self.__get_str_sql_list(tag_ids)),
        )

    def delete_tags(self, tag_ids: list) -> bool:
        try:
            query = self.__get_queries_to_delete_tag(tag_ids)
            self.session.execute(query)
            self.session.commit()
            return True
        except Exception as error:
            self.session.rollback()
            self.logger.error(error)
            return False
