from unittest import TestCase
from unittest.mock import Mock
from src.utils.company_anonymization import CompanyAnonymization


class TestCompanyAnonymization(TestCase):
    def setUp(self):
        self.username = "test@email.com"
        self.permissions = [
            {"id": "1", "permission": "read"},
            {"id": "2", "permission": "read"},
        ]
        self.company = {
            "id": "1",
            "name": "Test Company",
            "is_public": True,
        }
        self.mock_user_service = Mock()
        self.company_anonymization_instance = CompanyAnonymization(
            self.mock_user_service
        )

    def mock_get_user_company_permissions(self, response):
        attrs = {"get_user_company_permissions.return_value": response}
        self.mock_user_service.configure_mock(**attrs)

    def test_set_company_permissions_should_return_valid_list(self):
        self.mock_get_user_company_permissions(self.permissions)
        expected_companies = ["1", "2"]

        self.company_anonymization_instance.set_company_permissions(self.username)

        self.assertEqual(
            self.company_anonymization_instance.companies, expected_companies
        )

    def test_anonymize_company_name_should_return_anonimazed_data(self):
        expected_id = "1-xxxx"

        anonymized_id = self.company_anonymization_instance.anonymize_company_name(
            self.company.get("id")
        )

        self.assertEqual(anonymized_id, expected_id)

    def test_anonymize_company_description_should_return_anonymized_data(self):
        expected_company_anonymized = self.company.copy()
        expected_company_anonymized["name"] = "{id}-xxxx".format(
            id=expected_company_anonymized["id"][0:4]
        )

        company_anonymized = (
            self.company_anonymization_instance.anonymize_company_description(
                self.company, "id"
            )
        )

        self.assertEqual(company_anonymized, expected_company_anonymized)

    def test_anonymize_company_description_should_return_no_anonymized_data(self):
        expected_company_anonymized = self.company.copy()
        expected_company_anonymized["name"] = "{id}-xxxx".format(
            id=expected_company_anonymized["id"][0:4]
        )
        self.mock_get_user_company_permissions(self.permissions)

        self.company_anonymization_instance.set_company_permissions(self.username)
        company_anonymized = (
            self.company_anonymization_instance.anonymize_company_description(
                self.company, "id"
            )
        )

        self.assertEqual(company_anonymized, self.company)

    def test_anonymize_companies_list_should_return_anonymized_data(self):
        expected_company_anonymized = self.company.copy()
        expected_company_anonymized["name"] = "{id}-xxxx".format(
            id=expected_company_anonymized["id"][0:4]
        )

        companies_anonymized = (
            self.company_anonymization_instance.anonymize_companies_list(
                [self.company], "id"
            )
        )

        self.assertEqual(companies_anonymized, [expected_company_anonymized])

    def test_anonymize_companies_list_should_return_no_anonymized_data(self):
        self.mock_get_user_company_permissions(self.permissions)

        self.company_anonymization_instance.set_company_permissions(self.username)
        companies_anonymized = (
            self.company_anonymization_instance.anonymize_companies_list(
                [self.company], "id"
            )
        )

        self.assertEqual(companies_anonymized, [self.company])
