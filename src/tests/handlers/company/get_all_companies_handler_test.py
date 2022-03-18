import json
from src.tests.data.data_reader import read
from unittest import TestCase, mock
from src.handlers.company.get_all_companies_handler import handler


class TestGetAllCompaniesHandler(TestCase):
    def setUp(self):
        self.company = read("sample_company.json")
        self.event = read("sample_event.json")

    @mock.patch("company_service.CompanyService.get_all_companies")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_handler_success_should_return_200_response(
        self, mock_create_db_session, mock_create_db_engine, mock_get_companies
    ):
        mock_get_companies.return_value = [self.company]
        response = handler(self.event, {})

        mock_get_companies.assert_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 200)
        self.assertEqual(response.get("body"), json.dumps([self.company], default=str))

    @mock.patch("company_service.CompanyService.get_all_companies")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_handler_fail_should_return_error_400_response(
        self, mock_create_db_session, mock_create_db_engine, mock_get_all_companies
    ):
        error_message = "Cannot get companies"
        mock_get_all_companies.side_effect = Exception(error_message)

        response = handler(self.event, {})
        mock_get_all_companies.assert_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()

        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))
