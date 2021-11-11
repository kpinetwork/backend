from unittest import TestCase
import logging
from unittest.mock import Mock
from src.service.company.company_service import CompanyService

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class TestCompanyService(TestCase):
    def setUp(self):
        self.company = {
            "id": "1ad345fg",
            "name": "Test Company",
            "from_date": "2020-01-01",
            "fiscal_year": "2020-01-01",
            "sector": "Science",
            "vertical": "Technology",
            "inves_profile_name": "Small",
        }
        self.revenue_sum = {
            "id": "company_id",
            "name": "Test Company",
            "revenue_sum": 123,
        }
        self.mock_session = Mock()
        self.mock_query_builder = Mock()
        self.mock_response_sql = Mock()
        self.company_service_instance = CompanyService(
            self.mock_session, self.mock_query_builder, logger, self.mock_response_sql
        )
        return

    def mock_response_query_sql(self, response):
        attrs = {"process_query_result.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def mock_response_list_query_sql(self, response):
        attrs = {"process_query_list_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def test_get_company_success(self):
        self.mock_response_query_sql(self.company)

        get_company_out = self.company_service_instance.get_company(
            self.company.get("id")
        )

        self.assertEqual(get_company_out, self.company)
        self.company_service_instance.session.execute.assert_called_once()

    def test_get_company_with_empty_response_success(self):
        self.mock_response_query_sql(dict())

        get_company_out = self.company_service_instance.get_company(
            self.company.get("id")
        )

        self.assertEqual(get_company_out, dict())
        self.company_service_instance.session.execute.assert_called_once()

    def test_get_company_with_empty_id(self):
        get_company_out = self.company_service_instance.get_company("")

        self.assertEqual(get_company_out, dict())
        self.company_service_instance.session.execute.assert_not_called()

    def test_get_company_failed(self):
        self.company_service_instance.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.company_service_instance.get_company(self.company.get("id"))
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.company_service_instance.session.execute.assert_called_once()

    def test_get_all_companies_success(self):
        self.mock_response_list_query_sql([self.company])

        get_all_companies_out = self.company_service_instance.get_all_companies()

        self.assertEqual(get_all_companies_out, [self.company])
        self.assertEqual(len(get_all_companies_out), len([self.company]))
        self.company_service_instance.session.execute.assert_called_once()

    def test_get_all_companies_failed(self):
        self.company_service_instance.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.company_service_instance.get_all_companies()
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.company_service_instance.session.execute.assert_called_once()

    def test_get_revenue_sum_by_company_success(self):
        self.mock_response_list_query_sql([self.revenue_sum])

        get_all_companies_out = (
            self.company_service_instance.get_revenue_sum_by_company()
        )

        self.assertEqual(get_all_companies_out, [self.revenue_sum])
        self.assertEqual(len(get_all_companies_out), len([self.revenue_sum]))
        self.company_service_instance.session.execute.assert_called_once()

    def test_get_revenue_sum_by_company_failed(self):
        self.company_service_instance.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.company_service_instance.get_revenue_sum_by_company()
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.company_service_instance.session.execute.assert_called_once()
