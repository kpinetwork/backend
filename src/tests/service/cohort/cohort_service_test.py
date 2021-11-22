from unittest import TestCase
import logging
from unittest.mock import Mock
from src.service.cohort.cohort_service import (
    CohortService,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestCohortService(TestCase):
    def setUp(self):
        self.cohort = {
            "cohort_id": "1ad345fg",
            "cohort_name": "Cohort",
            "cohort.tag": "tag",
            "companies_margin_group": "",
            "companies_sector": "",
            "companies_vertical": "",
        }
        self.cohort_scenario = {
            "id": "1ad345fg",
            "name": "Test scenario",
            "currency": "USD",
            "type": "Budget",
            "start_at": "2020-01-31",
            "end_at": "2020-12-31",
            "metric_name": "revenue",
            "metric_value": "20",
            "metric_type": "standard",
            "metric_data_type": "integer",
            "metric_start_at": "2020-01-31",
            "metric_end_at": "2020-12-31",
        }
        self.mock_session = Mock()
        self.mock_query_builder = Mock()
        self.mock_response_sql = Mock()
        self.cohort_service_instance = CohortService(
            self.mock_session, self.mock_query_builder, logger, self.mock_response_sql
        )
        return

    def mock_response_query_sql(self, response):
        attrs = {"process_query_result.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def mock_response_list_query_sql(self, response):
        attrs = {"process_query_list_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def test_get_cohort_scenarios_success(self):
        self.mock_response_list_query_sql([self.cohort_scenario])

        get_scenarios_out = self.cohort_service_instance.get_cohort_scenarios(
            "id", "Budget", "2021"
        )

        self.assertEqual(get_scenarios_out, [self.cohort_scenario])
        self.cohort_service_instance.session.execute.assert_called_once()

    def test_get_cohort_scenarios_with_empty_id(self):
        get_scenario_out = self.cohort_service_instance.get_cohort_scenarios(
            "", "Budget", "2021"
        )

        self.assertEqual(get_scenario_out, [])
        self.cohort_service_instance.session.execute.assert_not_called()

    def test_get_cohort_scenarios_with_empty_response_success(self):
        self.mock_response_list_query_sql([])

        get_scenarios_out = self.cohort_service_instance.get_cohort_scenarios(
            "id", "Budget", "2021"
        )

        self.assertEqual(get_scenarios_out, [])
        self.cohort_service_instance.session.execute.assert_called_once()

    def test_get_cohort_scenarios_failed(self):
        self.cohort_service_instance.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.cohort_service_instance.get_cohort_scenarios(
                    "id", "Budget", "2021"
                )
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.cohort_service_instance.session.execute.assert_called_once()

    def test_get_cohort_information_by_id_success(self):
        self.mock_response_query_sql(self.cohort)

        get_cohort_out = self.cohort_service_instance.get_cohort_information_by_id("id")

        self.assertEqual(get_cohort_out, self.cohort)
        self.cohort_service_instance.session.execute.assert_called_once()

    def test_get_cohort_information_by_id_with_empty_id(self):
        self.mock_response_query_sql(dict())

        get_cohort_out = self.cohort_service_instance.get_cohort_information_by_id("")

        self.assertEqual(get_cohort_out, dict())
        self.cohort_service_instance.session.execute.assert_not_called()

    def test_get_cohort_information_by_id_with_empty_response_success(self):
        self.mock_response_query_sql(dict())

        get_cohort_out = self.cohort_service_instance.get_cohort_information_by_id("id")

        self.assertEqual(get_cohort_out, dict())
        self.cohort_service_instance.session.execute.assert_called_once()

    def test_get_cohort_information_by_id_failed(self):
        self.cohort_service_instance.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.cohort_service_instance.get_cohort_information_by_id("id")
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.cohort_service_instance.session.execute.assert_called_once()

    def test_get_cohorts_success(self):
        self.mock_response_list_query_sql([self.cohort])

        get_cohorts_out = self.cohort_service_instance.get_cohorts()

        self.assertEqual(get_cohorts_out, [self.cohort])
        self.cohort_service_instance.session.execute.assert_called_once()

    def test_get_cohorts_with_empty_response_success(self):
        self.mock_response_list_query_sql([])

        get_cohorts_out = self.cohort_service_instance.get_cohorts()

        self.assertEqual(get_cohorts_out, [])
        self.cohort_service_instance.session.execute.assert_called_once()

    def test_get_cohorts_failed(self):
        self.cohort_service_instance.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(self.cohort_service_instance.get_cohorts())

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.cohort_service_instance.session.execute.assert_called_once()
