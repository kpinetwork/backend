import logging
from unittest import TestCase
from unittest.mock import Mock

from src.service.tags.tags_repository import TagsRepository
from src.utils.query_builder import QuerySQLBuilder

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestTagsRepository(TestCase):
    def setUp(self):
        self.tag = {
            "id": "123",
            "name": "Tag Name",
            "company_id": "1",
            "company_name": "Test Company",
        }
        self.short_tag = {"id": "123", "name": "Tag Name"}
        self.total_tags = {"count": 1}
        self.all_tags = {
            "total": self.total_tags.get("count"),
            "tags": [self.tag],
        }
        self.mock_session = Mock()
        self.query_builder = QuerySQLBuilder()
        self.mock_response_sql = Mock()
        self.repository = TagsRepository(
            self.mock_session, self.query_builder, self.mock_response_sql, logger
        )

    def mock_response_query_sql(self, response):
        attrs = {"process_query_result.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def mock_response_list_query_sql(self, response):
        attrs = {"process_query_list_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def test_get_total_number_of_tags_when_query_execution_is_success_returns_the_count_of_tags(
        self,
    ):
        self.mock_response_query_sql(self.total_tags)

        total_number_of_tags = self.repository.get_total_number_of_tags()

        self.assertEqual(total_number_of_tags, self.total_tags)
        self.mock_session.execute.assert_called_once()

    def test_get_total_number_of_tags_when_the_query_execution_fails_throws_an_exception(
        self,
    ):
        self.mock_session.execute.side_effect = Exception("error")

        with self.assertRaises(Exception) as context:
            self.repository.get_total_number_of_tags()

        self.assertEqual(str(context.exception), "error")
        self.mock_session.execute.assert_called_once()

    def test_get_tags_with_companies_if_the_query_execution_is_success_returns_tags_companies_data(
        self,
    ):
        self.mock_response_list_query_sql(self.tag)

        get_tags_response = self.repository.get_tags_with_companies()

        self.assertEqual(get_tags_response, self.tag)
        self.mock_session.execute.assert_called_once()

    def test_get_tags_with_companies_when_the_query_execution_fails_return_empty_list(
        self,
    ):
        self.mock_session.execute.side_effect = Exception("error")

        get_tags_response = self.repository.get_tags_with_companies()

        self.assertEqual(get_tags_response, [])
        self.mock_session.execute.assert_called_once()

    def test_get_tags_when_the_query_execution_is_succesful_returns_the_tags_data(
        self,
    ):
        self.mock_response_list_query_sql(self.short_tag)

        get_tags_response = self.repository.get_tags()

        self.assertEqual(get_tags_response, self.short_tag)
        self.mock_session.execute.assert_called_once()

    def test_get_tags_when_the_query_execution_fails_return_empty_list(self):
        self.mock_session.execute.side_effect = Exception("error")

        get_tags_response = self.repository.get_tags()

        self.assertEqual(get_tags_response, [])
        self.mock_session.execute.assert_called_once()

    def test_get_tags_by_company_when_company_id_is_valid_should_return_list_of_tags(
        self,
    ):
        self.mock_response_list_query_sql([self.short_tag])
        company_id = "123"

        tags = self.repository.get_tags_by_company(company_id)

        self.assertEqual(tags, [self.short_tag])

    def test_get_tags_by_company_when_the_query_execution_fails_should_return_empty_list(
        self,
    ):
        self.mock_session.execute.side_effect = Exception("error")

        tags = self.repository.get_tags_by_company("123")

        self.assertEqual(tags, [])
        self.mock_session.execute.assert_called_once()

    def test_add_tag_success_without_associated_companies_should_return_added_tag(
        self,
    ):
        tag_response = self.tag.copy()
        tag_response["companies"] = []

        added_tag = self.repository.add_tag({"name": self.tag.get("name")})

        self.assertEqual(added_tag.get("name"), self.tag.get("name"))
        self.assertEqual(added_tag.get("companies"), [])

    def test_add_tag_success_with_associated_companies_should_return_added_tag(
        self,
    ):
        tag_response = self.tag.copy()
        tag_response["companies"] = ["123"]

        added_tag = self.repository.add_tag(tag_response)

        self.assertEqual(added_tag.get("name"), self.tag.get("name"))
        self.assertEqual(added_tag.get("companies"), tag_response.get("companies"))
        self.mock_session.execute.assert_called_once()

    def test_add_tag_with_invalid_tag_name_should_raise_exception(self):
        self.mock_session.execute.side_effect = Exception("Invalid tag name")

        with self.assertRaises(Exception) as context:
            self.repository.add_tag({"name": ""})

        self.assertEqual(str(context.exception), "Invalid tag name")
        self.mock_session.rollback.assert_called()

    def test_add_tag_with_invalid_transaction_exec_should_raise_exception(self):
        self.mock_session.execute.side_effect = Exception("error with query exec")

        with self.assertRaises(Exception) as context:
            self.repository.add_tag({"name": self.tag.get("name")})

        self.assertEqual(str(context.exception), "error with query exec")
        self.mock_session.execute.assert_called_once()
        self.mock_session.rollback.assert_called()

    def test_update_tags_with_no_empty_name_data_should_call_session_execute(self):
        tags_data = {
            "tag_1": {"name": "Change tag 1"},
            "tag_2": {"name": "Change tag 2"},
        }

        names_changed = self.repository.update_tags(tags_data)

        self.assertTrue(names_changed)
        self.mock_session.execute.assert_called_once()

    def test_update_tags_to_tags_with_no_empty_companies_to_add_should_call_db_session_execute(
        self,
    ):
        tags_data_to_change = {
            "tag_1": {"companies_to_add": ["company_1", "company_2"]}
        }

        added = self.repository.update_tags(tags_data_to_change)

        self.assertTrue(added)
        self.mock_session.execute.assert_called_once()

    def test_update_tags_with_no_empty_companies_to_delete_should_call_db_session_execute(
        self,
    ):
        tags_data_to_change = {
            "tag_2": {"companies_to_delete": ["company_1", "company_2"]}
        }

        deleted = self.repository.update_tags(tags_data_to_change)

        self.assertTrue(deleted)
        self.mock_session.execute.assert_called_once()

    def test_update_tags_with_no_valid_name_data_structure_should_raise_exception(self):
        name_data_to_change = {"tag_1": ["Tag change name"]}

        with self.assertRaises(Exception) as context:
            self.repository.update_tags(name_data_to_change)

        self.assertEqual(str(context.exception), "Invalid format to update names")
        self.mock_session.execute.assert_not_called()

    def test_update_tags_with_invalid_companies_to_add_data_structure_should_raise_exception(
        self,
    ):
        tags_data_to_change = {"tag_1": {"companies_to_add": 1}}

        with self.assertRaises(Exception) as context:
            self.repository.update_tags(tags_data_to_change)

        self.assertEqual(
            str(context.exception), "Invalid format to update companies tags"
        )
        self.mock_session.execute.assert_not_called()

    def test_update_tags_with_invalid_companies_to_delete_data_structure_should_raise_exception(
        self,
    ):
        tags_data_to_change = {"tag_1": {"companies_to_delete": 2}}

        with self.assertRaises(Exception) as context:
            self.repository.update_tags(tags_data_to_change)

        self.assertEqual(
            str(context.exception), "Invalid format to update companies tags"
        )
        self.mock_session.execute.assert_not_called()

    def test_update_tags_with_invalid_transaction_exec_should_not_update_tags(self):
        name_data = {"tag_1": {"name": "Tag change name"}}
        self.mock_session.execute.side_effect = Exception("error with query")

        updated = self.repository.update_tags(name_data)

        self.assertFalse(updated)
        self.mock_session.execute.assert_called()
        self.mock_session.rollback.assert_called()

    def test_get_queries_update_company_tags_with_empty_tag_list_should_return_empty_list(
        self,
    ):

        queries_list = self.repository._TagsRepository__get_queries_update_company_tags(
            "company_id", [], lambda x, y: x + y
        )

        self.assertEqual(queries_list, [])

    def test_update_company_tags_with_valid_tag_data_format_should_call_db_session_execute(
        self,
    ):
        company_tags_data = {
            "company_id": "company_1",
            "tags_to_add": ["tag_1"],
            "tags_to_delete": ["tags_2"],
        }

        updated = self.repository.update_company_tags(**company_tags_data)

        self.assertTrue(updated)
        self.mock_session.execute.assert_called_once()

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
        self.mock_session.execute.assert_not_called()

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
        self.mock_session.execute.assert_called_once()
        self.mock_session.rollback.assert_called()

    def test_delete_tags_with_no_empty_list_should_execute_query(self):
        tag_ids = ["tag_id_1", "tag_id_2"]

        deleted = self.repository.delete_tags(tag_ids)

        self.assertTrue(deleted)
        self.mock_session.execute.assert_called_once()

    def test_delete_tags_with_empty_list_should_call_rollback(self):
        tag_ids = []
        self.mock_session.execute.side_effect = Exception("error")

        deleted = self.repository.delete_tags(tag_ids)

        self.assertFalse(deleted)
        self.mock_session.rollback.assert_called_once()
