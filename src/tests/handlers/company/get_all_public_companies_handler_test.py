import json
from src.tests.data.data_reader import read
from unittest import TestCase, mock
import src.handlers.company.get_all_public_companies_handler as get_all_public_companies_handler
from src.handlers.company.get_all_public_companies_handler import handler


class TestGetAllPublicCompaniesHandler(TestCase):
    def setUp(self):
        self.username = "user@email.com"
        self.company = read("sample_company.json")
        self.companies = read("sample_companies.json")
        self.total_companies = len(list(self.companies))
        self.public_companies = {
            "total": self.total_companies,
            "companies": list(
                filter(
                    lambda company: company.get("is_public"),
                    self.companies.get("companies"),
                )
            ),
        }
        self.event = read("sample_event.json")

    @mock.patch("company_service.CompanyService.get_all_public_companies")
    @mock.patch.object(get_all_public_companies_handler, "get_username_from_user_id")
    @mock.patch("company_anonymization.CompanyAnonymization.set_company_permissions")
    @mock.patch.object(
        get_all_public_companies_handler, "get_user_details_service_instance"
    )
    @mock.patch.object(get_all_public_companies_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_all_public_companies_handler_success_should_return_200_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_get_user_service_instance,
        mock_set_company_permissions,
        mock_get_username_from_user_id,
        mock_get_public_companies,
    ):
        mock_get_user_service_instance.return_value = object()
        mock_verify_user_access.return_value = True
        mock_get_username_from_user_id.return_value = self.username
        mock_get_public_companies.return_value = self.public_companies

        response = handler(self.event, {})

        mock_get_public_companies.assert_called_with(1, 1, True)
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        mock_set_company_permissions.assert_called_with(self.username)
        self.assertEqual(response.get("statusCode"), 200)
        self.assertEqual(
            response.get("body"), json.dumps(self.public_companies, default=str)
        )

    @mock.patch("company_service.CompanyService.get_all_public_companies")
    @mock.patch.object(get_all_public_companies_handler, "get_username_from_user_id")
    @mock.patch("company_anonymization.CompanyAnonymization.set_company_permissions")
    @mock.patch.object(
        get_all_public_companies_handler, "get_user_details_service_instance"
    )
    @mock.patch.object(get_all_public_companies_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_all_public_companies_handler_fail_should_return_error_400_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_get_user_service_instance,
        mock_set_company_permissions,
        mock_get_username_from_user_id,
        mock_get_all_public_companies,
    ):
        error_message = "Cannot get companies"
        mock_get_all_public_companies.side_effect = Exception(error_message)
        mock_get_user_service_instance.return_value = object()
        mock_verify_user_access.return_value = True
        mock_get_username_from_user_id.return_value = self.username

        response = handler(self.event, {})

        mock_get_all_public_companies.assert_called_with(1, 1, True)
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        mock_set_company_permissions.assert_called_with(self.username)
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))
