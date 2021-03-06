from unittest import TestCase
import logging
from unittest.mock import Mock
from src.service.company.company_service import CompanyService
from src.utils.company_anonymization import CompanyAnonymization

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
            "is_public": False,
        }
        self.revenue_sum = {
            "id": "company_id",
            "name": "Test Company",
            "revenue_sum": 123,
        }
        self.total_companies = {"count": 1}
        self.all_companies = {
            "total": self.total_companies.get("count"),
            "companies": [self.company],
        }
        self.all_public_companies = {
            "total": self.total_companies.get("count"),
            "companies": [self.company],
        }
        self.metric_size_cohort = {"size_cohort": "1", "growth": "123"}
        self.metric_avg = {"revenue": "100"}
        self.companies_data = {"compani_id_01": True, "companie_id_02": False}
        self.mock_session = Mock()
        self.mock_query_builder = Mock()
        self.mock_response_sql = Mock()
        self.company_service_instance = CompanyService(
            self.mock_session,
            self.mock_query_builder,
            logger,
            self.mock_response_sql,
            CompanyAnonymization(object()),
        )
        return

    def mock_response_query_sql(self, response):
        attrs = {"process_query_result.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def mock_response_list_query_sql(self, response):
        attrs = {"process_query_list_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def mock_response_metrics_group_by_size_cohort_results(self, response):
        attrs = {"process_metrics_group_by_size_cohort_results.return_value": response}
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
        self.mock_response_query_sql(self.total_companies)
        self.mock_response_list_query_sql([self.company])

        get_all_companies_out = self.company_service_instance.get_all_companies()

        self.assertEqual(get_all_companies_out, self.all_companies)
        self.assertEqual(
            len(get_all_companies_out.get("companies")), len([self.company])
        )
        self.assertEqual(self.company_service_instance.session.execute.call_count, 2)

    def test_get_all_companies_failed(self):
        self.company_service_instance.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.company_service_instance.get_all_companies()
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.company_service_instance.session.execute.assert_called_once()

    def test_get_total_number_of_companies_success(self):
        self.mock_response_query_sql(self.total_companies)

        get_total_number_of_companies = (
            self.company_service_instance.get_total_number_of_companies(public=False)
        )

        self.assertEqual(get_total_number_of_companies, self.total_companies)
        self.company_service_instance.session.execute.assert_called_once()

    def test_get_total_number_of_companies_failed(self):
        self.company_service_instance.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.company_service_instance.get_total_number_of_companies(
                    public=False
                )
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.company_service_instance.session.execute.assert_called_once()

    def test_get_all_public_companies_with_access_should_return_no_anonymized_data(
        self,
    ):
        self.mock_response_query_sql(self.total_companies)
        self.mock_response_list_query_sql([self.company])

        get_all_companies_out = self.company_service_instance.get_all_public_companies(
            access=True
        )

        self.assertEqual(get_all_companies_out, self.all_public_companies)
        self.assertEqual(self.company_service_instance.session.execute.call_count, 2)

    def test_get_all_public_companies_without_access_should_return_hiden_companies(
        self,
    ):
        self.mock_response_query_sql(self.total_companies)
        self.mock_response_list_query_sql([self.company])

        get_all_companies_out = self.company_service_instance.get_all_public_companies(
            access=False
        )

        self.assertEqual(get_all_companies_out, {"total": 1, "companies": []})
        self.assertEqual(self.company_service_instance.session.execute.call_count, 2)

    def test_get_all_public_companies_should_return_empty_result(self):
        self.mock_response_query_sql({"count": 0})
        self.mock_response_list_query_sql([])

        get_all_companies_out = self.company_service_instance.get_all_public_companies(
            access=True
        )

        self.assertEqual(get_all_companies_out, {"total": 0, "companies": []})
        self.assertEqual(self.company_service_instance.session.execute.call_count, 2)

    def test_get_all_public_companies_failed(self):
        self.company_service_instance.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.company_service_instance.get_all_public_companies()
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.company_service_instance.session.execute.assert_called_once()

    def test_change_company_publicly_success(self):

        response_change_company_publicly = (
            self.company_service_instance.change_company_publicly(self.companies_data)
        )

        self.assertTrue(response_change_company_publicly)
        self.company_service_instance.session.execute.assert_called_once()

    def test_change_company_publicly_with_empty_parameter(self):
        response_change_company_publicly = (
            self.company_service_instance.change_company_publicly({})
        )

        self.assertTrue(response_change_company_publicly)
        self.company_service_instance.session.execute.assert_called_once()

    def test_change_company_publicly_failed(self):
        self.company_service_instance.session.execute.side_effect = Exception("error")

        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.company_service_instance.change_company_publicly(
                    self.companies_data
                )
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.company_service_instance.session.execute.assert_called_once()
