import json
from unittest import TestCase, mock
from src.handlers.metric.get_metric_types_handler import handler


class TestGetMetricTypesHandler(TestCase):
    def setUp(self):
        self.metrics = ["Revenue", "Ebitda"]
        self.event = {}

    @mock.patch("metric_type_service.MetricTypesService.get_metric_types")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_metric_types_handler_success_should_return_200_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_get_metric_types,
    ):
        mock_get_metric_types.return_value = self.metrics

        response = handler(self.event, {})

        mock_get_metric_types.assert_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 200)
        self.assertEqual(response.get("body"), json.dumps(self.metrics, default=str))

    @mock.patch("metric_type_service.MetricTypesService.get_metric_types")
    @mock.patch("connection.create_db_engine")
    @mock.patch("connection.create_db_session")
    def test_get_metric_types_fails_should_return_error_400_response(
        self,
        mock_create_db_session,
        mock_create_db_engine,
        mock_get_metric_types,
    ):
        error_message = "Cannot get metrics"
        mock_get_metric_types.side_effect = Exception(error_message)

        response = handler(self.event, {})

        mock_get_metric_types.assert_called()
        mock_create_db_engine.assert_not_called()
        mock_create_db_session.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))
