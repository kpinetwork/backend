from unittest import TestCase, mock
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
            "company_id": "1",
            "company_name": "Test Company",
        }
        self.total_tags = {"count": 1}
        self.tags_and_companies = {
            "123": {
                "id": "123",
                "name": "Tag Name",
                "companies": [
                    {"id": "1", "name": "Test Company"},
                    {"id": "2", "name": "Company Name"},
                ],
            }
        }
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

    def test_get_companies_by_tags_should_return_the_response_when_the_list_of_records_is_passed(
        self,
    ):
        expected_data = self.tags_and_companies
        data = [
            self.tag,
            {
                "id": "123",
                "name": "Tag Name",
                "company_id": "2",
                "company_name": "Company Name",
            },
        ]

        get_companies_by_tag = self.tags_service_instance.get_companies_by_tag(data)

        self.assertEqual(get_companies_by_tag, expected_data)

    @mock.patch("src.service.tags.tags_service.TagsService.get_companies_by_tag")
    def test_get_all_tags_return_results_when_queries_are_succesful(
        self, mock_get_companies_by_tag
    ):
        expected_data = {
            "total": self.total_tags.get("count"),
            "tags": self.tags_and_companies,
        }

        self.mock_response_query_sql(self.total_tags)
        self.mock_response_list_query_sql([self.tag])
        mock_get_companies_by_tag.return_value = self.tags_and_companies

        get_all_tags = self.tags_service_instance.get_all_tags()

        self.assertEqual(get_all_tags, expected_data)

    def test_get_all_tags_should_return_error_when_queries_fails(self):
        self.tags_service_instance.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(self.tags_service_instance.get_all_tags())

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.tags_service_instance.session.execute.assert_called_once()
