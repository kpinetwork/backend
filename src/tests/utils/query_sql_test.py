from unittest import TestCase
from src.utils.query_sql import QuerySQL


class TestQueryBuilder(TestCase):
    def setUp(self):
        self.query_sql_instance = QuerySQL()
        pass

    def test_get_select_by_id_query_success(self):
        table_name = "company"
        id = "test-id"
        query = self.query_sql_instance.get_select_by_id_query(table_name, id)
        expected_query = "SELECT * FROM {table_name} WHERE id='{id}';".format(
            table_name=table_name, id=id
        )

        self.assertEqual(query, expected_query)

    def test_get_select_by_id_query_failed(self):
        table_name = ""
        id = "test-id"
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.query_sql_instance.get_select_by_id_query(table_name, id)
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)

    def test_get_select_query_success(self):
        table_name = "company"
        offset = 0
        limit = 10
        query = self.query_sql_instance.get_select_query(table_name, offset, limit)

        expected_query = """
                SELECT * FROM {table_name}
                LIMIT {limit}
                OFFSET {offset};
            """.format(
            table_name=table_name, limit=limit, offset=offset
        )

        self.assertEqual(query, expected_query)

    def test_get_select_query_failed(self):
        table_name = ""
        offset = 0
        limit = 10
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.query_sql_instance.get_select_query(table_name, offset, limit)
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
