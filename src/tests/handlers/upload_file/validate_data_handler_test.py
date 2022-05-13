import json
from src.tests.data.data_reader import read
from unittest import TestCase, mock
from src.handlers.upload_file.validate_data_handler import handler


class TestValidateDataHandler(TestCase):
    def setUp(self):
        self.companies = read("sample_company_with_scenarios.json")
        self.event = read("sample_event_validate_data.json")
        self.validated_companies = {
            "repeated_ids": {},
            "repeated_names": {},
            "existing_names": [],
            "validated_companies": [
                {
                    "company_id": "f0e51d91-a55a-4f3b-9312-d2bab03b8020",
                    "company_name": "Sample Company",
                    "scenarios": {"Budget-2021": {"Revenue": True}},
                }
            ],
        }

    @mock.patch(
        "preview_data_validation_service.PreviewDataValidationService.validate_companies_data"
    )
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_validate_data_handler_success_should_return_200_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_validate_companies_data,
    ):
        data = json.loads(self.event.get("body"))
        mock_validate_companies_data.return_value = self.validated_companies

        response = handler(self.event, {})

        mock_validate_companies_data.assert_called_with(data)
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 200)
        self.assertEqual(
            response.get("body"), json.dumps(self.validated_companies, default=str)
        )

    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_validate_data_handler_fail_should_return_no_body_error_400_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
    ):
        error_message = "No company data provided"
        response = handler({}, {})

        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))

    @mock.patch(
        "preview_data_validation_service.PreviewDataValidationService.validate_companies_data"
    )
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_validate_data_handler_fail_should_return_error_400_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_validate_companies_data,
    ):
        error_message = "Cannot get companies"
        mock_validate_companies_data.side_effect = Exception(error_message)

        response = handler(self.event, {})

        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))
