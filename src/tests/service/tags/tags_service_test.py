import logging
from unittest.mock import Mock
from unittest import TestCase

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
        self.tag_with_companies = {
            "id": "123",
            "name": "Tag Name",
            "companies": [
                {"id": "1", "name": "Test Company"},
            ],
        }
        self.mock_repository = Mock()
        self.tags_service_instance = TagsService(logger, self.mock_repository)

    def test_get_companies_by_tags_if_tags_without_companies_is_passed_returns_tags_and_companies(
        self,
    ):
        tag_data = {
            "id": "234",
            "name": "Tag Test Name",
        }
        tag_data_with_companies_list = tag_data.copy()
        tag_data_with_companies_list["companies"] = []
        expected_tags_data = [self.tag_with_companies, tag_data_with_companies_list]
        data = [
            self.tag,
            tag_data,
        ]

        get_companies_by_tag_response = self.tags_service_instance.get_companies_by_tag(
            data
        )

        self.assertEqual(get_companies_by_tag_response, expected_tags_data)

    def test_get_companies_by_tags_if_tags_with_companies_is_passed_returns_tags_and_companies_data(
        self,
    ):
        tag_data = self.tag_with_companies.copy()
        tag_data["companies"].append({"id": "2", "name": "Company Name"})
        expected_tags_data = [tag_data]
        data = [
            self.tag,
            {
                "id": "123",
                "name": "Tag Name",
                "company_id": "2",
                "company_name": "Company Name",
            },
        ]

        get_companies_by_tag_response = self.tags_service_instance.get_companies_by_tag(
            data
        )

        self.assertEqual(get_companies_by_tag_response, expected_tags_data)

    def test_get_all_tags_if_user_has_access_should_return_the_count_and_tags_with_companies_data(
        self,
    ):
        expected_tags_dict = {
            "total": self.total_tags.get("count"),
            "tags": [self.tag_with_companies],
        }
        self.mock_repository.get_total_number_of_tags.return_value = self.total_tags
        self.mock_repository.get_tags_with_companies.return_value = [self.tag]

        get_all_tags_response = self.tags_service_instance.get_all_tags(True)

        self.assertEqual(get_all_tags_response, expected_tags_dict)
        self.mock_repository.get_total_number_of_tags.assert_called_once()
        self.mock_repository.get_tags_with_companies.assert_called_once()

    def test_get_all_tags_if_user_does_not_have_access_should_return_the_count_and_tags_data(
        self,
    ):
        expected_tags_dict = {
            "total": self.total_tags.get("count"),
            "tags": [self.short_tag],
        }
        self.mock_repository.get_total_number_of_tags.return_value = self.total_tags
        self.mock_repository.get_tags.return_value = [self.short_tag]

        get_all_tags_response = self.tags_service_instance.get_all_tags(False)

        self.assertEqual(get_all_tags_response, expected_tags_dict)
        self.mock_repository.get_total_number_of_tags.assert_called_once()
        self.mock_repository.get_tags.assert_called_once()

    def test_get_all_tags_when_query_execution_fails_should_raise_an_exception(self):
        self.mock_repository.get_total_number_of_tags.side_effect = Exception("error")

        with self.assertRaises(Exception) as context:
            self.tags_service_instance.get_all_tags(True)

        self.assertEqual(str(context.exception), "Can't get tags")
        self.mock_repository.get_total_number_of_tags.assert_called_once()

    def test_get_tags_by_company_should_return_list_of_tags(self):
        self.mock_repository.get_tags_by_company.return_value = [self.short_tag]

        tags = self.tags_service_instance.get_tags_by_company("123")

        self.assertEqual(tags, [self.short_tag])

    def test_get_tags_by_company_when_query_execution_fails_should_raised_an_exception(
        self,
    ):
        self.mock_repository.get_tags_by_company.side_effect = Exception("error")

        with self.assertRaises(Exception) as context:
            self.tags_service_instance.get_tags_by_company("123")

        self.assertEqual(str(context.exception), "Can't get tags")
        self.mock_repository.get_tags_by_company.assert_called_once()
