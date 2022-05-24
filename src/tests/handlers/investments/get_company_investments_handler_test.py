import json
from src.tests.data.data_reader import read
from unittest import TestCase, mock
from src.handlers.investments.get_company_investments_handler import handler


class TestGetCompanyInvestmentHandler(TestCase):
    def setUp(self):
        self.investments = read("sample_investments.json")
        self.event = read("sample_event_investment.json")

    @mock.patch("investments_service.InvestmentsService.get_company_investments")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_company_investments_handler_success_should_return_200_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_get_company_investments,
    ):
        mock_get_company_investments.return_value = self.investments
        id_from_event = self.event.get("pathParameters").get("company_id")

        response = handler(self.event, {})

        mock_get_company_investments.assert_called_with(
            self.investments[0].get("company_id")
        )
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 200)
        self.assertEqual(id_from_event, self.investments[0].get("company_id"))
        self.assertEqual(
            response.get("body"), json.dumps(self.investments, default=str)
        )

    @mock.patch("investments_service.InvestmentsService.get_company_investments")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_company_investment_fail_should_return_error_400_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_get_company_investments,
    ):
        error_message = "Cannot get company"
        mock_get_company_investments.side_effect = Exception(error_message)

        response = handler(self.event, {})

        mock_get_company_investments.assert_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))
