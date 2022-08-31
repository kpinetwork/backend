import json
from src.tests.data.data_reader import read
from parameterized import parameterized
from unittest import TestCase, mock
from src.handlers.company_details.get_company_details_handler import (
    handler,
    get_boolean_from_query,
    get_number_from_query,
)
import src.handlers.company_details.get_company_details_handler as details_handler
from src.service.company_details.company_details_service import CompanyDetails

offset = "offset"
limit = "limit"
ordered = "ordered"


class TestGetCompanyHandler(TestCase):
    def setUp(self):
        self.company = read("sample_company.json")
        self.event = read("sample_event_company.json")
        self.company_details = CompanyDetails(
            mock.Mock(), mock.Mock(), mock.Mock(), mock.Mock(), mock.Mock(), mock.Mock()
        )

    @parameterized.expand(
        [
            [{offset: None}, offset, 0, 0],
            [{offset: "1"}, offset, 0, 1],
            [{limit: "abc"}, limit, 20, 20],
            [{limit: "2"}, limit, 20, 2],
        ]
    )
    def test_get_number_from_query(self, params, field, default_value, expected_value):

        value = get_number_from_query(params, field, default_value)

        self.assertEqual(value, expected_value)

    @parameterized.expand(
        [
            [{ordered: ""}, ordered, False],
            [{ordered: None}, ordered, False],
            [{ordered: "undefined"}, ordered, False],
            [{ordered: "true"}, ordered, True],
            [{ordered: "false"}, ordered, False],
            [{}, ordered, False],
        ]
    )
    def test_get_boolean_from_query(self, params, field, expected_value):

        value = get_boolean_from_query(params, field)
        self.assertEqual(value, expected_value)

    @mock.patch("company_details_service.CompanyDetails.get_company_details")
    @mock.patch.object(details_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_company_details_handler_success_should_return_200_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_verify_user_access,
        mock_get_company_details,
    ):
        mock_get_company_details.return_value = self.company
        id_from_event = self.event.get("pathParameters").get("id")
        mock_verify_user_access.return_value = True

        response = handler(self.event, {})

        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 200)
        self.assertEqual(id_from_event, self.company.get("id"))
        self.assertEqual(response.get("body"), json.dumps(self.company))

    @mock.patch.object(details_handler, "verify_user_access")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_company_fail_should_return_error_400_response(
        self, mock_create_db_session, mock_create_db_engine, mock_verify_user_access
    ):
        error_message = "No permissions to get company details"
        mock_verify_user_access.return_value = False

        response = handler(self.event, {})

        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))
