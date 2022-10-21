from uuid import uuid4

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

    def __get_company_tag_queries(self, tag_id: str, companies: list) -> str:
        query = ""
        for company_id in companies:
            if company_id and company_id.strip():
                company_tag_id = str(uuid4())
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

    def __get_query_to_update_tag_name(self, tag_id: str, tag_data: dict) -> str:
        return (
            self.query_builder.add_table_name(TableNames.TAG)
            .add_set_conditions({"name": f"'{tag_data.get('name')}'"})
            .add_sql_where_equal_condition({f"{TableNames.TAG}.id": f"'{tag_id}'"})
            .build_update()
            .get_query()
        )

    def __get_query_to_add_company_to_tag(self, tag_id: str, company_id: str) -> str:
        return """
        INSERT INTO {company_tag}
        VALUES ('{record_id}', '{tag_id}', '{company_id}')
        """.format(
            company_tag=TableNames.COMPANY_TAG,
            record_id=str(uuid4()),
            tag_id=tag_id,
            company_id=company_id,
        )

    def __get_query_to_remove_company_from_tag(
        self, tag_id: str, company_id: str
    ) -> str:
        where_query = self.query_builder.add_sql_where_equal_condition(
            {"tag_id": f"'{tag_id}'", "company_id": f"'{company_id}'"}
        ).get_where_query()
        return """
        DELETE FROM {company_tag}
        {where_query}
        """.format(
            company_tag=TableNames.COMPANY_TAG, where_query=where_query
        )

    def __get_queries_to_udpate_tag_names(self, tags_data: dict) -> list:
        try:
            return [
                self.__get_query_to_update_tag_name(tag_id, tag_data)
                for tag_id, tag_data in tags_data.items()
                if tag_id and tag_id.strip() and tag_data.get("name")
            ]
        except Exception as error:
            self.logger.error(error)
            raise AppError("Invalid format to update names")

    def __get_queries_to_modify_company_tag_records(
        self, tags_data: dict, function_to_exec, field: str
    ) -> list:
        try:
            queries = []
            [
                queries.extend(
                    list(
                        map(
                            lambda company_id, tag=tag_id: function_to_exec(
                                tag, company_id
                            ),
                            tag_data.get(field),
                        )
                    )
                )
                for tag_id, tag_data in tags_data.items()
                if tag_id and tag_id.strip() and tag_data.get(field)
            ]
            return queries
        except Exception as error:
            self.logger.error(error)
            raise AppError("Invalid format to update companies tags")

    def __get_queries_update_company_tags(
        self, company_id: str, tags: list, function_to_exec
    ) -> list:
        try:
            if not tags:
                return []
            return [function_to_exec(tag_id, company_id) for tag_id in tags]
        except Exception as error:
            self.logger.error(error)
            raise AppError("Invalid format to update company tags")

    def __get_queries_to_add_companies_to_tags(self, tags_data: dict) -> list:
        return self.__get_queries_to_modify_company_tag_records(
            tags_data, self.__get_query_to_add_company_to_tag, "companies_to_add"
        )

    def __get_queries_to_remove_companies_from_tags(self, tags_data: dict) -> list:
        return self.__get_queries_to_modify_company_tag_records(
            tags_data,
            self.__get_query_to_remove_company_from_tag,
            "companies_to_delete",
        )

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

    def add_tag(self, tag: dict) -> dict:
        try:
            tag_id = str(uuid4())
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

    def update_tags(self, tags_data: dict) -> bool:
        try:
            tag_queries_list = self.__get_queries_to_udpate_tag_names(tags_data)
            tag_queries_list.extend(
                self.__get_queries_to_remove_companies_from_tags(tags_data)
            )
            tag_queries_list.extend(
                self.__get_queries_to_add_companies_to_tags(tags_data)
            )
            query = ";".join(tag_queries_list)
            self.session.execute(query)
            self.session.commit()
            return True
        except AppError as error:
            raise error
        except Exception as error:
            self.session.rollback()
            self.logger.error(f"here: {error}")
            return False

    def update_company_tags(
        self, company_id: str, tags_to_add: list, tags_to_delete: list
    ) -> bool:
        try:
            queries = self.__get_queries_update_company_tags(
                company_id, tags_to_add, self.__get_query_to_add_company_to_tag
            )
            queries.extend(
                self.__get_queries_update_company_tags(
                    company_id,
                    tags_to_delete,
                    self.__get_query_to_remove_company_from_tag,
                )
            )
            query = ";".join(queries)
            self.session.execute(query)
            self.session.commit()
            return True
        except AppError as error:
            raise error
        except Exception as error:
            self.session.rollback()
            self.logger.error(error)
            return False

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
