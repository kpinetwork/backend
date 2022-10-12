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

    def test_add_tag_with_invalid_transaction_exec_should_raise_exception(self):
        self.mock_session.execute.side_effect = Exception("error with query exec")

        with self.assertRaises(Exception) as context:
            self.repository.add_tag({"name": self.tag.get("name")})

        self.assertEqual(str(context.exception), "error with query exec")
        self.mock_session.execute.assert_called_once()
        self.mock_session.rollback.assert_called()
