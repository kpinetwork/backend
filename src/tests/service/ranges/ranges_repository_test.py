import logging
from unittest import TestCase
from unittest.mock import Mock

from src.service.ranges.ranges_repository import RangesRepository
from src.utils.query_builder import QuerySQLBuilder

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestRangesRepository(TestCase):
    def setUp(self):
        self.range = {
            "id": "1",
            "label": "$100-<$200k",
            "min_value": 100,
            "max_value": 200,
            "type": "metric_name",
        }
        self.total_ranges = {"count": 1}
        self.mock_session = Mock()
        self.query_builder = QuerySQLBuilder()
        self.mock_response_sql = Mock()
        self.repository = RangesRepository(
            self.mock_session, self.query_builder, self.mock_response_sql, logger
        )

    def mock_response_query_sql(self, response):
        attrs = {"process_query_result.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def mock_response_list_query_sql(self, response):
        attrs = {"process_query_list_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def test_get_total_number_of_ranges_when_query_execution_success_should_return_the_ranges_count(
        self,
    ):
        self.mock_response_query_sql(self.total_ranges)

        total_number_of_ranges = self.repository.get_total_number_of_ranges()

        self.assertEqual(total_number_of_ranges, self.total_ranges)
        self.mock_session.execute.assert_called_once()

    def test_get_total_number_of_ranges_when_the_query_execution_fails_throws_an_exception(
        self,
    ):
        self.mock_session.execute.side_effect = Exception("error")

        with self.assertRaises(Exception) as context:
            self.repository.get_total_number_of_ranges()

        self.assertEqual(str(context.exception), "error")
        self.mock_session.execute.assert_called_once()

    def test_get_ranges_when_the_query_execution_success_should_return_the_ranges_data(
        self,
    ):
        self.mock_response_list_query_sql([self.range])

        get_ranges_response = self.repository.get_ranges()

        self.assertEqual(get_ranges_response, [self.range])
        self.mock_session.execute.assert_called_once()

    def test_get_ranges_when_the_query_execution_fails_should_return_empty_list(self):
        self.mock_session.execute.side_effect = Exception("error")

        get_ranges_response = self.repository.get_ranges()

        self.assertEqual(get_ranges_response, [])
        self.mock_session.execute.assert_called_once()

    def test_get_ranges_by_metric_when_query_execution_success_should_return_ranges_list(
        self,
    ):
        self.mock_response_list_query_sql([self.range])

        ranges_by_metric = self.repository.get_ranges_by_metric("revenue")

        self.assertEqual(ranges_by_metric, [self.range])
        self.mock_session.execute.assert_called_once()

    def test_get_ranges_by_metric_when_query_execution_fails_should_return_empty_list(
        self,
    ):
        self.mock_session.execute.side_effect = Exception("error")

        ranges_by_metric = self.repository.get_ranges_by_metric("revenue")

        self.assertEqual(ranges_by_metric, [])
        self.mock_session.execute.assert_called_once()
