import json
from src.tests.data.data_reader import read
from unittest import TestCase, mock
from src.handlers.company_details.get_full_year_total_handler import handler
import src.handlers.company_details.get_full_year_total_handler as full_year_handler
from src.service.company_details.company_details_service import CompanyDetails

offset = "offset"
limit = "limit"
ordered = "ordered"


class TestGetCompanyHandler(TestCase):
    def setUp(self):
        self.total = {"total": 20.0}
        self.event = read("sample_event_get_full_year_total.json")
        self.company_details = CompanyDetails(
            mock.Mock(), mock.Mock(), mock.Mock(), mock.Mock(), mock.Mock(), mock.Mock()
        )

    @mock.patch("company_details_service.CompanyDetails.get_full_year_total_amount")
    @mock.patch.object(full_year_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_company_full_year_handler_success_should_return_200_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_get_full_year_total_amount,
    ):
        mock_get_full_year_total_amount.return_value = self.total
        mock_verify_user_access.return_value = True

        response = handler(self.event, {})

        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()

        self.assertEqual(response.get("statusCode"), 200)
        self.assertEqual(response.get("body"), json.dumps(self.total))

    @mock.patch("company_details_service.CompanyDetails.get_full_year_total_amount")
    @mock.patch.object(full_year_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_company_full_year_handler_success_should_return_200_response_and_zero(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_get_full_year_total_amount,
    ):

        mock_get_full_year_total_amount.return_value = {"total": 0}
        mock_verify_user_access.return_value = True

        response = handler(self.event, {})

        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()

        self.assertEqual(response.get("statusCode"), 200)
        self.assertEqual(response.get("body"), json.dumps({"total": 0}))

    @mock.patch.object(full_year_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_company_full_year_handler_fails_should_return_error_400_response(
        self, mock_create_db_session, mock_create_db_engine, mock_verify_user_access
    ):
        error_message = "No permissions to get the total"
        mock_verify_user_access.return_value = False

        response = handler(self.event, {})

        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))
