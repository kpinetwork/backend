import uuid

from app_names import TableNames
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL
from base_exception import AppError


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

    def get_tags_by_company(self, company_id: str) -> list:
        try:
            query = (
                self.query_builder.add_table_name(TableNames.TAG)
                .add_select_conditions(
                    [
                        f"{TableNames.TAG}.id",
                        f"{TableNames.TAG}.name",
                    ]
                )
                .add_join_clause(
                    {
                        f"{TableNames.COMPANY_TAG}": {
                            "from": f"{TableNames.COMPANY_TAG}.tag_id",
                            "to": f"{TableNames.TAG}.id",
                        }
                    }
                )
                .add_sql_order_by_condition(["name"], self.query_builder.Order.ASC)
                .add_sql_where_equal_condition(
                    {f"{TableNames.COMPANY_TAG}.company_id": f"'{company_id}'"}
                )
                .build()
                .get_query()
            )
            results = self.session.execute(query).fetchall()
            return self.response_sql.process_query_list_results(results)
        except Exception as error:
            self.logger.error(error)
            return []

    def __get_company_tag_queries(self, tag_id: str, companies: list) -> str:
        query = ""
        for company_id in companies:
            if company_id and company_id.strip():
                company_tag_id = str(uuid.uuid4())
                query += """
                    INSERT INTO {table}
                    VALUES ('{id}', '{tag_id}', '{company_id}');
                """.format(
                    table=TableNames.COMPANY_TAG,
                    id=company_tag_id,
                    tag_id=tag_id,
                    company_id=company_id,
                )
        return query

    def __get_tag_query(self, tag_id: str, tag_name: str) -> str:
        return """
            INSERT INTO {table_name}
            VALUES('{id}', '{name}');
            """.format(
            table_name=TableNames.TAG, id=tag_id, name=tag_name
        )

    def add_tag(self, tag: dict) -> dict:
        try:
            tag_id = str(uuid.uuid4())
            tag_name = tag.get("name")
            companies = tag.get("companies", [])

            if tag_name is None or not tag_name.strip():
                raise AppError("Invalid tag name")
            query = self.__get_tag_query(tag_id, tag_name)

            if companies and len(companies) > 0:
                company_tag_query = self.__get_company_tag_queries(tag_id, companies)
                query = """
                {tag}
                {company_tag}
                """.format(
                    tag=query, company_tag=company_tag_query
                )

            self.session.execute(query)
            self.session.commit()

            return {
                "id": tag_id,
                "name": tag_name,
                "companies": companies,
            }

        except Exception as error:
            self.session.rollback()
            self.logger.error(error)
            raise error
