from unittest import TestCase
import logging
from unittest.mock import Mock, patch
from parameterized import parameterized
from src.service.by_metric_report.metric_report_repository import MetricReportRepository

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
            {
                "id": "1",
                "name": "Test",
                "year": 2020,
                "value": 20,
                "period": "Full-year",
                "count_periods": 1,
            },
            {
                "id": "2",
                "name": "Company",
                "year": 2021,
                "value": 13,
                "period": "Full-year",
                "count_periods": 1,
            },
        ]

    def mock_response_list_query_sql(self, response):
        attrs = {"process_query_list_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def test_add_filters_with_data_should_return_dict_with_valid_sql_values(
        self,
    ):
        condition_name, condition_value = (
            "company.inves_profile_name",
            "Family office",
        )
        expected_out = {condition_name: [f"'{condition_value}'"]}
        conditions = {condition_name: [condition_value]}

        filters_out = self.repository.add_filters(**conditions)

        self.assertEqual(filters_out, expected_out)

    def test_get_years_should_return_valid_year_dict_list_when_successful_db_call(self):
        expected_years = [2020, 2021, 2022]
        self.mock_response_list_query_sql(
            [{"year": 2020}, {"year": 2021}, {"year": 2022}]
        )

        years = self.repository.get_years()

        self.assertEqual(years, expected_years)

    def test_get_years_should_return_empty_list_when_db_call_fails(self):
        self.mock_session.execute.side_effect = Exception("error")

        years = self.repository.get_years()

        self.assertEqual(years, [])

    def test___add_period_name_where_condition_should_return_query_with_period_condition(
        self,
    ):
        base_query = """query AND (time_period.period_name = 'Full-year'
        OR time_period.period_name IN ('Q1', 'Q2', 'Q3', 'Q4'))GROUP BY"""
        expected_query = "".join(base_query.split())

        new_query = (
            self.repository._MetricReportRepository__add_period_name_where_condition(
                "query GROUP BY"
            )
        )
        query_response = "".join(new_query.split())

        self.assertEqual(expected_query, query_response)

    def test__add_having_condition_should_return_query_with_having_condition(self):
        base_query = (
            "query HAVING (COUNT(full_year.period) = 1 AND "
            "full_year.period = 'Full-year') OR "
            "(COUNT(full_year.period) = 4 AND "
            "full_year.period='Quarters') LIMIT 1"
        )
        expected_query = "".join(base_query.split())

        new_query = self.repository._MetricReportRepository__add_having_condition(
            "query"
        )
        query_response = "".join(new_query.split())

        self.assertEqual(expected_query, query_response)

    def test__add_having_condition_for_main_metric_should_return_query_with_having_condition(
        self,
    ):
        base_query = (
            "query HAVING (COUNT(first_full_year.period) = 1 AND "
            "first_full_year.period = 'Full-year') OR "
            "(COUNT(first_full_year.period) = 4 AND "
            "first_full_year.period='Quarters')"
        )
        expected_query = "".join(base_query.split())

        new_query = self.repository._MetricReportRepository__add_having_condition_for_main_metric(
            "query"
        )
        query_response = "".join(new_query.split())

        self.assertEqual(expected_query, query_response)

    @patch.object(
        MetricReportRepository,
        "_MetricReportRepository__add_period_name_where_condition",
    )
    def test_get_base_metric_should_return_base_metrics_list_when_successful_call(
        self, mock_add_period_where_condition
    ):
        mock_add_period_where_condition.return_value = "Mock query"
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_base_metric("Revenue", "Actuals", dict())

        self.assertEqual(metrics, self.records)

    @patch.object(
        MetricReportRepository,
        "_MetricReportRepository__add_period_name_where_condition",
    )
    def test_get_base_metric_should_raise_an_exception_when_call_fails(
        self, mock_add_period_where_condition
    ):
        mock_add_period_where_condition.return_value = "Mock period condition"
        self.mock_session.execute.side_effect = Exception("error")

        with self.assertRaises(Exception) as context:
            self.repository.get_base_metric("Revenue", "Actuals", dict())

        self.assertEqual(str(context.exception), "error")

    @patch.object(
        MetricReportRepository,
        "_MetricReportRepository__add_period_name_where_condition",
    )
    @patch.object(
        MetricReportRepository,
        "_MetricReportRepository__add_having_condition_for_main_metric",
    )
    def test_get__no_base_metric_should_raise_an_exception_when_call_fails(
        self,
        mock_add_period_where_condition,
        mock_add_having_condition_for_main_metric,
    ):
        mock_add_period_where_condition.return_value = "Mock period condition"
        mock_add_having_condition_for_main_metric.return_value = "Mock having condition"
        self.mock_session.execute.side_effect = Exception("error")

        with self.assertRaises(Exception) as context:
            self.repository._MetricReportRepository__get_no_base_metrics(
                dict(), [], "Actuals"
            )

        self.assertEqual(str(context.exception), "error")

    @patch.object(
        MetricReportRepository, "_MetricReportRepository__add_having_condition"
    )
    @patch.object(
        MetricReportRepository,
        "_MetricReportRepository__add_period_name_where_condition",
    )
    @patch.object(
        MetricReportRepository,
        "_MetricReportRepository__get_calculated_submetric_subquery",
    )
    @patch.object(
        MetricReportRepository,
        "_MetricReportRepository__add_having_condition_for_main_metric",
    )
    def test_get_actuals_vs_budget_should_return_metric_dict_list_when_successful_call(
        self,
        mock_add_having_condition,
        mock_add_period_where_condition,
        mock_get_calculated_submetric_subquery,
        mock_add_having_condition_for_main_metric,
    ):
        mock_add_having_condition.return_value = "Mock subquery"
        mock_get_calculated_submetric_subquery.return_value = "Mock subquery"
        mock_add_period_where_condition.return_value = "Mock having condition"
        mock_add_having_condition_for_main_metric.return_value = "Mock having condition"
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_actuals_vs_budget_metric("Ebitda", dict())

        self.assertEqual(metrics, self.records)

    def test_get_actuals_vs_budget_metric_should_return_empty_list_when_exception_raised(
        self,
    ):
        self.mock_session.execute.side_effect = Exception("error")

        metrics = self.repository.get_actuals_vs_budget_metric("Ebitda", dict())

        self.assertEqual(metrics, [])

    @patch.object(
        MetricReportRepository, "_MetricReportRepository__add_having_condition"
    )
    @patch.object(
        MetricReportRepository,
        "_MetricReportRepository__add_period_name_where_condition",
    )
    @patch.object(
        MetricReportRepository,
        "_MetricReportRepository__add_having_condition_for_main_metric",
    )
    def test_get_ebitda_margin_should_return_metric_dict_list_when_successful_call(
        self,
        mock_add_having_condition,
        mock_add_period_where_condition,
        mock_add_having_condition_for_main_metric,
    ):
        mock_add_having_condition.return_value = "Mock subquery"
        mock_add_period_where_condition.return_value = "Mock having condition"
        mock_add_having_condition_for_main_metric.return_value = "Mock having condition"
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_ebitda_margin_metric(dict())

        self.assertEqual(metrics, self.records)

    def test_get_ebitda_margin_should_return_empty_list_when_exception_raised(self):
        self.mock_session.execute.side_effect = Exception("error")

        metrics = self.repository.get_ebitda_margin_metric(dict())

        self.assertEqual(metrics, [])

    def test_get_most_recent_revenue_should_return_dict_list_when_successful_call(self):
        expected_metrics = [
            {"id": "1", "name": "Actuals-2021", "value": 30},
            {"id": "1", "name": "Actuals-2020", "value": 20},
        ]
        self.mock_response_list_query_sql(expected_metrics)

        metrics = self.repository.get_most_recents_revenue(dict())

        self.assertEqual(metrics, expected_metrics)

    def test_get_most_recent_revenue_should_return_empty_list_when_exception_raised(
        self,
    ):
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
    def test_get_arguments_should_return_dynamic_args_with_different_input(
        self, metric, scenario, expected_arguments
    ):

        arguments = self.repository._MetricReportRepository__get_arguments(
            {}, metric, scenario
        )

        self.assertEqual(arguments, expected_arguments)

    @patch.object(
        MetricReportRepository,
        "_MetricReportRepository__add_period_name_where_condition",
    )
    def test_get_metric_records_should_call_function(
        self, mock_add_period_where_condition
    ):
        mock_add_period_where_condition.return_value = "Where condition mock"
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_metric_records("actuals_ebitda", dict())

        self.assertEqual(metrics, self.records)

    def test_get_metric_records_shoudl_fail_with_invalid_metric(self):
        with self.assertRaises(Exception) as context:
            self.repository.get_metric_records("invalid", dict())

        self.assertEqual(str(context.exception), "Metric not found")

    @patch.object(
        MetricReportRepository, "_MetricReportRepository__add_having_condition"
    )
    @patch.object(
        MetricReportRepository,
        "_MetricReportRepository__add_period_name_where_condition",
    )
    @patch.object(
        MetricReportRepository,
        "_MetricReportRepository__get_calculated_submetric_subquery",
    )
    @patch.object(
        MetricReportRepository,
        "_MetricReportRepository__add_having_condition_for_main_metric",
    )
    def test_get_gross_profit_should_return_list_on_success(
        self,
        mock_add_having_condition,
        mock_add_period_condition,
        mock_get_calculated_submetric,
        mock_add_having_condition_for_main_metrics,
    ):
        mock_add_having_condition.return_value = "Mock having condition"
        mock_add_period_condition.return_value = "Mock period condition"
        mock_get_calculated_submetric.return_value = "Mock subquery"
        mock_add_having_condition_for_main_metrics.return_value = (
            "Mock having condition"
        )
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_gross_profit(dict())

        self.assertEqual(metrics, self.records)

    def test_get_gross_profit_should_return_empty_list_when_fails(self):
        self.mock_session.execute.side_effect = Exception("error")

        metrics = self.repository.get_gross_profit(dict())

        self.assertEqual(metrics, [])

    @patch.object(
        MetricReportRepository, "_MetricReportRepository__add_having_condition"
    )
    @patch.object(
        MetricReportRepository,
        "_MetricReportRepository__add_period_name_where_condition",
    )
    @patch.object(
        MetricReportRepository,
        "_MetricReportRepository__get_calculated_submetric_subquery",
    )
    @patch.object(
        MetricReportRepository,
        "_MetricReportRepository__add_having_condition_for_main_metric",
    )
    def test_get_gross_margin_should_return_list_on_success(
        self,
        mock_add_having_condition,
        mock_add_period_condition,
        mock_get_calculated_submetric,
        mock_add_having_condition_for_main_metrics,
    ):
        mock_add_having_condition.return_value = "Mock having condition"
        mock_add_period_condition.return_value = "Mock period condition"
        mock_get_calculated_submetric.return_value = "Mock subquery"
        mock_add_having_condition_for_main_metrics.return_value = (
            "Mock having condition"
        )
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_gross_margin(dict())

        self.assertEqual(metrics, self.records)

    def test_get_gross_margin_should_return_empty_list_when_fails(self):
        self.mock_session.execute.side_effect = Exception("error")

        metrics = self.repository.get_gross_margin(dict())

        self.assertEqual(metrics, [])

    @patch.object(
        MetricReportRepository, "_MetricReportRepository__add_having_condition"
    )
    @patch.object(
        MetricReportRepository,
        "_MetricReportRepository__add_period_name_where_condition",
    )
    @patch.object(
        MetricReportRepository,
        "_MetricReportRepository__get_calculated_submetric_subquery",
    )
    @patch.object(
        MetricReportRepository,
        "_MetricReportRepository__add_having_condition_for_main_metric",
    )
    def test_get_revenue_per_employee_return_list_on_success(
        self,
        mock_add_having_condition,
        mock_add_period_condition,
        mock_get_calculated_submetric,
        mock_add_having_condition_for_main_metrics,
    ):
        mock_add_having_condition.return_value = "Mock having condition"
        mock_add_period_condition.return_value = "Mock period condition"
        mock_get_calculated_submetric.return_value = "Mock subquery"
        mock_add_having_condition_for_main_metrics.return_value = (
            "Mock having condition"
        )
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_revenue_per_employee(dict())

        self.assertEqual(metrics, self.records)

    def test_get_revenue_per_employee_should_return_empty_list_when_fails(self):
        self.mock_session.execute.side_effect = Exception("error")

        metrics = self.repository.get_revenue_per_employee(dict())

        self.assertEqual(metrics, [])

    @patch.object(
        MetricReportRepository, "_MetricReportRepository__add_having_condition"
    )
    @patch.object(
        MetricReportRepository,
        "_MetricReportRepository__add_period_name_where_condition",
    )
    @patch.object(
        MetricReportRepository,
        "_MetricReportRepository__get_calculated_submetric_subquery",
    )
    @patch.object(
        MetricReportRepository,
        "_MetricReportRepository__add_having_condition_for_main_metric",
    )
    def test_get_opex_as_revenue_return_list_on_success(
        self,
        mock_add_having_condition,
        mock_add_period_condition,
        mock_get_calculated_submetric,
        mock_add_having_condition_for_main_metrics,
    ):
        mock_add_having_condition.return_value = "Mock having condition"
        mock_add_period_condition.return_value = "Mock period condition"
        mock_get_calculated_submetric.return_value = "Mock subquery"
        mock_add_having_condition_for_main_metrics.return_value = (
            "Mock having condition"
        )
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_opex_as_revenue(dict())

        self.assertEqual(metrics, self.records)

    def test_get_opex_as_revenue_should_return_empty_list_when_fails(self):
        self.mock_session.execute.side_effect = Exception("error")

        metrics = self.repository.get_opex_as_revenue(dict())

        self.assertEqual(metrics, [])

    @patch.object(
        MetricReportRepository, "_MetricReportRepository__add_having_condition"
    )
    @patch.object(
        MetricReportRepository,
        "_MetricReportRepository__add_period_name_where_condition",
    )
    @patch.object(
        MetricReportRepository,
        "_MetricReportRepository__get_calculated_submetric_subquery",
    )
    @patch.object(
        MetricReportRepository,
        "_MetricReportRepository__add_having_condition_for_main_metric",
    )
    def test_get_debt_ebitda_return_list_on_success(
        self,
        mock_add_having_condition,
        mock_add_period_condition,
        mock_get_calculated_submetric,
        mock_add_having_condition_for_main_metrics,
    ):
        mock_add_having_condition.return_value = "Mock having condition"
        mock_add_period_condition.return_value = "Mock period condition"
        mock_get_calculated_submetric.return_value = "Mock subquery"
        mock_add_having_condition_for_main_metrics.return_value = (
            "Mock having condition"
        )
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_debt_ebitda(dict())

        self.assertEqual(metrics, self.records)

    def test_get_debt_ebitda_should_return_empty_list_when_fails(self):
        self.mock_session.execute.side_effect = Exception("error")

        metrics = self.repository.get_debt_ebitda(dict())

        self.assertEqual(metrics, [])

    @patch.object(
        MetricReportRepository, "_MetricReportRepository__add_having_condition"
    )
    @patch.object(
        MetricReportRepository,
        "_MetricReportRepository__add_period_name_where_condition",
    )
    @patch.object(
        MetricReportRepository,
        "_MetricReportRepository__get_calculated_submetric_subquery",
    )
    @patch.object(
        MetricReportRepository,
        "_MetricReportRepository__add_having_condition_for_main_metric",
    )
    def test_get_gross_retention_return_list_on_success(
        self,
        mock_add_having_condition,
        mock_add_period_condition,
        mock_get_calculated_submetric,
        mock_add_having_condition_for_main_metrics,
    ):
        mock_add_having_condition.return_value = "Mock having condition"
        mock_add_period_condition.return_value = "Mock period condition"
        mock_get_calculated_submetric.return_value = "Mock subquery"
        mock_add_having_condition_for_main_metrics.return_value = (
            "Mock having condition"
        )
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_gross_retention(dict())

        self.assertEqual(metrics, self.records)

    def test_get_gross_retention_should_return_empty_list_when_fails(self):
        self.mock_session.execute.side_effect = Exception("error")

        metrics = self.repository.get_gross_retention(dict())

        self.assertEqual(metrics, [])

    @patch.object(
        MetricReportRepository, "_MetricReportRepository__add_having_condition"
    )
    @patch.object(
        MetricReportRepository,
        "_MetricReportRepository__add_period_name_where_condition",
    )
    @patch.object(
        MetricReportRepository,
        "_MetricReportRepository__get_calculated_submetric_subquery",
    )
    @patch.object(
        MetricReportRepository,
        "_MetricReportRepository__add_having_condition_for_main_metric",
    )
    def test_get_metric_ratio_return_list_on_success(
        self,
        mock_add_having_condition,
        mock_add_period_condition,
        mock_get_calculated_submetric,
        mock_add_having_condition_for_main_metrics,
    ):
        mock_add_having_condition.return_value = "Mock having condition"
        mock_add_period_condition.return_value = "Mock period condition"
        mock_get_calculated_submetric.return_value = "Mock subquery"
        mock_add_having_condition_for_main_metrics.return_value = (
            "Mock having condition"
        )
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_metric_ratio("CAV", "CAC", dict())

        self.assertEqual(metrics, self.records)

    def test_get_metric_ratio_should_return_empty_list_when_fails(self):
        self.mock_session.execute.side_effect = Exception("error")

        metrics = self.repository.get_metric_ratio("CAV", "CAC", dict())

        self.assertEqual(metrics, [])
