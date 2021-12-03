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
        self.metric_size_cohort = {"size_cohort": "1", "growth": "123"}

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

    def test_get_companies_kpi_average_with_all_arguments_success(self):
        self.mock_response_query_sql([self.company])

        get_companies_kpi_average_out = (
            self.company_service_instance.get_companies_kpi_average(
                "Budget", "Ebitda", "2021", "Semiconductors", "Transportation"
            )
        )

        self.assertEqual(get_companies_kpi_average_out, [self.company])
        self.company_service_instance.session.execute.assert_called_once()

    def test_get_companies_kpi_average_failed(self):
        self.company_service_instance.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.company_service_instance.get_companies_kpi_average(
                    "Budget", "Ebitda", "2021", "Semiconductors", "Transportation"
                )
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.company_service_instance.session.execute.assert_called_once()

    def test_get_companies_kpi_average_without_sector_success(self):
        self.mock_response_query_sql([self.company])

        get_companies_kpi_average_out = (
            self.company_service_instance.get_companies_kpi_average(
                "Budget", "Ebitda", "2021", "", "Transportation"
            )
        )

        self.assertEqual(get_companies_kpi_average_out, [self.company])
        self.company_service_instance.session.execute.assert_called_once()

    def test_get_companies_kpi_average_without_vertical_success(self):
        self.mock_response_query_sql([self.company])

        get_companies_kpi_average_out = (
            self.company_service_instance.get_companies_kpi_average(
                "Budget", "Ebitda", "2021", "Sector", ""
            )
        )

        self.assertEqual(get_companies_kpi_average_out, [self.company])
        self.company_service_instance.session.execute.assert_called_once()

    def test_get_companies_kpi_average_without_sector_and_vertical_success(self):
        self.mock_response_query_sql([self.company])

        get_companies_kpi_average_out = (
            self.company_service_instance.get_companies_kpi_average(
                "Budget", "Ebitda", "2021", "", ""
            )
        )

        self.assertEqual(get_companies_kpi_average_out, [self.company])
        self.company_service_instance.session.execute.assert_called_once()

    def test_get_companies_count_by_size_success(self):
        self.mock_response_list_query_sql([self.company])

        get_companies_count_by_size_out = (
            self.company_service_instance.get_companies_count_by_size(
                "Sector test", "Vertical test"
            )
        )

        self.assertEqual(get_companies_count_by_size_out, [self.company])
        self.assertEqual(len(get_companies_count_by_size_out), len([self.company]))
        self.company_service_instance.session.execute.assert_called_once()

    def test_get_companies_count_by_size_with_empty_arguments_success(self):
        self.mock_response_list_query_sql([self.company])

        get_companies_count_by_size_out = (
            self.company_service_instance.get_companies_count_by_size("", "")
        )

        self.assertEqual(get_companies_count_by_size_out, [self.company])
        self.assertEqual(len(get_companies_count_by_size_out), len([self.company]))
        self.company_service_instance.session.execute.assert_called_once()

    def test_get_companies_count_by_size_with_sector_success(self):
        self.mock_response_list_query_sql([self.company])

        get_companies_count_by_size_out = (
            self.company_service_instance.get_companies_count_by_size("Sector", "")
        )

        self.assertEqual(get_companies_count_by_size_out, [self.company])
        self.assertEqual(len(get_companies_count_by_size_out), len([self.company]))
        self.company_service_instance.session.execute.assert_called_once()

    def test_get_companies_count_by_size_with_vertical_success(self):
        self.mock_response_list_query_sql([self.company])

        get_companies_count_by_size_out = (
            self.company_service_instance.get_companies_count_by_size("", "vertical")
        )

        self.assertEqual(get_companies_count_by_size_out, [self.company])
        self.assertEqual(len(get_companies_count_by_size_out), len([self.company]))
        self.company_service_instance.session.execute.assert_called_once()

    def test_get_companies_count_by_size_failed(self):
        self.company_service_instance.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.company_service_instance.get_companies_count_by_size(
                    "Sector test", "Vertical test"
                )
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

    def test_get_metric_avg_by_size_cohort_with_valid_metric_and_scenario(self):
        self.mock_response_list_query_sql([self.metric_size_cohort])

        get_metric_avg_by_size_cohort_out = (
            self.company_service_instance.get_metric_avg_by_size_cohort(
                "Budget", "Revenue", "", "", "2020", "growth"
            )
        )

        self.assertEqual(get_metric_avg_by_size_cohort_out, [self.metric_size_cohort])
        self.company_service_instance.session.execute.assert_called_once()

    def test_get_metric_avg_by_size_cohort_without_valid_metric_and_scenario(self):
        get_metric_avg_by_size_cohort_out = (
            self.company_service_instance.get_metric_avg_by_size_cohort(
                "", "", "", "", "2020", "growth"
            )
        )

        self.assertEqual(get_metric_avg_by_size_cohort_out, [])
        self.company_service_instance.session.execute.assert_not_called()

    def test_get_metric_avg_by_size_cohort_with_all_params(self):
        self.mock_response_list_query_sql([self.metric_size_cohort])

        get_metric_avg_by_size_cohort_out = (
            self.company_service_instance.get_metric_avg_by_size_cohort(
                "Budget", "Revenue", "Science", "Maths", "2020", "growth"
            )
        )

        self.assertEqual(get_metric_avg_by_size_cohort_out, [self.metric_size_cohort])
        self.company_service_instance.session.execute.assert_called_once()

    def test_get_metric_avg_by_size_cohort_with_empty_response(self):
        self.mock_response_list_query_sql([])

        get_metric_avg_by_size_cohort_out = (
            self.company_service_instance.get_metric_avg_by_size_cohort(
                "Budget", "Revenue", "Science", "Maths", "2020", "growth"
            )
        )

        self.assertEqual(get_metric_avg_by_size_cohort_out, [])
        self.company_service_instance.session.execute.assert_called_once()

    def test_get_metric_avg_by_size_cohort_failed(self):
        self.company_service_instance.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.company_service_instance.get_metric_avg_by_size_cohort(
                    "Budget", "Revenue", "Science", "Maths", "2020", "growth"
                )
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.company_service_instance.session.execute.assert_called_once()

    def test_get_growth_and_margin_by_size_cohort_success(self):
        record = self.metric_size_cohort.copy()
        record["margin"] = record.pop("growth")

        expected_out = {"1": [self.metric_size_cohort, record]}

        self.mock_response_metrics_group_by_size_cohort_results(expected_out)

        get_growth_and_margin_by_size_cohort_out = (
            self.company_service_instance.get_growth_and_margin_by_size_cohort(
                "", "", "2020"
            )
        )

        self.assertEqual(get_growth_and_margin_by_size_cohort_out, expected_out)
        self.company_service_instance.session.execute.assert_called()
        self.assertEqual(self.company_service_instance.session.execute.call_count, 2)

    def test_get_growth_and_margin_by_size_cohort_success_with_empty_response(self):
        self.mock_response_metrics_group_by_size_cohort_results(dict())

        get_growth_and_margin_by_size_cohort_out = (
            self.company_service_instance.get_growth_and_margin_by_size_cohort(
                "", "", "2020"
            )
        )

        self.assertEqual(get_growth_and_margin_by_size_cohort_out, dict())
        self.company_service_instance.session.execute.assert_called()
        self.assertEqual(self.company_service_instance.session.execute.call_count, 2)

    def test_get_growth_and_margin_by_size_cohort_failed(self):
        self.company_service_instance.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.company_service_instance.get_growth_and_margin_by_size_cohort(
                    "", "", "2020"
                )
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.company_service_instance.session.execute.assert_called_once()
