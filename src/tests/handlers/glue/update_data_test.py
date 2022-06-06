import json
from src.tests.data.data_reader import read
from unittest import TestCase, mock
from src.handlers.glue.update_data import handler


class TestGetCompanyInvestmentHandler(TestCase):
    def setUp(self):
        self.event = read("sample_event_update_data.json")

    @mock.patch("update_data_service.UpdateDataService.update_data")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_update_data_success_should_return_201_response(
        self, mock_create_db_session, mock_create_db_engine, mock_update_data
    ):
        companies_from_event = json.loads(self.event.get("body")).get("companies")
        metrics_from_event = json.loads(self.event.get("body")).get("metrics")

        mock_update_data.return_value = json.dumps({"updated": True})

        response = handler(self.event, {})

        mock_update_data.assert_called_with(companies_from_event, metrics_from_event)
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 200)
        self.assertEqual(response.get("body"), json.dumps({"updated": True}))

    @mock.patch("update_data_service.UpdateDataService.update_data")
    def test_update_data_fail_no_body_400_response(self, mock_update_data):
        error_message = "No data provided"

        response = handler({}, {})

        mock_update_data.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))

    @mock.patch("update_data_service.UpdateDataService.update_data")
    def test_update_data_fail_no_companies_and_metrics_400_response(
        self, mock_update_data
    ):
        error_message = "No data provided"

        response = handler({"body": '{"companies": [], "metrics": []}'}, {})

        mock_update_data.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))
