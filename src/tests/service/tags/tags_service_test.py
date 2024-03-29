import logging
from unittest.mock import Mock, patch
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

    def test_get_tags_by_company_when_company_id_is_invalid_should_raised_an_exception(
        self,
    ):
        self.mock_repository.get_tags_by_company.side_effect = Exception(
            "Invalid company ID"
        )

        with self.assertRaises(Exception) as context:
            self.tags_service_instance.get_tags_by_company("")

        self.assertEqual(str(context.exception), "Can't get tags: Invalid company ID")
        self.mock_repository.get_tags_by_company.assert_not_called()

    def test_get_tags_by_company_when_query_execution_fails_should_raised_an_exception(
        self,
    ):
        self.mock_repository.get_tags_by_company.side_effect = Exception("error")

        with self.assertRaises(Exception) as context:
            self.tags_service_instance.get_tags_by_company("123")

        self.assertEqual(str(context.exception), "Can't get tags: error")
        self.mock_repository.get_tags_by_company.assert_called_once()

    def test_add_tag_sucess_should_return_added_tag(self):
        tag_expected = self.tag.copy()
        tag_expected.update({"companies": ["123"]})
        self.mock_repository.add_tag.return_value = tag_expected

        tag = self.tags_service_instance.add_tag(self.tag)

        self.assertEqual(tag.get("name"), tag_expected.get("name"))
        self.assertEqual(tag.get("companies"), tag_expected.get("companies"))

    def test_add_tag_when_query_execution_fails_should_raise_an_exception(self):
        self.mock_repository.add_tag.side_effect = Exception("error")

        with self.assertRaises(Exception) as context:
            self.tags_service_instance.add_tag(self.tag)

        self.assertEqual(str(context.exception), "Cannot add new tag: error")
        self.mock_repository.add_tag.assert_called_once()

    def test_update_tags_from_tag_panel_without_empty_tags_data_when_sucess_should_update_tags(
        self,
    ):
        tags_data = {"tag_1": {"name": "Tag name changed"}}
        self.mock_repository.update_tags.return_value = True

        updated = self.tags_service_instance.update_tags_from_tag_panel(tags_data)

        self.assertTrue(updated)
        self.mock_repository.update_tags.assert_called()

    def test_update_tags_from_tag_panel_with_empty_tags_data_should_raise_exception(
        self,
    ):
        tags_data = {"tag_1": {}}

        with self.assertRaises(Exception) as context:
            self.tags_service_instance.update_tags_from_tag_panel(tags_data)

        self.assertEqual(str(context.exception), "There isn't data to modify")
        self.mock_repository.update_tags.assert_not_called()

    def test_company_tags_without_empty_tags_data_when_sucess_should_update_company_tags(
        self,
    ):
        company_tags = {
            "company_id": "company_1",
            "tags_to_delete": ["tag_1"],
            "tags_to_add": ["tag_3"],
        }

        self.mock_repository.update_company_tags.return_value = True
        updated = self.tags_service_instance.update_company_tags(company_tags)

        self.assertTrue(updated)
        self.mock_repository.update_company_tags.assert_called()

    def test_update_company_tags_with_empty_tags_data_should_raise_exception(self):
        company_tags = {
            "company_id": None,
        }

        with self.assertRaises(Exception) as context:
            self.tags_service_instance.update_company_tags(company_tags)

        self.assertEqual(str(context.exception), "There isn't data to modify")
        self.mock_repository.update_company_tags.assert_not_called()

    @patch("src.service.tags.tags_service.TagsService.update_company_tags")
    def test_update_tags_with_empty_tags_data_should_call_update_company_data(
        self, mock_update_company_tags
    ):
        company_tags = {
            "company_id": "company_1",
            "tags_to_delete": ["tag_1"],
        }
        mock_update_company_tags.return_value = True

        updated = self.tags_service_instance.update_tags({"company": company_tags})

        self.assertTrue(updated)
        mock_update_company_tags.assert_called()

    @patch("src.service.tags.tags_service.TagsService.update_tags_from_tag_panel")
    def test_update_tags_with_tags_data_should_call_update_tags_from_tag_panel(
        self, mock_update_tags_from_tag_panel
    ):
        tags_data = {"tag_1": {"name": "Tag name changed"}}
        mock_update_tags_from_tag_panel.return_value = True

        updated = self.tags_service_instance.update_tags({"tags": tags_data})

        self.assertTrue(updated)
        mock_update_tags_from_tag_panel.assert_called()

    def test_delete_tags_with_empty_list_should_raise_exception(self):
        tag_ids = []
        error_message = "No tags to delete"

        with self.assertRaises(Exception) as context:
            self.tags_service_instance.delete_tags(tag_ids)

        self.assertEqual(str(context.exception), error_message)

    def test_delete_tags_with_valid_ids_and_should_delete_tags(self):
        tag_ids = ["tag_id_1"]

        deleted = self.tags_service_instance.delete_tags(tag_ids)

        self.assertTrue(deleted)
        self.mock_repository.delete_tags.assert_called_once()
