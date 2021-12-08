from unittest import TestCase
import logging
from unittest.mock import Mock
from src.service.universe_overview.universe_overview_service import (
    UniverseOverviewService,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestUniverseOverview(TestCase):
    def setUp(self):
        self.size_cohort = {"size_cohort": "size_cohort_1", "count": 1}
        self.mock_session = Mock()
        self.mock_query_builder = Mock()
        self.mock_response_sql = Mock()
        self.overview_service_instance = UniverseOverviewService(
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

    def test_get_companies_count_by_size_success(self):
        self.mock_response_list_query_sql([self.size_cohort])

        get_companies_count_by_size_out = (
            self.overview_service_instance.get_companies_count_by_size(
                "Sector test", "Vertical test"
            )
        )

        self.assertEqual(get_companies_count_by_size_out, [self.size_cohort])
        self.assertEqual(len(get_companies_count_by_size_out), len([self.size_cohort]))
        self.overview_service_instance.session.execute.assert_called_once()

    def test_get_companies_count_by_size_with_empty_arguments_success(self):
        self.mock_response_list_query_sql([self.size_cohort])

        get_companies_count_by_size_out = (
            self.overview_service_instance.get_companies_count_by_size("", "")
        )

        self.assertEqual(get_companies_count_by_size_out, [self.size_cohort])
        self.assertEqual(len(get_companies_count_by_size_out), len([self.size_cohort]))
        self.overview_service_instance.session.execute.assert_called_once()

    def test_get_companies_count_by_size_failed(self):
        self.overview_service_instance.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.overview_service_instance.get_companies_count_by_size(
                    "Sector test", "Vertical test"
                )
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.overview_service_instance.session.execute.assert_called_once()

    def test_get_metric_avg_by_size_cohort_with_valid_metric_and_scenario(self):
        self.mock_response_list_query_sql([self.size_cohort])

        get_metric_avg_by_size_cohort_out = (
            self.overview_service_instance.get_metric_avg_by_size_cohort(
                "Budget", "Revenue", "", "", "2020", "count"
            )
        )

        self.assertEqual(get_metric_avg_by_size_cohort_out, [self.size_cohort])
        self.overview_service_instance.session.execute.assert_called_once()

    def test_get_metric_avg_by_size_cohort_without_valid_metric_and_scenario(self):
        get_metric_avg_by_size_cohort_out = (
            self.overview_service_instance.get_metric_avg_by_size_cohort(
                "", "", "", "", "2020", "count"
            )
        )

        self.assertEqual(get_metric_avg_by_size_cohort_out, [])
        self.overview_service_instance.session.execute.assert_not_called()

    def test_get_metric_avg_by_size_cohort_with_all_params(self):
        self.mock_response_list_query_sql([self.size_cohort])

        get_metric_avg_by_size_cohort_out = (
            self.overview_service_instance.get_metric_avg_by_size_cohort(
                "Budget", "Revenue", "Science", "Maths", "2020", "count"
            )
        )

        self.assertEqual(get_metric_avg_by_size_cohort_out, [self.size_cohort])
        self.overview_service_instance.session.execute.assert_called_once()

    def test_get_metric_avg_by_size_cohort_with_empty_response(self):
        self.mock_response_list_query_sql([])

        get_metric_avg_by_size_cohort_out = (
            self.overview_service_instance.get_metric_avg_by_size_cohort(
                "Budget", "Revenue", "Science", "Maths", "2020", "count"
            )
        )

        self.assertEqual(get_metric_avg_by_size_cohort_out, [])
        self.overview_service_instance.session.execute.assert_called_once()

    def test_get_metric_avg_by_size_cohort_failed(self):
        self.overview_service_instance.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.overview_service_instance.get_metric_avg_by_size_cohort(
                    "Budget", "Revenue", "Science", "Maths", "2020", "count"
                )
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.overview_service_instance.session.execute.assert_called_once()
