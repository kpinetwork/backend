import logging
from unittest.mock import Mock
from unittest import TestCase

from src.service.ranges.ranges_service import RangesService
from src.utils.app_names import MetricNames

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestRangesService(TestCase):
    def setUp(self):
        self.ranges = [
            {
                "id": "1",
                "label": "$100-<$200k",
                "min_value": 100,
                "max_value": 200,
                "type": "revenue",
            },
            {
                "id": "2",
                "label": "$200-<$300k",
                "min_value": 200,
                "max_value": 300,
                "type": "revenue_per_employee",
            },
            {
                "id": "3",
                "label": "$200-<$300k",
                "min_value": 200,
                "max_value": 300,
                "type": "revenue",
            },
        ]
        self.total_ranges = {"count": 3}
        self.ranges_by_metric = [
            {
                "key": "revenue",
                "name": MetricNames.REVENUE,
                "ranges": [
                    {
                        "id": "1",
                        "label": "$100-<$200k",
                        "min_value": 100,
                        "max_value": 200,
                    },
                    {
                        "id": "3",
                        "label": "$200-<$300k",
                        "min_value": 200,
                        "max_value": 300,
                    },
                ],
            },
            {
                "key": "revenue_per_employee",
                "name": MetricNames.REVENUE_PER_EMPLOYEE,
                "ranges": [
                    {
                        "id": "2",
                        "label": "$200-<$300k",
                        "min_value": 200,
                        "max_value": 300,
                    }
                ],
            },
        ]
        self.mock_repository = Mock()
        self.ranges_service_instance = RangesService(logger, self.mock_repository)

    def test_get_all_ranges_if_query_execution_success_should_return_the_count_and_ranges_data(
        self,
    ):
        expected_ranges_dict = {
            "total": self.total_ranges.get("count"),
            "ranges": self.ranges_by_metric,
        }
        self.mock_repository.get_total_number_of_ranges.return_value = self.total_ranges
        self.mock_repository.get_ranges.return_value = self.ranges

        get_all_ranges_response = self.ranges_service_instance.get_all_ranges()

        self.assertEqual(get_all_ranges_response, expected_ranges_dict)
        self.mock_repository.get_total_number_of_ranges.assert_called_once()
        self.mock_repository.get_ranges.assert_called_once()

    def test_get_all_ranges_when_query_execution_fails_should_raise_an_exception(self):
        self.mock_repository.get_total_number_of_ranges.side_effect = Exception("error")

        with self.assertRaises(Exception) as context:
            self.ranges_service_instance.get_all_ranges()

        self.assertEqual(str(context.exception), "Can't get ranges")
        self.mock_repository.get_total_number_of_ranges.assert_called_once()

    def test_get_ranges_by_metric_when_metric_name_is_invalid_should_raise_an_exception(
        self,
    ):
        with self.assertRaises(Exception) as context:
            self.ranges_service_instance.get_ranges_by_metric(None)

        self.assertEqual(str(context.exception), "Invalid metric")
        self.mock_repository.get_ranges_by_metric.assert_not_called()

    def test_get_ranges_by_metric_when_metric_name_is_valid_should_return_list_with_ranges(
        self,
    ):
        self.mock_repository.get_ranges_by_metric.return_value = self.ranges

        ranges = self.ranges_service_instance.get_ranges_by_metric("revenue")

        self.mock_repository.get_ranges_by_metric.assert_called()
        self.assertEqual(ranges, self.ranges)
