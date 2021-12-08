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
        self.scenarios = [
            {"scenario": "Test 1", "metric": "Revenue", "alias": "growth"},
            {"scenario": "Test 2", "metric": "Revenue", "alias": "margin"},
        ]
        self.metric_avg = {"revenue": "100"}
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

    def test_get_metric_avg_by_scenario_with_valid_metric_and_scenario(self):
        self.mock_response_query_sql([self.metric_avg])

        get_metric_avg_by_scenario_out = (
            self.overview_service_instance.get_metric_avg_by_scenario(
                "Budget", "Revenue", "2020", "Sector", "Vertical", "growth"
            )
        )

        self.assertEqual(get_metric_avg_by_scenario_out, [self.metric_avg])
        self.overview_service_instance.session.execute.assert_called_once()

    def test_get_metric_avg_by_scenario_with_empty_response(self):
        self.mock_response_query_sql([])

        get_metric_avg_by_scenario_out = (
            self.overview_service_instance.get_metric_avg_by_scenario(
                "Budget", "Revenue", "2020", "Maths", "Science", "growth"
            )
        )

        self.assertEqual(get_metric_avg_by_scenario_out, [])
        self.overview_service_instance.session.execute.assert_called_once()

    def test_get_metric_avg_by_scenario_failed(self):
        self.overview_service_instance.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.overview_service_instance.get_metric_avg_by_scenario(
                    "Budget", "Revenue", "2020", "Maths", "Science", "growth"
                )
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.overview_service_instance.session.execute.assert_called_once()

    def test_get_companies_kpi_average_with_all_arguments_success(self):
        expected_out = [{"revenue": "100"}]
        self.mock_response_list_query_sql(expected_out)

        get_companies_kpi_average_out = (
            self.overview_service_instance.get_companies_kpi_average(
                "2021", "Semiconductors", "Transportation"
            )
        )

        self.assertEqual(get_companies_kpi_average_out, expected_out)
        self.assertEqual(self.overview_service_instance.session.execute.call_count, 3)

    def test_get_companies_kpi_average_failed(self):
        self.overview_service_instance.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.overview_service_instance.get_companies_kpi_average(
                    "2021", "Semiconductors", "Transportation"
                )
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.assertEqual(
                self.overview_service_instance.session.execute.call_count, 3
            )

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

    def test_get_scenarios_pair_by_size_cohort_success(self):
        record = self.size_cohort.copy()
        record["margin"] = record.pop("count")
        expected_out = {record["size_cohort"]: [self.size_cohort, record]}
        self.mock_response_list_query_sql([self.size_cohort, record])
        self.mock_response_metrics_group_by_size_cohort_results(expected_out)

        get_scenarios_pair_by_size_cohort_out = (
            self.overview_service_instance.get_scenarios_pair_by_size_cohort(
                self.scenarios, "Sector", "Vertical", "2020"
            )
        )

        self.assertEqual(get_scenarios_pair_by_size_cohort_out, expected_out)
        self.overview_service_instance.session.execute.assert_called()
        self.assertEqual(self.overview_service_instance.session.execute.call_count, 2)

    def test_get_scenarios_pair_by_size_cohort_success_with_empty_response(self):
        self.mock_response_list_query_sql([])
        self.mock_response_metrics_group_by_size_cohort_results(dict())

        get_scenarios_pair_by_size_cohort_out = (
            self.overview_service_instance.get_scenarios_pair_by_size_cohort(
                self.scenarios, "Sector", "Vertical", "2020"
            )
        )

        self.assertEqual(get_scenarios_pair_by_size_cohort_out, dict())
        self.overview_service_instance.session.execute.assert_called()
        self.assertEqual(self.overview_service_instance.session.execute.call_count, 2)

    def test_get_scenarios_pair_by_size_cohort_failed(self):
        self.overview_service_instance.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.overview_service_instance.get_scenarios_pair_by_size_cohort(
                    self.scenarios, "Sector", "Vertical", "2020"
                )
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.overview_service_instance.session.execute.assert_called_once()

    def test_get_growth_and_margin_by_size_cohort_is_actual_success(self):
        record = self.size_cohort.copy()
        record["margin"] = record.pop("count")
        expected_out = {record["size_cohort"]: [self.size_cohort, record]}
        self.mock_response_list_query_sql([self.size_cohort, record])
        self.mock_response_metrics_group_by_size_cohort_results(expected_out)

        get_growth_and_margin_by_size_cohort_out = (
            self.overview_service_instance.get_growth_and_margin_by_size_cohort(
                "Sector", "Vertical", "2020"
            )
        )

        self.assertEqual(get_growth_and_margin_by_size_cohort_out, expected_out)
        self.overview_service_instance.session.execute.assert_called()
        self.assertEqual(self.overview_service_instance.session.execute.call_count, 2)

    def test_get_growth_and_margin_by_size_cohort_is_not_actual_success(self):
        record = self.size_cohort.copy()
        record["margin"] = record.pop("count")
        expected_out = {record["size_cohort"]: [self.size_cohort, record]}
        self.mock_response_list_query_sql([self.size_cohort, record])
        self.mock_response_metrics_group_by_size_cohort_results(expected_out)

        get_growth_and_margin_by_size_cohort_out = (
            self.overview_service_instance.get_growth_and_margin_by_size_cohort(
                "Sector", "Vertical", "2020", False
            )
        )

        self.assertEqual(get_growth_and_margin_by_size_cohort_out, expected_out)
        self.overview_service_instance.session.execute.assert_called()
        self.assertEqual(self.overview_service_instance.session.execute.call_count, 2)

    def test_get_growth_and_margin_by_size_cohort_failed(self):
        self.overview_service_instance.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.overview_service_instance.get_growth_and_margin_by_size_cohort(
                    "Sector", "Vertical", "2020"
                )
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.overview_service_instance.session.execute.assert_called_once()

    def test_get_revenue_and_ebitda_by_size_cohort_success(self):
        revenue = {"size_cohort": "size_cohort_1", "revenue": 1}
        record = revenue.copy()
        record["ebitda"] = record.pop("revenue")
        expected_out = {record["size_cohort"]: [revenue, record]}
        self.mock_response_list_query_sql([revenue, record])
        self.mock_response_metrics_group_by_size_cohort_results(expected_out)

        get_revenue_and_ebitda_by_size_cohort_out = (
            self.overview_service_instance.get_revenue_and_ebitda_by_size_cohort(
                "Sector", "Vertical", "2020"
            )
        )

        self.assertEqual(get_revenue_and_ebitda_by_size_cohort_out, expected_out)
        self.overview_service_instance.session.execute.assert_called()
        self.assertEqual(self.overview_service_instance.session.execute.call_count, 2)

    def test_get_revenue_and_ebitda_by_size_cohort_success_with_empty_response(self):
        self.mock_response_list_query_sql([])
        self.mock_response_metrics_group_by_size_cohort_results(dict())

        get_revenue_and_ebitda_by_size_cohort_out = (
            self.overview_service_instance.get_revenue_and_ebitda_by_size_cohort(
                "Sector", "Vertical", "2020"
            )
        )

        self.assertEqual(get_revenue_and_ebitda_by_size_cohort_out, dict())
        self.overview_service_instance.session.execute.assert_called()
        self.assertEqual(self.overview_service_instance.session.execute.call_count, 2)

    def test_get_revenue_and_ebitda_by_size_cohort_failed(self):
        self.overview_service_instance.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.overview_service_instance.get_revenue_and_ebitda_by_size_cohort(
                    "Sector", "Vertical", "2020"
                )
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.overview_service_instance.session.execute.assert_called_once()

    def test_get_rule_of_40_success(self):
        expected_out = []
        self.mock_response_list_query_sql(expected_out)

        get_rule_of_40_out = self.overview_service_instance.get_rule_of_40(
            "Test", "Test", "2020"
        )

        self.assertEqual(get_rule_of_40_out, expected_out)
        self.overview_service_instance.session.execute.assert_called_once()

    def test_get_rule_of_40_success_with_empty_response(self):
        self.mock_response_list_query_sql([])

        get_rule_of_40_out = self.overview_service_instance.get_rule_of_40(
            "", "", "2020"
        )

        self.assertEqual(get_rule_of_40_out, [])
        self.overview_service_instance.session.execute.assert_called_once()

    def test_get_rule_of_40_failed(self):
        self.overview_service_instance.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.overview_service_instance.get_rule_of_40("", "", "2020")
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.overview_service_instance.session.execute.assert_called_once()

    def test_get_universe_overview_success(self):
        record = self.size_cohort.copy()
        record["margin"] = record.pop("count")
        size_cohort_expected_out = {record["size_cohort"]: [self.size_cohort, record]}
        self.mock_response_list_query_sql([self.size_cohort, record])
        self.mock_response_metrics_group_by_size_cohort_results(
            size_cohort_expected_out
        )

        get_universe_overview_out = (
            self.overview_service_instance.get_universe_overview(
                "Sector", "Vertical", "2020"
            )
        )

        expected_out = {
            "kpi_average": [self.size_cohort, record],
            "count_by_size": [self.size_cohort, record],
            "growth_and_margin": size_cohort_expected_out,
            "expected_growth_and_margin": size_cohort_expected_out,
            "revenue_and_ebitda": size_cohort_expected_out,
            "rule_of_40": [self.size_cohort, record],
        }

        self.assertEqual(get_universe_overview_out, expected_out)
        self.overview_service_instance.session.execute.assert_called()
        self.assertEqual(self.overview_service_instance.session.execute.call_count, 11)

    def test_get_universe_overview_success_with_empty_response(self):
        self.mock_response_list_query_sql([])
        self.mock_response_metrics_group_by_size_cohort_results(dict())

        get_universe_overview_out = (
            self.overview_service_instance.get_universe_overview(
                "Sector", "Vertical", "2020"
            )
        )

        expected_out = {
            "kpi_average": [],
            "count_by_size": [],
            "growth_and_margin": dict(),
            "expected_growth_and_margin": dict(),
            "revenue_and_ebitda": dict(),
            "rule_of_40": [],
        }

        self.assertEqual(get_universe_overview_out, expected_out)
        self.overview_service_instance.session.execute.assert_called()
        self.assertEqual(self.overview_service_instance.session.execute.call_count, 11)

    def test_get_universe_overview_failed(self):
        self.overview_service_instance.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.overview_service_instance.get_universe_overview(
                    "Sector", "Vertical", "2020"
                )
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.overview_service_instance.session.execute.assert_called_once()
