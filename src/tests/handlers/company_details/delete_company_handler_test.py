import json
from src.tests.data.data_reader import read
from unittest import TestCase, mock
from src.handlers.company_details.delete_company_handler import handler
import src.handlers.company_details.delete_company_handler as delete_handler
from src.service.company_details.company_details_service import CompanyDetails


class TestDeleteCompanyHandler(TestCase):
    def setUp(self):
        self.event = read("sample_event_company.json")
        self.company_details = CompanyDetails(
            mock.Mock(), mock.Mock(), mock.Mock(), mock.Mock(), mock.Mock(), mock.Mock()
        )

    @mock.patch("company_details_service.CompanyDetails.delete_company")
    @mock.patch.object(delete_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_delete_company_handler_success_should_return_200_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_delete_company,
    ):
        mock_delete_company.return_value = True
        mock_verify_user_access.return_value = True

        response = handler(self.event, {})

        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 200)
        self.assertEqual(response.get("body"), json.dumps({"deleted": True}))

    @mock.patch.object(delete_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_delete_company_fails_should_return_error_400_response(
        self, mock_create_db_session, mock_create_db_engine, mock_verify_user_access
    ):
        error_message = "No permissions to delete companies"
        mock_verify_user_access.return_value = False

        response = handler(self.event, {})

        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))
