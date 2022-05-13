import logging
from unittest import TestCase
from unittest.mock import Mock
from parameterized import parameterized
from preview_data_validation_service import (
    PreviewDataValidationService,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestUploadFileService(TestCase):
    def setUp(self):
        self.company_with_financial_info = {
            "f0e51d91-a55a-4f3b-9312-d2bab03b8020": {
                "company_id": "f0e51d91-a55a-4f3b-9312-d2bab03b8020",
                "company_name": "Sample Company",
                "scenarios": {"Budget-2021": ["Revenue"], "Budget-2022": ["Ebitda"]},
            },
            "30e51d91-a55a-4f3b-9312-d2bab03b8020": {
                "company_id": "f0e51d91-a55a-4f3b-9312-d2bab03b8020",
                "company_name": "Sample Company 2",
                "scenarios": {"Budget-2021": ["Revenue"], "Budget-2022": ["Ebitda"]},
            },
        }
        self.mock_session = Mock()
        self.mock_query_builder = Mock()
        self.mock_response_sql = Mock()
        self.preview_data_validation_service_instance = PreviewDataValidationService(
            self.mock_session, self.mock_query_builder, logger, self.mock_response_sql
        )
        return

    def mock_response_query_sql(self, response):
        attrs = {
            "process_companies_data_with_financial_information.return_value": response
        }
        self.mock_response_sql.configure_mock(**attrs)

    def test_get_companies_data_success(self):
        self.mock_response_query_sql(self.company_with_financial_info)

        get_companies_out = (
            self.preview_data_validation_service_instance.get_companies_data()
        )

        self.assertEqual(get_companies_out, self.company_with_financial_info)
        self.preview_data_validation_service_instance.session.execute.assert_called_once()

    def test_get_companies_data_failed(self):
        self.preview_data_validation_service_instance.session.execute.side_effect = (
            Exception("error")
        )
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.preview_data_validation_service_instance.get_companies_data()
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.preview_data_validation_service_instance.session.execute.assert_called_once()

    @parameterized.expand(
        [
            [
                [
                    {
                        "company_id": "f0e51d91-a55a-4f3b-9312-d2bab03b8020",
                        "company_name": "Sample Company",
                        "scenarios": {"Budget": {"2021": ["Revenue"]}},
                    }
                ],
                {
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
                },
            ],
            [
                [
                    {
                        "company_id": "f0e51d91-a55a-4f3b-9312-d2bab03b8020",
                        "company_name": "Sample Company",
                        "scenarios": {"Budget": {"2023": ["Revenue"]}},
                    }
                ],
                {
                    "repeated_ids": {},
                    "repeated_names": {},
                    "existing_names": [],
                    "validated_companies": [
                        {
                            "company_id": "f0e51d91-a55a-4f3b-9312-d2bab03b8020",
                            "company_name": "Sample Company",
                            "scenarios": {"Budget-2023": {"Revenue": False}},
                        }
                    ],
                },
            ],
            [
                [
                    {
                        "company_name": "Sample Company",
                        "scenarios": {"Budget": {"2021": ["Revenue"]}},
                    }
                ],
                {
                    "repeated_ids": {},
                    "repeated_names": {},
                    "existing_names": ["Sample Company"],
                    "validated_companies": [],
                },
            ],
        ]
    )
    def test_validate_companies_data_success(self, companies_to_validate, expected):
        self.mock_response_query_sql(self.company_with_financial_info)

        validated_companies = (
            self.preview_data_validation_service_instance.validate_companies_data(
                companies_to_validate
            )
        )

        self.assertEqual(validated_companies, expected)

    def test_validate_companies_data_failed(self):
        self.preview_data_validation_service_instance.session.execute.side_effect = (
            Exception("error")
        )
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.preview_data_validation_service_instance.validate_companies_data(
                    []
                )
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.preview_data_validation_service_instance.session.execute.assert_called_once()
