from uuid import uuid4

from app_names import TableNames
from query_builder import QuerySQLBuilder
from response_sql import ResponseSQL
from base_exception import AppError


class RangesRepository:
    def __init__(
        self, session, query_builder: QuerySQLBuilder, response_sql: ResponseSQL, logger
    ) -> None:
        self.logger = logger
        self.session = session
        self.query_builder = query_builder
        self.response_sql = response_sql

    def __get_first_range_label(self, max_value: float, label: str) -> str:
        return f"<${round(max_value)} {label}"

    def __get_last_range_label(self, min_value: float, label: str) -> str:
        return f"${round(min_value)} {label}+"

    def __get_range_label(self, min_value: float, max_value: float, label: str) -> str:
        return f"${round(min_value)}-<${round(max_value)} {label}"

    def __get_query_to_add_first_range(
        self, range: dict, metric_key: str, label: str
    ) -> str:
        return """
            INSERT INTO {value_range}
            (id, label, max_value, type)
            VALUES ('{record_id}', '{label}', '{max_value}', '{type}')
            """.format(
            value_range=TableNames.RANGE,
            record_id=str(uuid4()),
            label=self.get_range_label(
                range.get("min_value"), range.get("max_value"), label
            ),
            max_value=int(range.get("max_value")),
            type=metric_key,
        )

    def __get_query_to_add_last_range(
        self, range: dict, metric_key: str, label: str
    ) -> str:
        return """
            INSERT INTO {value_range}
            (id, label, min_value, type)
            VALUES ('{record_id}', '{label}', '{min_value}', '{type}')
            """.format(
            value_range=TableNames.RANGE,
            record_id=str(uuid4()),
            label=self.get_range_label(
                range.get("min_value"), range.get("max_value"), label
            ),
            min_value=int(range.get("min_value")),
            type=metric_key,
        )

    def __get_query_to_modify_first_range(
        self, range: dict, metric_key: str, label: str
    ) -> str:
        return """
            UPDATE {value_range}
            SET label= '{label}', max_value='{max_value}', type= '{type}'
            WHERE id = '{record_id}'
            """.format(
            value_range=TableNames.RANGE,
            label=self.get_range_label(
                range.get("min_value"), range.get("max_value"), label
            ),
            max_value=int(range.get("max_value")),
            type=metric_key,
            record_id=range.get("id"),
        )

    def __get_query_to_modify_last_range(
        self, range: dict, metric_key: str, label: str
    ) -> str:
        return """
            UPDATE {value_range}
            SET label= '{label}', min_value='{min_value}', type= '{type}'
            WHERE id = '{record_id}'
            """.format(
            value_range=TableNames.RANGE,
            label=self.get_range_label(
                range.get("min_value"), range.get("max_value"), label
            ),
            min_value=int(range.get("min_value")),
            type=metric_key,
            record_id=range.get("id"),
        )

    def __get_query_to_add_ranges_to_metric(
        self, range: dict, metric_key: str, label: str
    ) -> str:
        if range.get("min_value") is None:
            return self.__get_query_to_add_first_range(range, metric_key, label)
        if range.get("max_value") is None:
            return self.__get_query_to_add_last_range(range, metric_key, label)
        return """
        INSERT INTO {value_range}
        VALUES ('{record_id}', '{label}', '{min_value}', '{max_value}', '{type}')
        """.format(
            value_range=TableNames.RANGE,
            record_id=str(uuid4()),
            label=self.get_range_label(
                range.get("min_value"), range.get("max_value"), label
            ),
            min_value=int(range.get("min_value")),
            max_value=int(range.get("max_value")),
            type=metric_key,
        )

    def __get_query_to_update_ranges_to_metric(
        self, range: dict, metric_key: str, label: str
    ) -> str:
        if range.get("min_value") is None:
            return self.__get_query_to_modify_first_range(range, metric_key, label)
        if range.get("max_value") is None:
            return self.__get_query_to_modify_last_range(range, metric_key, label)
        return """
        UPDATE {value_range}
        SET label= '{label}', min_value= '{min_value}', max_value='{max_value}', type= '{type}'
        WHERE id = '{record_id}'
        """.format(
            value_range=TableNames.RANGE,
            label=self.get_range_label(
                range.get("min_value"), range.get("max_value"), label
            ),
            min_value=int(range.get("min_value")),
            max_value=int(range.get("max_value")),
            type=metric_key,
            record_id=range.get("id"),
        )

    def __get_query_to_delete_ranges_to_metric(self, range_id: str) -> str:
        return """
        DELETE FROM {value_range}
        WHERE id = '{record_id}'
        """.format(
            value_range=TableNames.RANGE, record_id=range_id
        )

    def __get_queries_modify_metric_ranges(
        self, key: str, ranges: list, function_to_exec, label: str
    ) -> list:
        try:
            if not ranges:
                return []
            return [function_to_exec(range_data, key, label) for range_data in ranges]
        except Exception as error:
            self.logger.error(error)
            raise AppError("Invalid format to update metric_ranges")

    def __get_queries_delete_metric_ranges(
        self, ranges: list, function_to_exec
    ) -> list:
        try:
            if not ranges:
                return []
            return [function_to_exec(range_id) for range_id in ranges]
        except Exception as error:
            self.logger.error(error)
            raise AppError("Invalid format to delete metric_ranges")

    def get_range_label(self, min_value: str, max_value: str, label: str) -> str:
        if min_value is None or min_value == "":
            return self.__get_first_range_label(int(max_value), label)
        if max_value is None or min_value == "":
            return self.__get_last_range_label(int(min_value), label)
        return self.__get_range_label(int(min_value), int(max_value), label)

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

    def get_ranges_by_metric(self, metric: str) -> list:
        try:
            query = (
                self.query_builder.add_table_name(TableNames.RANGE)
                .add_select_conditions()
                .add_sql_where_equal_condition(
                    {
                        f"not {TableNames.RANGE}.type": f"'{'growth'}'",
                        f"{TableNames.RANGE}.type": f"'{metric}'",
                    }
                )
                .add_sql_order_by_condition(
                    ["type, max_value"], self.query_builder.Order.ASC
                )
                .build()
                .get_query()
            )

            results = self.session.execute(query).fetchall()
            return self.response_sql.process_query_list_results(results)
        except Exception as error:
            self.logger.error(error)
            return []

    def modify_metric_ranges(
        self,
        metric_key: str,
        label: str,
        ranges_to_add: list,
        ranges_to_delete: list,
        ranges_to_update: list,
    ) -> bool:
        try:
            queries = self.__get_queries_modify_metric_ranges(
                metric_key,
                ranges_to_add,
                self.__get_query_to_add_ranges_to_metric,
                label,
            )
            queries.extend(
                self.__get_queries_modify_metric_ranges(
                    metric_key,
                    ranges_to_update,
                    self.__get_query_to_update_ranges_to_metric,
                    label,
                )
            )
            queries.extend(
                self.__get_queries_delete_metric_ranges(
                    ranges_to_delete,
                    self.__get_query_to_delete_ranges_to_metric,
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
