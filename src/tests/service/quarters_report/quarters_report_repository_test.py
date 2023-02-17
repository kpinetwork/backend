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
            "year_year", "revenue", "Actuals", [2021, 2022], None, dict()
        )

        self.assertEqual(metrics, self.records)

    @patch.object(QuartersReportRepository, "get_base_query")
    def test_get_metric_by_quarters_with_year_to_date_should_call_function(
        self, mock_base_query
    ):
        mock_base_query.return_value = "Mock subquery"
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_metric_records_by_quarters(
            "year_to_date", "revenue", "Actuals", [2021, 2022], "Q2", dict()
        )

        self.assertEqual(metrics, self.records)

    def test_get_metric_by_quarters_should_fail_with_invalid_metric(self):
        with self.assertRaises(Exception) as context:
            self.repository.get_metric_records_by_quarters(
                "year_year", "invalid", "Actuals", [2021, 2022], None, dict()
            )

        self.assertEqual(str(context.exception), "Metric not found")

    def test_get_quarters_year_to_year_records_should_call_function(self):
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_quarters_year_to_year_records(
            "year_to_year", "ebitda_margin", "actuals", [2021, 2022], None, dict()
        )

        self.assertEqual(metrics, self.records)

    def test_get_quarters_year_to_year_records_should_fail_with_invalid_metric(self):
        with self.assertRaises(Exception) as context:
            self.repository.get_quarters_year_to_year_records(
                "year_to_year", "invalid", "actuals", [2021, 2022], None, dict()
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
            "revenue", [2021, 2022], dict(), "actuals_budget", "year_to_year", "Q3"
        )

        self.assertEqual(metrics, [])

    def test_get_actuals_plus_budget_metrics_query_when_sucess_should_return_records(
        self,
    ):
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_actuals_plus_budget_metrics_query(
            "revenue", [2021, 2022], dict(), "actuals_budget", "year_to_date", None
        )

        self.assertEqual(metrics, self.records)

    def test_get_metric_ratio_success_should_return_list(self):
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_metric_ratio([2021, 2021], "CAV", "CAC", dict())

        self.assertEqual(metrics, self.records)

    @patch.object(
        QuartersReportRepository,
        "_QuartersReportRepository__get_full_year_table__calculated_metrics",
    )
    def test_get_metric_ratio_success_with_scenario_should_return_list(
        self, mock_full_year_table
    ):
        mock_full_year_table.return_value = "Mock table"
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_metric_ratio(
            [2021, 2021], "CAV", "CAC", dict(), "Actuals"
        )

        self.assertEqual(metrics, self.records)

    def test_get_metric_ratio_should_return_empty_list_when_fails(self):
        self.mock_session.execute.side_effect = Exception("error")

        metrics = self.repository.get_metric_ratio([2021, 2021], "CAV", "CAC", dict())

        self.assertEqual(metrics, [])

    @patch.object(
        QuartersReportRepository,
        "_QuartersReportRepository__get_full_year_table__calculated_metrics",
    )
    def test_get_metric_as_percentage_of_revenue_success_with_scenario_should_return_list(
        self, mock_full_year_table
    ):
        mock_full_year_table.return_value = "Mock table"
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_metric_as_percentage_of_revenue(
            [2021, 2021], "Revenue", dict(), "Actuals"
        )

        self.assertEqual(metrics, self.records)

    def test_get_metric_as_percentage_of_revenue_should_return_empty_list_when_fails(
        self,
    ):
        self.mock_session.execute.side_effect = Exception("error")

        metrics = self.repository.get_metric_as_percentage_of_revenue(
            [2021, 2021], "Ebitda", dict()
        )

        self.assertEqual(metrics, [])

    def test_get_gross_retention_success_should_return_list(self):
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_gross_retention([2021, 2021], dict())

        self.assertEqual(metrics, self.records)

    @patch.object(
        QuartersReportRepository,
        "_QuartersReportRepository__get_full_year_table__calculated_metrics",
    )
    def test_get_gross_retention_success_with_scenario_should_return_list(
        self, mock_full_year_table
    ):
        mock_full_year_table.return_value = "Mock table"
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_gross_retention([2021, 2021], dict(), "Actuals")

        self.assertEqual(metrics, self.records)

    def test_get_gross_retention_should_return_empty_list_when_fails(self):
        self.mock_session.execute.side_effect = Exception("error")

        metrics = self.repository.get_gross_retention([2021, 2021], dict())

        self.assertEqual(metrics, [])

    def test_get_debt_ebitda_success_should_return_list(self):
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_debt_ebitda([2021, 2021], dict())

        self.assertEqual(metrics, self.records)

    @patch.object(
        QuartersReportRepository,
        "_QuartersReportRepository__get_full_year_table__calculated_metrics",
    )
    def test_get_debt_ebitda_success_with_scenario_should_return_list(
        self, mock_full_year_table
    ):
        mock_full_year_table.return_value = "Mock table"
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_debt_ebitda([2021, 2021], dict(), "Actuals")

        self.assertEqual(metrics, self.records)

    def test_get_debt_ebitda_should_return_empty_list_when_fails(self):
        self.mock_session.execute.side_effect = Exception("error")

        metrics = self.repository.get_debt_ebitda([2021, 2021], dict())

        self.assertEqual(metrics, [])

    def test_get_opex_as_revenue_actuals_budget_success_should_return_list(self):
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_opex_as_revenue(
            [2021, 2021], dict(), "actuals_budget", "year_to_year", None
        )

        self.assertEqual(metrics, self.records)

    @patch.object(
        QuartersReportRepository,
        "_QuartersReportRepository__get_full_year_table__calculated_metrics",
    )
    def test_get_opex_as_revenue_success_with_scenario_should_return_list(
        self, mock_full_year_table
    ):
        mock_full_year_table.return_value = "Mock table"
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_opex_as_revenue([2021, 2021], dict(), "Actuals")

        self.assertEqual(metrics, self.records)

    def test_get_opex_as_revenue_should_return_empty_list_when_fails(self):
        self.mock_session.execute.side_effect = Exception("error")

        metrics = self.repository.get_opex_as_revenue(
            [2021, 2021], dict(), "actuals_budget", "year_to_year", None
        )

        self.assertEqual(metrics, [])

    def test_get_revenue_per_employee_actuals_plus_budget_success_should_return_list(
        self,
    ):
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_revenue_per_employee(
            [2021, 2021], dict(), "actuals_budget", "year_to_year"
        )

        self.assertEqual(metrics, self.records)

    @patch.object(
        QuartersReportRepository,
        "_QuartersReportRepository__get_full_year_table__calculated_metrics",
    )
    def test_get_revenue_per_employee_success_with_scenario_should_return_list(
        self, mock_full_year_table
    ):
        mock_full_year_table.return_value = "Mock table"
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_revenue_per_employee(
            [2021, 2021], dict(), "Actuals"
        )

        self.assertEqual(metrics, self.records)

    def test_get_revenue_per_employee_should_return_empty_list_when_fails(self):
        self.mock_session.execute.side_effect = Exception("error")

        metrics = self.repository.get_revenue_per_employee([2021, 2021], dict())

        self.assertEqual(metrics, [])

    def test_get_gross_margin_success_should_return_list(self):
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_gross_margin([2021, 2021], dict())

        self.assertEqual(metrics, self.records)

    @patch.object(
        QuartersReportRepository,
        "_QuartersReportRepository__get_full_year_table__calculated_metrics",
    )
    def test_get_gross_margin_success_with_scenario_should_return_list(
        self, mock_full_year_table
    ):
        mock_full_year_table.return_value = "Mock table"
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_gross_margin([2021, 2021], dict(), "Actuals")

        self.assertEqual(metrics, self.records)

    def test_get_gross_margin_should_return_empty_list_when_fails(self):
        self.mock_session.execute.side_effect = Exception("error")

        metrics = self.repository.get_gross_margin([2021, 2021], dict())

        self.assertEqual(metrics, [])

    def test_get_actuals_vs_budget_metric_success_should_return_list(self):
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_actuals_vs_budget_metric(
            [2021, 2021], "Revenue", dict()
        )

        self.assertEqual(metrics, [])

    @patch.object(
        QuartersReportRepository,
        "_QuartersReportRepository__get_full_year_table__calculated_metrics",
    )
    def test_get_actuals_vs_budget_metric_success_with_scenario_should_return_list(
        self, mock_full_year_table
    ):
        mock_full_year_table.return_value = "Mock table"
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_actuals_vs_budget_metric(
            [2021, 2021], "Revenue", dict(), "Actuals"
        )

        self.assertEqual(metrics, self.records)

    def test_get_actuals_vs_budget_metric_should_return_empty_list_when_fails(self):
        self.mock_session.execute.side_effect = Exception("error")

        metrics = self.repository.get_actuals_vs_budget_metric(
            [2021, 2021], "Revenue", dict(), "Actuals"
        )

        self.assertEqual(metrics, [])

    @patch.object(
        QuartersReportRepository,
        "_QuartersReportRepository__get_full_year_table__calculated_metrics",
    )
    def test_get_gross_profit_success_with_scenario_should_return_list(
        self, mock_full_year_table
    ):
        mock_full_year_table.return_value = "Mock table"
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_gross_profit([2021, 2021], dict(), "Actuals")

        self.assertEqual(metrics, self.records)

    def test_get_gross_profit_success_should_return_list(self):
        self.mock_response_list_query_sql(self.records)

        metrics = self.repository.get_gross_profit([2021, 2021], dict())

        self.assertEqual(metrics, self.records)

    def test_get_gross_profit_should_return_empty_list_when_fails(self):
        self.mock_session.execute.side_effect = Exception("error")

        metrics = self.repository.get_gross_profit(
            [2021, 2021], dict(), "actuals_budget", "year_to_year", None
        )

        self.assertEqual(metrics, [])

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

    @patch.object(
        QuartersReportRepository,
        "_QuartersReportRepository__get_full_year_table_base_query",
    )
    @patch.object(
        QuartersReportRepository,
        "_QuartersReportRepository__get_full_year_avg_subquery",
    )
    def test__get_full_year_table_calculated_metrics(
        self, mock_full_year_base_query, mock_full_year_subquery
    ):
        mock_full_year_base_query.return_value = "Mock query"
        mock_full_year_subquery.return_value = "Mock query"

        query = self.repository._QuartersReportRepository__get_full_year_table__calculated_metrics(
            [], ""
        )

        self.assertEqual(query, "Mock query")

    @patch.object(
        QuartersReportRepository,
        "_QuartersReportRepository__get_base_table_for_calculated_metrics",
    )
    @patch.object(
        QuartersReportRepository,
        "_QuartersReportRepository__get_full_year_average_base_query",
    )
    def test__get_full_year_average_subquery_calculated_metrics(
        self, mock_base_table_query, mock_full_year_subquery
    ):
        mock_base_table_query.return_value = "Query "
        mock_full_year_subquery.return_value = "Mock query"
        expected_response = "Query  HAVING count(sum_quarters.period_name ) = 4 "

        query = self.repository._QuartersReportRepository__get_full_year_avg_subquery(
            [], ""
        )

        self.assertEqual(query, expected_response)

    def test_get_calculated_metrics_with_base_scenarios_return_empty_list_when_fails(
        self,
    ):
        self.mock_session.execute.side_effect = Exception("error")

        metrics = self.repository.get_calculated_metrics_with_base_scenarios(
            "Select vale", "Actuals", "Revenue", [2020], dict()
        )

        self.assertEqual(metrics, [])

    def test__get_full_year_table_base_query(self):
        self.repository._QuartersReportRepository__get_full_year_table_base_query(
            "", [], []
        )

        self.mock_query_builder.assert_not_called()

    def test_get_actuals_plus_main_table_subquery(self):
        self.repository.get_actuals_plus_main_table_subquery(
            "Revenue",
            [2021],
            dict(),
            "year_to_date",
            "Q2",
        )
        self.mock_query_builder.assert_not_called()
