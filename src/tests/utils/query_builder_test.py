from unittest import TestCase
from src.utils.query_builder import QuerySQLBuilder
from src.utils.commons_functions import remove_white_spaces


class TestQueryBuilder(TestCase):
    def setUp(self):
        self.query_sql_instance = QuerySQLBuilder()
        self.table_name = "test"
        self.join_value = {
            "other": {"alias": "o", "from": "o.id", "to": f"{self.table_name}.id"}
        }

    def test_add_table_name_with_valid_name(self):
        query_builder = QuerySQLBuilder().add_table_name(self.table_name)

        self.assertEqual(query_builder.table_name, self.table_name)

    def test_add_table_name_with_invalid_name(self):
        table_name = ""

        with self.assertRaises(Exception):
            exception = self.assertRaises(QuerySQLBuilder().add_table_name(table_name))

            self.assertEqual(exception, Exception)

    def test_add_select_conditions_with_valid_list(self):
        columns = ["id"]
        query_builder = QuerySQLBuilder().add_select_conditions(columns)

        self.assertEqual(len(query_builder.select_conditions), len(columns))
        self.assertEqual(query_builder.select_conditions, columns)

    def test_add_select_conditions_with_None_list(self):
        columns = None
        query_builder = QuerySQLBuilder().add_select_conditions(columns)

        expected_columns = ["*"]

        self.assertEqual(len(query_builder.select_conditions), len(expected_columns))
        self.assertEqual(query_builder.select_conditions, expected_columns)

    def test_add_join_clause_with_valid_dict(self):
        expected_join_clause = f"""
                JOIN other AS o
                ON o.id = {self.table_name}.id
            """

        query_builder = QuerySQLBuilder().add_join_clause(self.join_value)

        clause = query_builder.join_clauses[0]

        self.assertEqual(len(query_builder.join_clauses), len([expected_join_clause]))
        self.assertEqual(
            remove_white_spaces(clause), remove_white_spaces(expected_join_clause)
        )

    def test_add_join_clause_with_invalid_table_name(self):

        join_dict = {"": {"alias": "o", "from": "o.id", "to": f"{self.table_name}.id"}}

        with self.assertRaises(Exception):
            exception = self.assertRaises(QuerySQLBuilder().add_join_clause(join_dict))

            self.assertEqual(exception, Exception)

    def test_add_join_clause_with_invalid_alias_name(self):

        join_dict = {
            "other": {"alias": "", "from": "o.id", "to": f"{self.table_name}.id"}
        }

        query_builder = QuerySQLBuilder().add_join_clause(join_dict)

        expected_clause = f"""
                JOIN other
                ON o.id = {self.table_name}.id
            """

        self.assertEqual(len(query_builder.join_clauses), len([expected_clause]))
        self.assertEqual(
            remove_white_spaces(query_builder.join_clauses[0]),
            remove_white_spaces(expected_clause),
        )

    def test_add_join_clause_with_invalid_on_values(self):

        join_dict = {"other": {"alias": "o", "from": "", "to": ""}}

        with self.assertRaises(Exception):
            exception = self.assertRaises(QuerySQLBuilder().add_join_clause(join_dict))

            self.assertEqual(exception, Exception)

    def test_add_join_clause_with_None_dict(self):
        join_dict = None
        query_builder = QuerySQLBuilder().add_join_clause(join_dict)

        expected_join_clauses = []

        self.assertEqual(len(query_builder.join_clauses), len(expected_join_clauses))
        self.assertEqual(query_builder.join_clauses, expected_join_clauses)

    def test_add_sql_where_equal_condition_with_valid_dict(self):
        conditions = {"name": "test"}
        query_builder = QuerySQLBuilder().add_sql_where_equal_condition(conditions)

        expected_where_condition = "name = test"

        self.assertEqual(len(query_builder.where_conditions), len(conditions))
        self.assertEqual(query_builder.where_conditions, [expected_where_condition])

    def test_add_sql_where_equal_condition_with_None_dict(self):
        query_builder = QuerySQLBuilder().add_sql_where_equal_condition(None)

        self.assertEqual(len(query_builder.where_conditions), 0)
        self.assertEqual(query_builder.where_conditions, [])

    def test_add_sql_group_by_condition_with_valid_column_name(self):
        column_name = f"{self.table_name}.name"
        query_builder = QuerySQLBuilder().add_sql_group_by_condition(column_name)

        self.assertEqual(query_builder.group_by, column_name)

    def test_add_sql_group_by_condition_with_invalid_column_name(self):
        column_name = ""
        with self.assertRaises(Exception):
            exception = self.assertRaises(
                QuerySQLBuilder().add_sql_group_by_condition(column_name)
            )

            self.assertEqual(exception, Exception)

    def test_add_sql_limit_condition_with_valid_limit(self):
        limit = 10

        query_builder = QuerySQLBuilder().add_sql_limit_condition(limit)

        self.assertEqual(query_builder.limit, limit)

    def test_add_sql_limit_condition_with_invalid_limit(self):
        limit = None

        with self.assertRaises(Exception):
            exception = self.assertRaises(
                QuerySQLBuilder().add_sql_limit_condition(limit)
            )

            self.assertEqual(exception, Exception)

    def test_add_sql_offset_condition_with_valid_offset(self):
        offset = 10

        query_builder = QuerySQLBuilder().add_sql_offset_condition(offset)

        self.assertEqual(query_builder.offset, offset)

    def test_add_sql_offset_condition_with_invalid_offset(self):
        offset = None

        with self.assertRaises(Exception):
            exception = self.assertRaises(
                QuerySQLBuilder().add_sql_offset_condition(offset)
            )

            self.assertEqual(exception, Exception)

    def test_add_sql_order_by_condition(self):
        query_builder = QuerySQLBuilder()
        query_builder.add_sql_order_by_condition("id", query_builder.Order.DESC)

        expected_order_by = ("id", "DESC")

        self.assertEqual(query_builder.order_by, expected_order_by)

    def test__build_select_with_condition(self):
        columns = ["id", "name"]
        query_builder = QuerySQLBuilder().add_select_conditions(columns)
        expected_condition = ",".join(columns)

        result = query_builder._QuerySQLBuilder__build_select()

        self.assertEqual(result, expected_condition)

    def test__build_select_without_condition(self):
        query_builder = QuerySQLBuilder()
        expected_condition = "*"

        result = query_builder._QuerySQLBuilder__build_select()

        self.assertEqual(result, expected_condition)

    def test__build_where_with_condition(self):
        conditions = {"name": "test"}
        query_builder = QuerySQLBuilder().add_sql_where_equal_condition(conditions)

        expected_condition = "WHERE name = test"
        result = query_builder._QuerySQLBuilder__build_where()

        self.assertEqual(result, expected_condition)

    def test__build_where_without_condition(self):
        query_builder = QuerySQLBuilder()
        expected_condition = ""

        result = query_builder._QuerySQLBuilder__build_where()

        self.assertEqual(result, expected_condition)

    def test__build_group_by_condition_with_value(self):
        column_name = f"{self.table_name}.name"
        query_builder = QuerySQLBuilder().add_sql_group_by_condition(column_name)

        expected_group_by_condition = f"GROUP BY {column_name}"
        result = query_builder._QuerySQLBuilder__build_group_by()

        self.assertEqual(result, expected_group_by_condition)

    def test__build_group_by_condition_with_None(self):
        query_builder = QuerySQLBuilder()

        expected_group_by_condition = ""
        result = query_builder._QuerySQLBuilder__build_group_by()

        self.assertEqual(result, expected_group_by_condition)

    def test__build_offset_with_value(self):
        offset = 10
        query_builder = QuerySQLBuilder().add_sql_offset_condition(offset)

        expected_offset_condition = f"OFFSET {offset}"
        result = query_builder._QuerySQLBuilder__build_offset()

        self.assertEqual(result, expected_offset_condition)

    def test__build_where_with_None(self):
        query_builder = QuerySQLBuilder()
        expected_offset_condition = ""

        result = query_builder._QuerySQLBuilder__build_offset()

        self.assertEqual(result, expected_offset_condition)

    def test__build_limit_with_value(self):
        limit = 10
        query_builder = QuerySQLBuilder().add_sql_limit_condition(limit)

        expected_limit_condition = f"LIMIT {limit}"
        result = query_builder._QuerySQLBuilder__build_limit()

        self.assertEqual(result, expected_limit_condition)

    def test__build_limit_with_None(self):
        query_builder = QuerySQLBuilder()
        expected_limit_condition = ""

        result = query_builder._QuerySQLBuilder__build_limit()

        self.assertEqual(result, expected_limit_condition)

    def test__build_order_by_with_value(self):
        query_builder = QuerySQLBuilder()
        query_builder.add_sql_order_by_condition("id", query_builder.Order.DESC)

        expected_order_by_condition = "ORDER BY id DESC"
        result = query_builder._QuerySQLBuilder__build_order_by()

        self.assertEqual(result, expected_order_by_condition)

    def test__build_order_by_with_None(self):
        query_builder = QuerySQLBuilder()

        expected_order_by_condition = ""
        result = query_builder._QuerySQLBuilder__build_order_by()

        self.assertEqual(result, expected_order_by_condition)

    def test__clear(self):
        query_builder = (
            QuerySQLBuilder()
            .add_table_name(self.table_name)
            .add_select_conditions(["name"])
            .add_sql_where_equal_condition({"name": "'test'"})
            .add_sql_offset_condition(2)
            .add_sql_limit_condition(10)
            .build()
        )

        query_builder._QuerySQLBuilder__clear()

        self.assertEqual(query_builder.table_name, "")
        self.assertEqual(query_builder.select_conditions, [])
        self.assertEqual(query_builder.where_conditions, [])
        self.assertIsNone(query_builder.limit)
        self.assertIsNone(query_builder.offset)

    def test_build_with_all_conditions(self):
        query_builder = (
            QuerySQLBuilder()
            .add_table_name(self.table_name)
            .add_select_conditions(["name"])
            .add_sql_where_equal_condition({"name": "'test'"})
            .add_sql_offset_condition(2)
            .add_sql_limit_condition(10)
            .build()
        )

        self.assertTrue(len(query_builder.where_conditions) > 0)
        self.assertTrue(len(query_builder.select_conditions) > 0)

    def test_get_query(self):
        query_builder = (
            QuerySQLBuilder()
            .add_table_name(self.table_name)
            .add_select_conditions(["name"])
            .add_sql_where_equal_condition({"name": "'test'"})
            .add_sql_offset_condition(2)
            .add_sql_group_by_condition(f"{self.table_name}.name")
            .add_sql_limit_condition(10)
            .build()
        )

        expected_query = """
            SELECT name FROM test
            WHERE name = 'test'
            GROUP BY {table_name}.name
            OFFSET 2
            LIMIT 10
        """.format(
            table_name=self.table_name
        )

        query = query_builder.get_query()
        print("QUERY ", remove_white_spaces(query))
        self.assertEqual(
            remove_white_spaces(query), remove_white_spaces(expected_query)
        )
