from unittest import TestCase
import logging
from unittest.mock import Mock
from src.service.metrics.metrics_service import MetricsService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestMetricsService(TestCase):
    def setUp(self):
        self.mock_session = Mock()
        self.mock_query_builder = Mock()
        self.mock_response_sql = Mock()

        self.query_response = {"id": "1234", "value": "3", "type": "standard"}
        self.mock_session.commit.return_value = {}
        self.metrics_service_instance = MetricsService(
            self.mock_session, self.mock_query_builder, logger, self.mock_response_sql
        )
        return

    def mock_query_result(self, response):
        attrs = {"process_query_result.return_value": response}
        self.mock_session.configure_mock(**attrs)

    def mock_response_list_query_sql(self, response):
        attrs = {"process_query_list_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def mock_process_query_average_result(self, response):
        attrs = {"process_query_average_result.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def test_success_get_metric_by_company_id(self):
        self.mock_query_result([self.query_response])
        self.mock_response_list_query_sql([self.query_response])
        response = self.metrics_service_instance.get_metric_by_company_id(
            "1234", "test", "type"
        )
        self.assertEqual(response, [self.query_response])
        self.assertEqual(self.mock_session.execute.call_count, 1)

    def test_success_get_metric_by_company_id_with_empty_response(self):
        self.mock_query_result([])
        self.mock_response_list_query_sql([])
        response = self.metrics_service_instance.get_metric_by_company_id(
            "1234", "", ""
        )
        self.assertEqual(response, [])
        self.assertEqual(self.mock_session.execute.call_count, 1)

    def test_get_metric_by_company_id_with_empty_id(self):
        response = self.metrics_service_instance.get_metric_by_company_id("", "", "")
        self.assertEqual(response, dict())
        self.metrics_service_instance.session.execute.assert_not_called()

    def test_get_metric_by_company_id_failed(self):
        self.metrics_service_instance.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.metrics_service_instance.get_metric_by_company_id(
                    self.query_response.get("id"), "", ""
                )
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.metrics_service_instance.session.execute.assert_called_once()

    def test_get_all_metrics_success(self):
        self.mock_response_list_query_sql([self.query_response])
        response = self.metrics_service_instance.get_metrics()

        self.assertEqual(response, [self.query_response])
        self.assertEqual(len(response), len([self.query_response]))
        self.metrics_service_instance.session.execute.assert_called_once()

    def test_get_all_metrics_failed(self):
        self.metrics_service_instance.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(self.metrics_service_instance.get_metrics())

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.metrics_service_instance.session.execute.assert_called_once()

    def test_get_average_metrics_with_invalid_name(self):
        name = " "
        company_id = "1"
        expected_output = dict()

        response = self.metrics_service_instance.get_average_metrics(name, company_id)

        self.assertEqual(response, expected_output)
        self.metrics_service_instance.session.execute.assert_not_called()


    def test_get_average_metrics_with_invalid_company_id(self):
        name = "test"
        company_id = " "
        expected_output = dict()

        response = self.metrics_service_instance.get_average_metrics(name, company_id)

        self.assertEqual(response, expected_output)
        self.metrics_service_instance.session.execute.assert_not_called()

    def test_get_average_metrics_success(self):
        expected_average = {"average": 123}
        name = "test"
        company_id = "1"
        self.mock_process_query_average_result(expected_average)

        result = self.metrics_service_instance.get_average_metrics(name, company_id)

        self.assertEqual(result, expected_average)
        self.metrics_service_instance.session.execute.assert_called_once()

    def test_get_average_metrics_success_with_empty_response(self):
        expected_average = dict()
        name = "test"
        company_id = "1"
        self.mock_process_query_average_result(expected_average)

        result = self.metrics_service_instance.get_average_metrics(name, company_id)

        self.assertEqual(result, expected_average)
        self.metrics_service_instance.session.execute.assert_called_once()    

    def test_get_average_metrics_failed(self):
        name = "test"
        company_id = "1"

        self.metrics_service_instance.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(self.metrics_service_instance.get_average_metrics(name, company_id))

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.metrics_service_instance.session.execute.assert_called_once()

