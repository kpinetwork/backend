from unittest import TestCase
import logging
from unittest.mock import Mock
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
