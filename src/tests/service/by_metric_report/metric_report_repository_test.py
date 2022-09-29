from unittest import TestCase
import logging
from unittest.mock import Mock
from src.service.by_metric_report.metric_report_repository import MetricReportRepository
from parameterized import parameterized

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestMetricReportRepository(TestCase):
    def setUp(self):
        self.mock_session = Mock()
        self.mock_query_builder = Mock()
        self.mock_response_sql = Mock()
        self.repository = MetricReportRepository(
            self.mock_session, self.mock_query_builder, self.mock_response_sql, logger
        )
        self.records = [
            {"id": "1", "name": "Test", "year": 2020, "value": 20},
            {"id": "2", "name": "Company", "year": 2021, "value": 13},
        ]

    def mock_response_list_query_sql(self, response):
        attrs = {"process_query_list_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def test_add_company_filters_with_data(self):
        expected_out = {"company.sector": ["'Application'"]}

        filters_out = self.repository.add_company_filters(sector=["Application"])

        self.assertEqual(filters_out, expected_out)

    def test_get_years_success(self):
        expected_years = [2020, 2021, 2022]
        self.mock_response_list_query_sql(
            [{"year": 2020}, {"year": 2021}, {"year": 2022}]
        )

        years = self.repository.get_years()

        self.assertEqual(years, expected_years)

    def test_get_years_fail(self):
        self.mock_session.execute.side_effect = Exception("error")

        years = self.repository.get_years()

        self.assertEqual(years, [])

    def test_get_base_metric_success(self):
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_base_metric("Revenue", "Actuals", dict())

        self.assertEqual(metrics, self.records)

    def test_get_base_metric_fail(self):
        self.mock_session.execute.side_effect = Exception("error")

        metrics = self.repository.get_base_metric("Revenue", "Actuals", dict())

        self.assertEqual(metrics, [])

    def test_get_actuals_vs_budget_metric_success(self):
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_actuals_vs_budget_metric("Ebitda", dict())

        self.assertEqual(metrics, self.records)

    def test_get_actuals_vs_budget_metric_fail(self):
        self.mock_session.execute.side_effect = Exception("error")

        metrics = self.repository.get_actuals_vs_budget_metric("Ebitda", dict())

        self.assertEqual(metrics, [])

    def test_get_ebitda_margin_success(self):
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_ebitda_margin_metric(dict())

        self.assertEqual(metrics, self.records)

    def test_get_ebitda_margin_fail(self):
        self.mock_session.execute.side_effect = Exception("error")

        metrics = self.repository.get_ebitda_margin_metric(dict())

        self.assertEqual(metrics, [])

    def test_get_most_recent_revenue_success(self):
        expected_metrics = [
            {"id": "1", "name": "Actuals-2021", "value": 30},
            {"id": "1", "name": "Actuals-2020", "value": 20},
        ]
        self.mock_response_list_query_sql(expected_metrics)

        metrics = self.repository.get_most_recents_revenue(dict())

        self.assertEqual(metrics, expected_metrics)

    def test_get_most_recent_revenue_fail(self):
        self.mock_session.execute.side_effect = Exception("error")

        metrics = self.repository.get_most_recents_revenue(dict())

        self.assertEqual(metrics, [])

    @parameterized.expand(
        [
            ["Revenue", None, {"filters": {}, "metric": "Revenue"}],
            [None, "Actuals", {"filters": {}, "scenario": "Actuals"}],
            [
                "Ebitda",
                "Actuals",
                {"filters": {}, "metric": "Ebitda", "scenario": "Actuals"},
            ],
        ]
    )
    def test_get_arguments(self, metric, scenario, expected_arguments):

        arguments = self.repository._MetricReportRepository__get_arguments(
            {}, metric, scenario
        )

        self.assertEqual(arguments, expected_arguments)

    def test_get_metric_records_should_call_function(self):
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_metric_records("actuals_ebitda", dict())

        self.assertEqual(metrics, self.records)

    def test_get_metric_records_shoudl_fail_with_invalid_metric(self):
        with self.assertRaises(Exception) as context:
            self.repository.get_metric_records("invalid", dict())

        self.assertEqual(str(context.exception), "Metric not found")

    def test_get_gross_profit_should_return_list_on_success(self):
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_gross_profit(dict())

        self.assertEqual(metrics, self.records)

    def test_get_gross_profit_should_return_empty_list_when_fails(self):
        self.mock_session.execute.side_effect = Exception("error")

        metrics = self.repository.get_gross_profit(dict())

        self.assertEqual(metrics, [])

    def test_get_gross_margin_should_return_list_on_success(self):
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_gross_margin(dict())

        self.assertEqual(metrics, self.records)

    def test_get_gross_margin_should_return_empty_list_when_fails(self):
        self.mock_session.execute.side_effect = Exception("error")

        metrics = self.repository.get_gross_margin(dict())

        self.assertEqual(metrics, [])

    def test_get_revenue_per_employee_return_list_on_success(self):
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_revenue_per_employee(dict())

        self.assertEqual(metrics, self.records)

    def test_get_revenue_per_employee_should_return_empty_list_when_fails(self):
        self.mock_session.execute.side_effect = Exception("error")

        metrics = self.repository.get_revenue_per_employee(dict())

        self.assertEqual(metrics, [])

    def test_get_opex_as_revenue_return_list_on_success(self):
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_opex_as_revenue(dict())

        self.assertEqual(metrics, self.records)

    def test_get_opex_as_revenue_should_return_empty_list_when_fails(self):
        self.mock_session.execute.side_effect = Exception("error")

        metrics = self.repository.get_opex_as_revenue(dict())

        self.assertEqual(metrics, [])

    def test_get_debt_ebitda_return_list_on_success(self):
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_debt_ebitda(dict())

        self.assertEqual(metrics, self.records)

    def test_get_debt_ebitda_should_return_empty_list_when_fails(self):
        self.mock_session.execute.side_effect = Exception("error")

        metrics = self.repository.get_debt_ebitda(dict())

        self.assertEqual(metrics, [])

    def test_get_gross_retention_return_list_on_success(self):
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_gross_retention(dict())

        self.assertEqual(metrics, self.records)

    def test_get_gross_retention_should_return_empty_list_when_fails(self):
        self.mock_session.execute.side_effect = Exception("error")

        metrics = self.repository.get_gross_retention(dict())

        self.assertEqual(metrics, [])

    def test_get_metric_ratio_return_list_on_success(self):
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_metric_ratio("CAV", "CAC", dict())

        self.assertEqual(metrics, self.records)

    def test_get_metric_ratio_should_return_empty_list_when_fails(self):
        self.mock_session.execute.side_effect = Exception("error")

        metrics = self.repository.get_metric_ratio("CAV", "CAC", dict())

        self.assertEqual(metrics, [])
