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
        self.short_tag = {"id": "123", "name": "Tag Name"}
        self.total_tags = {"count": 1}
        self.all_tags = [
            {
                "id": "123",
                "name": "Tag Name",
                "companies": [
                    {"id": "1", "name": "Test Company"},
                    {"id": "2", "name": "Company Name"},
                ],
            }
        ]
        self.mock_session = Mock()
        self.mock_query_builder = Mock()
        self.mock_response_sql = Mock()
        self.mock_repository = Mock()
        self.tags_service_instance = TagsService(logger, self.mock_repository)

    def mock_response_query_sql(self, response):
        attrs = {"process_query_result.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def mock_response_list_query_sql(self, response):
        attrs = {"process_query_list_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def test_get_companies_by_tags_returns_the_tags_and_companies_when_the_query_response_is_passed(
        self,
    ):
        expected_data = self.all_tags
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
    def test_get_all_tags_should_return_the_count_and_tags_data_if_user_has_access(
        self, mock_get_companies_by_tag
    ):
        expected_data = {
            "total": self.total_tags.get("count"),
            "tags": self.all_tags,
        }

        self.mock_repository.get_total_number_of_tags.return_value = self.total_tags
        self.mock_repository.get_tags_with_companies.return_value = [self.tag]
        mock_get_companies_by_tag.return_value = self.all_tags

        get_all_tags = self.tags_service_instance.get_all_tags(True)

        self.assertEqual(get_all_tags, expected_data)

    @mock.patch("src.service.tags.tags_service.TagsService.get_companies_by_tag")
    def test_get_all_tags_should_return_the_count_and_tags_data_if_user_does_not_have_access(
        self, mock_get_companies_by_tag
    ):
        expected_data = {
            "total": self.total_tags.get("count"),
            "tags": [self.short_tag],
        }

        self.mock_repository.get_total_number_of_tags.return_value = self.total_tags
        self.mock_repository.get_tags.return_value = [self.short_tag]
        mock_get_companies_by_tag.return_value = self.all_tags

        get_all_tags = self.tags_service_instance.get_all_tags(False)

        self.assertEqual(get_all_tags, expected_data)

    def test_get_all_tags_should_raise_an_exception_when_queries_fails(self):
        self.mock_session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(self.tags_service_instance.get_all_tags(True))

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.mock_session.execute.assert_called_once()
