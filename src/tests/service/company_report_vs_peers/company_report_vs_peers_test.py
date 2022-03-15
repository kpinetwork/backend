from unittest import TestCase
import logging
from unittest.mock import Mock
from src.service.company_report_vs_peers.company_report_vs_peers_service import (
    CompanyReportvsPeersService,
)
from src.utils.company_anonymization import CompanyAnonymization

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestCompanyReportvsPeers(TestCase):
    def setUp(self):
        self.size_cohort = {"size_cohort": "size_cohort_1", "count": 1}
        self.scenarios = [
            {"scenario": "Test 1", "metric": "Revenue", "alias": "growth"},
            {"scenario": "Test 2", "metric": "Revenue", "alias": "margin"},
        ]
        self.company = {
            "name": "MAMSoft",
            "id": "dfdf7feb-rf9e-4f6e-9504-f24f205fe60a",
            "sector": "Application Software",
            "vertical": "Life Sciences",
            "inves_profile_name": "Early stage VC",
            "size_cohort": "$30-<$50 million",
            "margin_group": "Low",
        }
        self.metric_value = {"annual_ebitda": "15"}
        self.mock_session = Mock()
        self.mock_query_builder = Mock()
        self.mock_response_sql = Mock()
        self.company_anonymization = CompanyAnonymization(object)
        self.overview_service_instance = CompanyReportvsPeersService(
            self.mock_session,
            self.mock_query_builder,
            logger,
            self.mock_response_sql,
            self.company_anonymization,
        )
        return

    def mock_response_query_sql(self, response):
        attrs = {"process_query_result.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def mock_response_list_query_sql(self, response):
        attrs = {"process_query_list_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def mock_response_rule_of_40_chart_query_sql(self, response):
        attrs = {"process_rule_of_40_chart_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def mock_response_metrics_group_by_size_cohort_results(self, response):
        attrs = {"process_metrics_group_by_size_cohort_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def test_get_company_description_with_access_success(self):
        self.mock_response_query_sql(self.company)

        get_description = self.overview_service_instance.get_description("1", True)

        self.assertEqual(get_description, self.company)
        self.overview_service_instance.session.execute.assert_called_once()

    def test_get_company_description_without_access_success_with_anonymized_data(self):
        self.mock_response_query_sql(self.company)
        data = self.company.copy()
        data["name"] = "{id}-xxxx".format(id=data["id"][0:4])

        get_description = self.overview_service_instance.get_description("1", False)

        self.assertEqual(get_description, data)
        self.overview_service_instance.session.execute.assert_called_once()

    def test_get_company_description_failed(self):
        self.overview_service_instance.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.overview_service_instance.get_description("1", True)
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.overview_service_instance.session.execute.assert_called_once()

    def test_get_metric_by_scenario_with_valid_metric_and_scenario(self):
        self.mock_response_query_sql([self.metric_value])

        get_metric_by_scenario_out = (
            self.overview_service_instance.get_metric_by_scenario(
                "1",
                "Actuals",
                "Revenue",
                "growth",
            )
        )

        self.assertEqual(get_metric_by_scenario_out, [self.metric_value])
        self.overview_service_instance.session.execute.assert_called_once()

    def test_get_metric_by_scenario_with_empty_response(self):
        self.mock_response_query_sql([])

        get_metric_by_scenario_out = (
            self.overview_service_instance.get_metric_by_scenario(
                "1",
                "Actuals",
                "Revenue",
                "growth",
            )
        )

        self.assertEqual(get_metric_by_scenario_out, [])
        self.overview_service_instance.session.execute.assert_called_once()

    def test_get_metric_by_scenario_failed(self):
        self.overview_service_instance.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.overview_service_instance.get_metric_by_scenario(
                    "1",
                    "Actuals",
                    "Revenue",
                    "growth",
                )
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.overview_service_instance.session.execute.assert_called_once()

    def test_get_company_financial_profile_success(self):
        expected_out = {"revenue": "100"}
        self.mock_response_query_sql(expected_out)

        get_company_financial_profile_out = (
            self.overview_service_instance.get_company_financial_profile("1", "2020")
        )

        self.assertEqual(get_company_financial_profile_out, expected_out)
        self.assertEqual(self.overview_service_instance.session.execute.call_count, 6)

    def test_get_company_financial_profile_failed(self):
        self.overview_service_instance.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.overview_service_instance.get_company_financial_profile(
                    "1", "2020"
                )
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.assertEqual(
                self.overview_service_instance.session.execute.call_count, 6
            )

    def test_get_rule_of_40_company_vs_peers_with_access_success(self):
        expected_out = [
            {
                "company_id": "d26dfba2-fdd8-40lc-ab88-82bfpfc4778a",
                "name": "MAMSoft",
                "revenue_growth_rate": "129",
                "ebitda_margin": "-15",
                "revenue": "60",
            }
        ]
        expected_out = []
        self.mock_response_rule_of_40_chart_query_sql(expected_out)

        get_rule_of_40_out = self.overview_service_instance.get_rule_of_40(
            ["Sector"], ["Vertical"], ["Investor"], ["Growth"], ["Size"], "2020", True
        )

        self.assertEqual(get_rule_of_40_out, expected_out)
        self.overview_service_instance.session.execute.assert_called_once()

    def test_get_rule_of_40_company_vs_peers_without_access_success_should_return_anonymized_data(
        self,
    ):
        expected_out = [
            {
                "company_id": "d26dfba2-fdd8-40lc-ab88-82bfpfc4778a",
                "name": "MAMSoft",
                "revenue_growth_rate": "129",
                "ebitda_margin": "-15",
                "revenue": "60",
            }
        ]
        expected_out = []
        self.mock_response_rule_of_40_chart_query_sql(expected_out)

        get_rule_of_40_out = self.overview_service_instance.get_rule_of_40(
            ["Sector"], ["Vertical"], ["Investor"], ["Growth"], ["Size"], "2020", False
        )

        self.assertEqual(get_rule_of_40_out, expected_out)
        self.overview_service_instance.session.execute.assert_called_once()

    def test_get_rule_of_40_success_with_empty_response(self):
        self.mock_response_rule_of_40_chart_query_sql([])

        get_rule_of_40_out = self.overview_service_instance.get_rule_of_40(
            ["Sector"], ["Vertical"], ["Investor"], ["Growth"], ["Size"], "2020", True
        )

        self.assertEqual(get_rule_of_40_out, [])
        self.overview_service_instance.session.execute.assert_called_once()

    def test_get_rule_of_40_failed(self):
        self.overview_service_instance.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.overview_service_instance.get_rule_of_40(
                    ["Sector"],
                    ["Vertical"],
                    ["Investor"],
                    ["Growth"],
                    ["Size"],
                    "2020",
                    True,
                )
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.overview_service_instance.session.execute.assert_called_once()

    def test_get_company_report_vs_peers_success(self):
        record = self.size_cohort.copy()
        record["margin"] = record.pop("count")
        expected_out = {"revenue": "100"}
        self.mock_response_query_sql(expected_out)
        self.mock_response_list_query_sql([self.size_cohort, record])
        self.mock_response_rule_of_40_chart_query_sql([self.size_cohort, record])

        get_company_report_vs_peers_out = (
            self.overview_service_instance.get_company_report_vs_peers(
                "1",
                ["Semiconductors"],
                ["Transportation"],
                ["Investor"],
                ["Growth"],
                ["Size", "Size2"],
                "2020",
                True,
            )
        )

        expected_out = {
            "description": expected_out,
            "financial_profile": expected_out,
            "rule_of_40": [self.size_cohort, record],
        }

        self.assertEqual(get_company_report_vs_peers_out, expected_out)
        self.overview_service_instance.session.execute.assert_called()
        self.assertEqual(self.overview_service_instance.session.execute.call_count, 8)

    def test_get_company_report_vs_peers_with_empty_response(self):
        self.mock_response_list_query_sql([])
        self.mock_response_query_sql(dict())
        self.mock_response_rule_of_40_chart_query_sql([])

        get_company_report_vs_peers_out = (
            self.overview_service_instance.get_company_report_vs_peers(
                "1",
                ["Semiconductors"],
                ["Transportation"],
                ["Investor"],
                ["Growth"],
                ["Size", "Size2"],
                "2020",
                True,
            )
        )

        expected_out = dict()

        self.assertEqual(get_company_report_vs_peers_out, expected_out)
        self.overview_service_instance.session.execute.assert_called()
        self.assertEqual(self.overview_service_instance.session.execute.call_count, 1)

    def test_get_get_company_report_vs_peers_failed(self):
        self.overview_service_instance.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.overview_service_instance.get_company_report_vs_peers(
                    "1",
                    ["Semiconductors"],
                    ["Transportation"],
                    ["Investor"],
                    ["Growth"],
                    ["Size", "Size2"],
                    "2020",
                    True,
                )
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.overview_service_instance.session.execute.assert_called_once()
