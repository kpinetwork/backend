from unittest import TestCase
import logging
from unittest.mock import Mock
from src.service.tags.tags_service import TagsService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestTagsService(TestCase):
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
        self.tags_service_instance = TagsService(
            self.mock_session, self.mock_query_builder, self.mock_response_sql, logger
        )

    def mock_response_query_sql(self, response):
        attrs = {"process_query_result.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def mock_response_list_query_sql(self, response):
        attrs = {"process_query_list_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def test_get_all_tags_return_results_sucess(self):
        self.mock_response_query_sql(self.total_tags)
        self.mock_response_list_query_sql([self.tag])

        get_all_tags = self.tags_service_instance.get_all_tags()

        self.assertEqual(get_all_tags, self.all_tags)

    def test_get_all_tags_failed(self):
        self.tags_service_instance.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(self.tags_service_instance.get_all_tags())

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.tags_service_instance.session.execute.assert_called_once()
