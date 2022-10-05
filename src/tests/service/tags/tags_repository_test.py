import logging
from unittest import TestCase
from unittest.mock import Mock

from src.utils.query_builder import QuerySQLBuilder
from src.service.tags.tags_repository import TagsRepository

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestTagsRepository(TestCase):
    def setUp(self):
        self.tag = {
            "id": "123",
            "name": "Tag Name",
        }
        self.total_tags = {"count": 1}
        self.all_tags = {
            "total": self.total_tags.get("count"),
            "tags": [self.tag],
        }
        self.mock_session = Mock()
        self.mock_query_builder = Mock()
        self.mock_response_sql = Mock()
        self.repository = TagsRepository(
            self.mock_session, self.mock_query_builder, self.mock_response_sql, logger
        )

    def mock_response_query_sql(self, response):
        attrs = {"process_query_result.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def mock_response_list_query_sql(self, response):
        attrs = {"process_query_list_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def test_get_total_number_of_tags_success(self):
        self.mock_response_query_sql(self.total_tags)

        get_total_number_of_tags = self.repository.get_total_number_of_tags()

        self.assertEqual(get_total_number_of_tags, self.total_tags)
        self.repository.session.execute.assert_called_once()

    def test_get_total_number_of_tags_failed(self):
        self.repository.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(self.repository.get_total_number_of_tags())

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.repository.session.execute.assert_called_once()

    def test_get_tags_return_results_sucess(
        self,
    ):
        self.mock_response_list_query_sql(self.tag)

        get_tags = self.repository.get_tags()

        self.assertEqual(get_tags, self.tag)

    def test_get_tags_failed(self):
        self.repository.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(self.repository.get_tags())

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.repository.session.execute.assert_called_once()

    def test_update_tags_with_no_empty_name_data_should_call_session_db(self):
        tags_data = {
            "tag_1": {"name": "Change tag 1"},
            "tag_2": {"name": "Change tag 2"},
        }
        self.repository.query_builder = QuerySQLBuilder()

        names_changed = self.repository.update_tags(tags_data)

        self.assertTrue(names_changed)
        self.repository.session.execute.assert_called_once()

    def test_update_tags_to_tags_with_no_empty_companies_to_add_should_call_db_session(
        self,
    ):
        data = {"tag_1": {"companies_to_add": ["company_1", "company_2"]}}
        self.repository.query_builder = QuerySQLBuilder()

        added = self.repository.update_tags(data)

        self.assertTrue(added)
        self.mock_session.execute.assert_called_once()

    def test_update_tags_with_no_empty_companies_to_delete_should_call_db_session(self):
        data = {"tag_2": {"companies_to_delete": ["company_1", "company_2"]}}
        self.repository.query_builder = QuerySQLBuilder()

        deleted = self.repository.update_tags(data)

        self.assertTrue(deleted)
        self.mock_session.execute.assert_called_once()

    def test_update_tags_with_no_valid_name_data_structure_should_raise_exception(self):
        name_data = {"tag_1": ["Tag change name"]}
        self.repository.query_builder = QuerySQLBuilder()

        with self.assertRaises(Exception) as context:
            self.repository.update_tags(name_data)

        self.assertEqual(str(context.exception), "Invalid format to update names")
        self.repository.session.execute.assert_not_called()

    def test_update_tags_with_invalid_companies_to_add_data_structure_should_raise_exception(
        self,
    ):
        data = {"tag_1": {"companies_to_add": 1}}
        self.repository.query_builder = QuerySQLBuilder()

        with self.assertRaises(Exception) as context:
            self.repository.update_tags(data)

        self.assertEqual(
            str(context.exception), "Invalid format to update companies tags"
        )
        self.mock_session.execute.assert_not_called()

    def test_update_tags_with_invalid_companies_to_delete_data_structure_should_raise_exception(
        self,
    ):
        data = {"tag_1": {"companies_to_delete": 2}}
        self.repository.query_builder = QuerySQLBuilder()

        with self.assertRaises(Exception) as context:
            self.repository.update_tags(data)

        self.assertEqual(
            str(context.exception), "Invalid format to update companies tags"
        )
        self.mock_session.execute.assert_not_called()

    def test_update_tags_with_invalid_transaction_exec_should_not_update_tags(self):
        name_data = {"tag_1": {"name": "Tag change name"}}
        self.repository.query_builder = QuerySQLBuilder()
        self.mock_session.execute.side_effect = Exception("error with query")

        updated = self.repository.update_tags(name_data)

        self.assertFalse(updated)
        self.repository.session.execute.assert_called()
        self.repository.session.rollback.assert_called()

    def test_get_queries_update_company_tags_with_empty_tag_list_should_return_empty_list(
        self,
    ):

        queries_list = self.repository._TagsRepository__get_queries_update_company_tags(
            "company_id", [], lambda x, y: x + y
        )

        self.assertEqual(queries_list, [])

    def test_update_company_tags_with_valid_tag_data_format_should_call_db_session(
        self,
    ):
        company_tags_data = {
            "company_id": "company_1",
            "tags_to_add": ["tag_1"],
            "tags_to_delete": ["tags_2"],
        }

        updated = self.repository.update_company_tags(**company_tags_data)

        self.assertTrue(updated)
        self.repository.session.execute.assert_called_once()

    def test_update_company_tags_with_invalid_tags_data_format_should_raise_exception(
        self,
    ):
        company_tags_data = {
            "company_id": "company_1",
            "tags_to_add": 1,
            "tags_to_delete": ["tags_2"],
        }
        with self.assertRaises(Exception) as context:
            self.repository.update_company_tags(**company_tags_data)

        self.assertEqual(
            str(context.exception), "Invalid format to update company tags"
        )
        self.repository.session.execute.assert_not_called()

    def test_update_company_tags_with_invalid_transaction_exec_should_not_update_company_tags(
        self,
    ):
        company_tags_data = {
            "company_id": "company_1",
            "tags_to_add": ["tag_1"],
            "tags_to_delete": ["tags_2"],
        }
        self.mock_session.execute.side_effect = Exception("error with query exec")

        updated = self.repository.update_company_tags(**company_tags_data)

        self.assertFalse(updated)
        self.repository.session.execute.assert_called_once()
        self.repository.session.rollback.assert_called()
