from unittest import TestCase
import logging
from unittest.mock import Mock
from src.service.comparison_vs_peers.comparison_vs_peers import (
    ComparisonvsPeersService,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestComparisonvsPeers(TestCase):
    def setUp(self):
        self.scenarios = [
            {"scenario": "Test 1", "metric": "Revenue", "alias": "growth"},
            {"scenario": "Test 2", "metric": "Revenue", "alias": "margin"},
        ]
        self.metric_value = {"growth": 15}
        self.company = {
            "id": "id",
            "name": "Company",
            "sector": "Science",
            "vertical": "Maths",
            "size_cohort": "100+",
        }
        self.comparison = {
            "id": "id",
            "name": "Test",
            "sector": "Science",
            "vertical": "Maths",
            "size_cohort": "100+",
            "growth": 17,
        }
        self.mock_session = Mock()
        self.mock_query_builder = Mock()
        self.mock_response_sql = Mock()
        self.comparison_service_instance = ComparisonvsPeersService(
            self.mock_session, self.mock_query_builder, logger, self.mock_response_sql
        )
        return

    def mock_response_query_sql(self, response):
        attrs = {"process_query_result.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def mock_response_list_query_sql(self, response):
        attrs = {"process_query_list_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def test_get_most_recent_metric_by_scenario_with_valid_metric_and_scenario(self):
        self.mock_response_query_sql(self.metric_value)

        get_most_recent_metric_by_scenario_out = (
            self.comparison_service_instance.get_most_recent_metric_by_scenario(
                "1",
                "Actuals",
                "Revenue",
                "growth",
            )
        )

        self.assertEqual(get_most_recent_metric_by_scenario_out, self.metric_value)
        self.comparison_service_instance.session.execute.assert_called_once()

    def test_get_most_recent_metric_by_scenario_with_empty_response(self):
        self.mock_response_query_sql(dict())

        get_most_recent_metric_by_scenario_out = (
            self.comparison_service_instance.get_most_recent_metric_by_scenario(
                "1",
                "Actuals",
                "Revenue",
                "growth",
            )
        )

        self.assertEqual(get_most_recent_metric_by_scenario_out, dict())
        self.comparison_service_instance.session.execute.assert_called_once()

    def test_get_most_recent_metric_by_scenario_failed(self):
        self.comparison_service_instance.session.execute.side_effect = Exception(
            "error"
        )
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.comparison_service_instance.get_most_recent_metric_by_scenario(
                    "1",
                    "Actuals",
                    "Revenue",
                    "growth",
                )
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.comparison_service_instance.session.execute.assert_called_once()

    def test_get_company_comparison_data_success(self):
        self.mock_response_list_query_sql([self.metric_value])
        self.mock_response_query_sql(self.metric_value)

        get_company_comparison_data_out = (
            self.comparison_service_instance.get_company_comparison_data("id")
        )

        self.assertEqual(get_company_comparison_data_out, self.metric_value)
        self.assertEqual(self.comparison_service_instance.session.execute.call_count, 7)

    def test_get_company_comparison_data_with_empty_company_id(self):
        get_company_comparison_data_out = (
            self.comparison_service_instance.get_company_comparison_data("")
        )

        self.assertEqual(get_company_comparison_data_out, dict())
        self.comparison_service_instance.session.execute.assert_not_called()

    def test_get_company_comparison_data_failed(self):
        self.comparison_service_instance.session.execute.side_effect = Exception(
            "error"
        )
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.comparison_service_instance.get_company_comparison_data("id")
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.comparison_service_instance.session.execute.assert_called_once()

    def test_get_peers_with_full_data(self):
        self.mock_response_list_query_sql([self.company])

        get_peers_out = self.comparison_service_instance.get_peers(
            ["Science"], ["Maths"], ["Family office"], ["Negative"], ["100+"]
        )

        self.assertEqual(get_peers_out, [self.company])
        self.comparison_service_instance.session.execute.assert_called_once()

    def test_get_peers_with_empty_response(self):
        self.mock_response_list_query_sql([])

        get_peers_out = self.comparison_service_instance.get_peers(
            ["Science"], ["Maths"], ["Family office"], ["Negative"], ["100+"]
        )

        self.assertEqual(get_peers_out, [])
        self.comparison_service_instance.session.execute.assert_called_once()

    def test_get_peers_failed(self):
        self.comparison_service_instance.session.execute.side_effect = Exception(
            "error"
        )
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.comparison_service_instance.get_peers(
                    ["Science"], ["Maths"], ["Family office"], ["Negative"], ["100+"]
                )
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.comparison_service_instance.session.execute.assert_called_once()

    def test_get_peers_comparison_data_success(self):
        company_data = self.company.copy()
        company_data.update(self.metric_value)
        self.mock_response_list_query_sql([company_data])
        self.mock_response_query_sql(self.metric_value)

        get_peers_comparison_data_out = (
            self.comparison_service_instance.get_peers_comparison_data(
                "id 2",
                ["Science"],
                ["Maths"],
                ["Family office"],
                ["Negative"],
                ["100+"],
            )
        )

        self.assertEqual(get_peers_comparison_data_out, [company_data])
        self.assertEqual(self.comparison_service_instance.session.execute.call_count, 7)

    def test_get_peers_comparison_data_failed(self):
        self.comparison_service_instance.session.execute.side_effect = Exception(
            "error"
        )
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.comparison_service_instance.get_peers_comparison_data(
                    "id",
                    ["Science"],
                    ["Maths"],
                    ["Family office"],
                    ["Negative"],
                    ["100+"],
                )
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.comparison_service_instance.session.execute.assert_called_once()

    def test_get_rank_success(self):
        company_data = self.company.copy()
        company_data.update(self.metric_value)
        expected_out = {"growth": "2 of 2"}

        get_rank_out = self.comparison_service_instance.get_rank(
            company_data, [self.comparison]
        )

        self.assertEqual(get_rank_out, expected_out)

    def test_get_rank_success_with_empty_company_data(self):
        get_rank_out = self.comparison_service_instance.get_rank(
            dict(), [self.comparison]
        )

        self.assertEqual(get_rank_out, dict())

    def test_get_rank_success_with_empty_peer_data(self):
        company_data = self.company.copy()
        company_data.update(self.metric_value)
        expected_out = {"growth": "1 of 1"}

        get_rank_out = self.comparison_service_instance.get_rank(company_data, [])

        self.assertEqual(get_rank_out, expected_out)

    def test_get_comparison_vs_peers_success(self):
        company_data = self.company.copy()
        company_data.update(self.metric_value)
        self.mock_response_list_query_sql([company_data])
        self.mock_response_query_sql(self.metric_value)

        expected_out = {
            "company_comparison_data": self.metric_value,
            "rank": {"growth": "2 of 2"},
            "peers_comparison_data": [company_data],
        }

        get_comparison_vs_peers__out = (
            self.comparison_service_instance.get_comparison_vs_peers(
                "id",
                ["Science"],
                ["Maths"],
                ["Family office"],
                ["Negative"],
                ["100+"],
                "2021",
            )
        )

        self.assertEqual(get_comparison_vs_peers__out, expected_out)
        self.assertEqual(self.comparison_service_instance.session.execute.call_count, 8)

    def test_get_comparison_vs_peers_failed(self):
        self.comparison_service_instance.session.execute.side_effect = Exception(
            "error"
        )
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.comparison_service_instance.get_comparison_vs_peers(
                    "id",
                    ["Science"],
                    ["Maths"],
                    ["Family office"],
                    ["Negative"],
                    ["100+"],
                    "2021",
                )
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.comparison_service_instance.session.execute.assert_called_once()
