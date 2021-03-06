import json
from src.tests.data.data_reader import read
from unittest import TestCase, mock
from src.handlers.company.change_company_publicly_handler import handler
import src.handlers.company.change_company_publicly_handler as publicly_handler


class TestChangeCompanyPubliclyHandler(TestCase):
    def setUp(self):
        self.company = read("sample_company.json")
        self.event = read("sample_event_company_publicly.json")

    @mock.patch("company_service.CompanyService.change_company_publicly")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    @mock.patch.object(publicly_handler, "verify_user_access")
    def test_change_company_publicly_handler_success_should_return_200_response(
        self,
        mock_verify_user_access,
        mock_create_db_session,
        mock_create_db_engine,
        mock_change_company_publicly,
    ):
        mock_verify_user_access.return_value = True
        mock_change_company_publicly.return_value = True
        data = json.loads(self.event.get("body"))
        expected_response = {"modified": True}

        response = handler(self.event, {})

        mock_change_company_publicly.assert_called_with(data.get("companies"))
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 200)
        self.assertEqual(
            response.get("body"), json.dumps(expected_response, default=str)
        )

    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    @mock.patch.object(publicly_handler, "verify_user_access")
    def test_change_company_publicly_handler_fail_should_return_no_body_error_400_response(
        self,
        mock_verify_user_access,
        mock_create_db_session,
        mock_create_db_engine,
    ):
        error_message = "No company data provided"
        mock_verify_user_access.return_value = True
        response = handler({"requestContext": self.event.get("requestContext")}, {})

        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))

    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    @mock.patch.object(publicly_handler, "verify_user_access")
    def test_get_all_public_companies_handler_success_should_return_error_400_response(
        self,
        mock_verify_user_access,
        mock_create_db_session,
        mock_create_db_engine,
    ):
        error_message = "No permissions to change company publicly"
        mock_verify_user_access.return_value = False

        response = handler(self.event, {})

        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))
