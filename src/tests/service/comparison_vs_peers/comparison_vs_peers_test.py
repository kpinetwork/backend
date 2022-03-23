from unittest import TestCase
import logging
from unittest.mock import Mock
from src.service.comparison_vs_peers.comparison_vs_peers_service import (
    ComparisonvsPeersService,
)
from src.utils.company_anonymization import CompanyAnonymization
from src.utils.profile_range import ProfileRange

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
            "id": "1",
            "name": "Company",
            "sector": "Science",
            "vertical": "Maths",
            "size_cohort": "100+",
            "growth": 17,
            "revenue": 120,
        }
        self.comparison = {
            "id": "2",
            "name": "Test",
            "sector": "Science",
            "vertical": "Maths",
            "size_cohort": "100+",
            "growth": 34,
            "revenue": 110,
        }
        self.mock_session = Mock()
        self.mock_query_builder = Mock()
        self.mock_response_sql = Mock()
        self.company_anonymization = CompanyAnonymization(object)
        self.profile_range = ProfileRange(
            self.mock_session, self.mock_query_builder, logger, self.mock_response_sql
        )
        self.profile_range.ranges = [
            {"label": "100+", "max_value": None, "min_value": 100}
        ]
        self.comparison_service_instance = ComparisonvsPeersService(
            self.mock_session,
            self.mock_query_builder,
            logger,
            self.mock_response_sql,
            self.company_anonymization,
            self.profile_range,
        )
        return

    def mock_response_query_sql(self, response):
        attrs = {"process_query_result.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def mock_response_list_query_sql(self, response):
        attrs = {"process_query_list_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def mock_proccess_comparison_results(self, response):
        attrs = {"proccess_comparison_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def test_add_company_filters_with_data(self):
        expected_out = {"company.sector": ["'Application'"]}

        filters_out = self.comparison_service_instance.add_company_filters(
            sector=["Application"]
        )

        self.assertEqual(filters_out, expected_out)

    def test_remove_revenue_without_permissions(self):
        self.company_anonymization.companies = ["2"]
        data = {"id": "1", "size_cohort": "100+", "revenue": 102}
        expected_out = {"id": "1", "size_cohort": "100+", "revenue": "100+"}

        self.comparison_service_instance.remove_revenue([data])

        self.assertEqual([data], [expected_out])

    def test_remove_revenue_without_revenue_value(self):
        data = {"size_cohort": "100+"}
        expected_out = {"size_cohort": "100+", "revenue": "NaN"}

        self.comparison_service_instance.remove_revenue([data])

        self.assertEqual([data], [expected_out])

    def test_get_company_success(self):
        expected_out = {"sector": "Test"}
        self.mock_response_query_sql(expected_out)

        get_company_out = self.comparison_service_instance.get_company("id")

        self.assertEqual(get_company_out, expected_out)
        self.comparison_service_instance.session.execute.assert_called_once()

    def test_get_company_failed(self):
        self.comparison_service_instance.session.execute.side_effect = Exception(
            "error"
        )
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.comparison_service_instance.get_company("1")
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.comparison_service_instance.session.execute.assert_called_once()

    def test_get_peers_comparison_metric_with_acces_success(self):
        self.mock_response_list_query_sql([self.company])

        get_peers_comparison_metric_out = (
            self.comparison_service_instance.get_peers_comparison_metric(
                {"metric": "growth", "scenario": "Actuals", "alias": "growth"}, {}, True
            )
        )

        self.assertEqual(get_peers_comparison_metric_out, [self.company])
        self.comparison_service_instance.session.execute.assert_called_once()

    def test_get_peers_comparison_metric_without_acces_success_should_return_anonymized_data(
        self,
    ):
        self.mock_response_list_query_sql([self.company])
        company_anonymized = self.company.copy()
        company_anonymized["name"] = "{id}-xxxx".format(
            id=company_anonymized["id"][0:4]
        )

        get_peers_comparison_metric_out = (
            self.comparison_service_instance.get_peers_comparison_metric(
                {"metric": "growth", "scenario": "Actuals", "alias": "growth"},
                {},
                False,
            )
        )

        self.assertEqual(get_peers_comparison_metric_out, [company_anonymized])
        self.comparison_service_instance.session.execute.assert_called_once()

    def test_get_peers_comparison_metric_failed(self):
        self.comparison_service_instance.session.execute.side_effect = Exception(
            "error"
        )

        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.comparison_service_instance.get_peers_comparison_metric(
                    {"metric": "growth", "scenario": "Actuals", "alias": "growth"},
                    {},
                    True,
                )
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.comparison_service_instance.session.execute.assert_called_once()

    def test_get_peers_comparison_data_success(self):
        self.mock_response_list_query_sql([self.company])
        self.mock_proccess_comparison_results({"1": self.company})

        get_peers_comparison_data_out = (
            self.comparison_service_instance.get_peers_comparison_data(
                "1", [], [], [], [], [], "2020", True
            )
        )

        self.assertEqual(get_peers_comparison_data_out, {"1": self.company})
        self.assertEqual(self.comparison_service_instance.session.execute.call_count, 6)

    def test_get_peers_comparison_data_wihout_access_success(self):
        self.mock_response_list_query_sql([self.company])
        company_anonymized = self.company.copy()
        company_anonymized["name"] = "{id}-xxxx".format(
            id=company_anonymized["id"][0:4]
        )
        self.mock_proccess_comparison_results({"1": company_anonymized})

        get_peers_comparison_data_out = (
            self.comparison_service_instance.get_peers_comparison_data(
                "1", [], [], [], [], [], "2020", False
            )
        )

        self.assertEqual(get_peers_comparison_data_out, {"1": company_anonymized})
        self.assertEqual(self.comparison_service_instance.session.execute.call_count, 6)

    def test_get_peers_comparison_data_with_empty_company_id(self):
        self.mock_response_list_query_sql([])
        self.mock_proccess_comparison_results(dict())

        get_peers_comparison_data_out = (
            self.comparison_service_instance.get_peers_comparison_data(
                " ", [], [], [], [], [], "2020", True
            )
        )

        self.assertEqual(get_peers_comparison_data_out, dict())
        self.comparison_service_instance.session.execute.assert_not_called()

    def test_get_peers_comparison_data_failed(self):
        self.comparison_service_instance.session.execute.side_effect = Exception(
            "error"
        )

        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.comparison_service_instance.get_peers_comparison_data(
                    "1", [], [], [], [], [], "2020", True
                )
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.comparison_service_instance.session.execute.assert_called_once()

    def test_get_rank_success(self):
        company_data = self.company.copy()
        company_data.update(self.metric_value)
        expected_out = {"growth": "2 of 2", "revenue": "1 of 2"}

        get_rank_out = self.comparison_service_instance.get_rank(
            company_data, [self.comparison]
        )

        self.assertEqual(get_rank_out, expected_out)

    def test_get_rank_success_with_empty_company_data(self):
        get_rank_out = self.comparison_service_instance.get_rank(
            dict(), [self.comparison]
        )

        self.assertEqual(get_rank_out, dict())

    def test_get_peers_comparison_success(self):
        self.mock_response_query_sql(self.company)
        self.mock_response_list_query_sql([self.company, self.comparison])
        self.mock_proccess_comparison_results({"1": self.company, "2": self.comparison})
        peers = self.comparison.copy()
        expected_out = {
            "company_comparison_data": self.company,
            "rank": {},
            "peers_comparison_data": [peers],
        }

        get_peers_comparison_out = (
            self.comparison_service_instance.get_peers_comparison(
                "1", [], [], [], [], [], "2020", False, True
            )
        )

        self.assertEqual(get_peers_comparison_out, expected_out)
        self.assertEqual(self.comparison_service_instance.session.execute.call_count, 6)

    def test_get_peers_comparison_success_with_no_company_data(self):
        self.mock_response_list_query_sql([self.company, self.comparison])
        self.mock_proccess_comparison_results({"1": self.company, "2": self.comparison})
        peers = self.comparison.copy()
        peers["revenue"] = peers["size_cohort"]
        expected_out = {
            "company_comparison_data": dict(),
            "rank": dict(),
            "peers_comparison_data": [self.company, peers],
        }

        get_peers_comparison_out = (
            self.comparison_service_instance.get_peers_comparison(
                "1", [], [], [], [], [], "2020", True, False
            )
        )

        self.assertEqual(get_peers_comparison_out, expected_out)

    def test_get_peers_comparison_failed(self):
        self.comparison_service_instance.session.execute.side_effect = Exception(
            "error"
        )

        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.comparison_service_instance.get_peers_comparison(
                    "1", [], [], [], [], [], "2020", True, True
                )
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.comparison_service_instance.session.execute.assert_called_once()
