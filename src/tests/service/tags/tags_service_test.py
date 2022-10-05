import logging
from unittest import TestCase
from unittest.mock import Mock, patch

from src.service.tags.tags_service import TagsService
from src.utils.query_builder import QuerySQLBuilder

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

    def test_update_tags_from_tag_panel_without_empty_tags_data_when_sucess_should_update_tags(
        self,
    ):
        tags_data = {"tag_1": {"name": "Tag name changed"}}
        self.tags_service_instance.repository.query_builder = QuerySQLBuilder()

        updated = self.tags_service_instance.update_tags_from_tag_panel(tags_data)

        self.assertTrue(updated)
        self.mock_session.execute.assert_called()

    def test_update_tags_from_tag_panel_with_empty_tags_data_should_raise_exception(
        self,
    ):
        tags_data = {"tag_1": {}}
        self.tags_service_instance.repository.query_builder = QuerySQLBuilder()

        with self.assertRaises(Exception) as context:
            self.tags_service_instance.update_tags_from_tag_panel(tags_data)

        self.assertEqual(str(context.exception), "There isn't data to modify")
        self.mock_session.execute.assert_not_called()

    def test_company_tags_without_empty_tags_data_when_sucess_should_update_company_tags(
        self,
    ):
        company_tags = {
            "company_id": "company_1",
            "tags_to_delete": ["tag_1"],
            "tags_to_add": ["tag_3"],
        }
        self.tags_service_instance.repository.query_builder = QuerySQLBuilder()

        updated = self.tags_service_instance.update_company_tags(company_tags)

        self.assertTrue(updated)
        self.mock_session.execute.assert_called()

    def test_update_company_tags_with_empty_tags_data_should_raise_exception(self):
        company_tags = {
            "company_id": None,
        }
        self.tags_service_instance.repository.query_builder = QuerySQLBuilder()

        with self.assertRaises(Exception) as context:
            self.tags_service_instance.update_company_tags(company_tags)

        self.assertEqual(str(context.exception), "There isn't data to modify")
        self.mock_session.execute.assert_not_called()

    @patch("src.service.tags.tags_service.TagsService.update_company_tags")
    def test_update_tags_with_empty_tags_data_should_call_update_company_data(
        self, mock_update_company_tags
    ):
        company_tags = {
            "company_id": "company_1",
            "tags_to_delete": ["tag_1"],
        }
        self.tags_service_instance.repository.query_builder = QuerySQLBuilder()
        mock_update_company_tags.return_value = True

        updated = self.tags_service_instance.update_tags({"company": company_tags})

        self.assertTrue(updated)
        mock_update_company_tags.assert_called()

    @patch("src.service.tags.tags_service.TagsService.update_tags_from_tag_panel")
    def test_update_tags_with_tags_data_should_call_update_tags_from_tag_panel(
        self, mock_update_tags_from_tag_panel
    ):
        tags_data = {"tag_1": {"name": "Tag name changed"}}
        self.tags_service_instance.repository.query_builder = QuerySQLBuilder()
        mock_update_tags_from_tag_panel.return_value = True

        updated = self.tags_service_instance.update_tags({"tags": tags_data})

        self.assertTrue(updated)
        mock_update_tags_from_tag_panel.assert_called()
