from unittest import TestCase
import logging
from unittest.mock import Mock
from src.service.metrics.metrics_service import MetricsService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestMetricsService(TestCase):
    def setUp(self):
        self.mock_session = Mock()
        self.mock_query_sql = Mock()
        self.mock_response_sql = Mock()

        self.query_response = {"id": "1234", "value": "3", "type": "standard"}
        self.mock_session.commit.return_value = {}
        self.metrics_service_instance = MetricsService(
            self.mock_session, self.mock_query_sql, logger, self.mock_response_sql
        )
        return

    def mock_query_result(self, response):
        mock_cursor = Mock()
        cursor_attrs = {"fetchall.return_value": response}
        mock_cursor.configure_mock(**cursor_attrs)
        engine_attrs = {"execute.return_value": mock_cursor}
        self.mock_session.configure_mock(**engine_attrs)

    def mock_response_query_sql(self, response):
        attrs = {"process_query_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def test_success_get_metric_by_id(self):
        self.mock_query_result([self.query_response])
        self.mock_response_query_sql(self.query_response)
        response = self.metrics_service_instance.get_metric_by_id("1234")
        self.assertEqual(response, self.query_response)
        self.assertEqual(self.mock_session.execute.call_count, 1)

    def test_success_get_metric_by_id_with_empty_response(self):
        self.mock_query_result([])
        self.mock_response_query_sql({})
        response = self.metrics_service_instance.get_metric_by_id("1234")
        self.assertEqual(response, {})
        self.assertEqual(self.mock_session.execute.call_count, 1)

    def test_get_metric_by_id_with_empty_id(self):
        response = self.metrics_service_instance.get_metric_by_id("")
        self.assertEqual(response, dict())
        self.metrics_service_instance.session.execute.assert_not_called()

    def test_get_metric_by_id_failed(self):
        self.metrics_service_instance.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.metrics_service_instance.get_metric_by_id(
                    self.query_response.get("id")
                )
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.metrics_service_instance.session.execute.assert_called_once()

    def test_get_all_metrics_success(self):
        self.metrics_service_instance.session.execute.return_value = iter(
            [self.query_response]
        )

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
