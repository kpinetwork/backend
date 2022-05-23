import json
from src.tests.data.data_reader import read
from unittest import TestCase, mock
from src.handlers.investments.add_investment_handler import handler


class TestGetCompanyInvestmentHandler(TestCase):
    def setUp(self):
        self.event = read("sample_event_add_investment.json")
        self.response = read("sample_response_investment.json")

    @mock.patch("investments_service.InvestmentsService.add_investment")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_add_investment_handler_success_should_return_201_response(
        self, mock_create_db_session, mock_create_db_engine, mock_add_investment
    ):
        id_from_event = self.event.get("pathParameters").get("company_id")
        investment_from_event = self.event.get("body")
        mock_add_investment.return_value = self.response

        response = handler(self.event, {})

        mock_add_investment.assert_called_with(id_from_event, investment_from_event)
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 201)
        self.assertTrue(self.response.get("added"))
        self.assertEqual(self.response.get("investment"), investment_from_event)

    @mock.patch("investments_service.InvestmentsService.add_investment")
    def test_add_investment_fail_no_body_400_response(self, mock_add_investment):
        error_message = "No data provided"

        response = handler({}, {})

        mock_add_investment.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))
