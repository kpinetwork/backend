import json
from src.tests.data.data_reader import read
from unittest import TestCase, mock
from src.handlers.investment_year_report.get_investment_year_options_handler import (
    handler,
)


class TestInvestmentReportHandler(TestCase):
    def setUp(self):
        self.options = read("sample_invest_year_options.json")

    @mock.patch("investment_options_service.InvestmentOptionsService.get_years_options")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_invest_year_options_handler_success_should_return_200_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_get_years_options,
    ):
        mock_get_years_options.return_value = self.options

        response = handler({}, {})

        mock_get_years_options.assert_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 200)
        self.assertEqual(response.get("body"), json.dumps(self.options))

    @mock.patch("investment_options_service.InvestmentOptionsService.get_years_options")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_invest_year_options_handler_fail_should_return_400_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_get_years_options,
    ):
        mock_get_years_options.side_effect = Exception("error")
        expected_out = {"error": "error"}

        response = handler({}, {})

        mock_get_years_options.assert_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps(expected_out))
