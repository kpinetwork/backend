import json
from src.tests.data.data_reader import read
from unittest import TestCase, mock
from src.handlers.company.get_company_handler import handler


class TestGetCompanyHandler(TestCase):
    def setUp(self):
        self.company = read("sample_company.json")
        self.event = read("sample_event_company.json")

    @mock.patch("company_service.CompanyService.get_company")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_company_handler_success_should_return_200_response(
        self, mock_create_db_session, mock_create_db_engine, mock_get_company
    ):
        mock_get_company.return_value = self.company
        id_from_event = self.event.get("pathParameters").get("id")

        response = handler(self.event, {})

        mock_get_company.assert_called_with(self.company.get("id"))
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 200)
        self.assertEqual(id_from_event, self.company.get("id"))
        self.assertEqual(response.get("body"), json.dumps(self.company, default=str))

    @mock.patch("company_service.CompanyService.get_company")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_company_fail_should_return_error_400_response(
        self, mock_create_db_session, mock_create_db_engine, mock_get_company
    ):
        error_message = "Cannot get company"
        mock_get_company.side_effect = Exception(error_message)

        response = handler(self.event, {})

        mock_get_company.assert_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))
