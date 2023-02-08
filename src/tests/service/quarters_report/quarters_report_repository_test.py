from unittest import TestCase
import logging
from unittest.mock import Mock, patch
from src.service.quarters_report.quarters_report_repository import (
    QuartersReportRepository,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestQuartersReportRepository(TestCase):
    def setUp(self):
        self.mock_session = Mock()
        self.mock_query_builder = Mock()
        self.mock_response_sql = Mock()
        self.repository = QuartersReportRepository(
            self.mock_session, self.mock_query_builder, self.mock_response_sql, logger
        )
        self.records = [
            {
                "id": "1",
                "name": "Test",
                "scenario": "Actuals-2020",
                "metric": "Revenue",
                "year": 2020,
                "value": 20,
                "period_name": "Q1",
                "average": 2,
                "full_year_average": 3,
                "full_year": 2,
                "count_periods": 1,
            },
            {
                "id": "2",
                "name": "Company",
                "scenario": "Actuals-2021",
                "metric": "Revenue",
                "year": 2021,
                "value": 22,
                "period_name": "Q1",
                "average": 9,
                "full_year_average": 2,
                "full_year": 1,
                "count_periods": 4,
            },
        ]

    def mock_response_list_query_sql(self, response):
        attrs = {"process_query_list_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    @patch.object(QuartersReportRepository, "get_base_query")
    def test_get_metric_by_quarters_should_call_function(self, mock_base_query):
        mock_base_query.return_value = "Mock subquery"
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_metric_records_by_quarters(
            "year_year", "revenue", "Actuals", [2021, 2022], dict()
        )

        self.assertEqual(metrics, self.records)

    def test_get_metric_by_quarters_shoudl_fail_with_invalid_metric(self):
        with self.assertRaises(Exception) as context:
            self.repository.get_metric_records_by_quarters(
                "year_year", "invalid", "Actuals", [2021, 2022], dict()
            )

        self.assertEqual(str(context.exception), "Metric not found")

    def test_get_base_metric_records_should_return_empty_list_when_fails(self):
        self.mock_session.execute.side_effect = Exception("error")

        metrics = self.repository.get_base_metric_records(
            "revenue", "Actuals", [2021, 2022], dict()
        )

        self.assertEqual(metrics, [])

    def test_get_actuals_plus_budget_metrics_query_should_return_empty_list_when_fails(
        self,
    ):
        self.mock_session.execute.side_effect = Exception("error")

        metrics = self.repository.get_actuals_plus_budget_metrics_query(
            "revenue", [2021, 2022], dict()
        )

        self.assertEqual(metrics, [])

    def test_get_actuals_plus_budget_metrics_query_when_sucess_should_return_records(
        self,
    ):
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_actuals_plus_budget_metrics_query(
            "revenue", [2021, 2022], dict()
        )

        self.assertEqual(metrics, self.records)
