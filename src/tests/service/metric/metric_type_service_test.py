from unittest import TestCase
import logging
from unittest.mock import Mock
from src.service.metric.metric_type_service import MetricTypesService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestMetricTypesService(TestCase):
    def setUp(self):
        self.metrics = [{"name": "Revenue"}, {"name": "Ebitda"}]
        self.mock_session = Mock()
        self.mock_query_builder = Mock()
        self.mock_response_sql = Mock()
        self.service_instance = MetricTypesService(
            self.mock_session, self.mock_query_builder, self.mock_response_sql, logger
        )

    def mock_response_list_query_sql(self, response):
        attrs = {"process_query_list_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def test_get_metric_types_success(self):
        self.mock_response_list_query_sql(self.metrics)

        metric_names = self.service_instance.get_metric_types()

        self.assertEqual(metric_names, ["Revenue", "Ebitda"])
        self.service_instance.session.execute.assert_called_once()

    def test_get_metric_types_failed(self):
        self.mock_session.execute.side_effect = Exception("error")

        metric_names = self.service_instance.get_metric_types()

        self.assertEqual(metric_names, [])
        self.service_instance.session.execute.assert_called_once()
