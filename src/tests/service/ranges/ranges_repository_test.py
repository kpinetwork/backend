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

    def test_get_queries_modify_metric_ranges_with_empty_list_should_return_empty_list(
        self,
    ):

        queries_list = (
            self.repository._RangesRepository__get_queries_modify_metric_ranges(
                "key", [], lambda x, y: x + y, "million"
            )
        )

        self.assertEqual(queries_list, [])

    def test_get_queries_delete_metric_ranges_with_empty_list_should_return_empty_list(
        self,
    ):

        queries_list = (
            self.repository._RangesRepository__get_queries_delete_metric_ranges(
                [], lambda x, y: x + y
            )
        )

        self.assertEqual(queries_list, [])

    def test_modify_metric_ranges_with_data_and_limit_to_update_should_call_db_session_execute(
        self,
    ):
        metric_ranges_data = {
            "metric_key": "new_bookings_metric",
            "label": "million",
            "ranges_to_add": [{"min_value": 30, "max_value": 40}],
            "ranges_to_delete": ["123"],
            "ranges_to_update": [
                {"id": "1", "min_value": None, "max_value": 30},
                {"id": "2", "min_value": 40, "max_value": None},
            ],
        }

        updated = self.repository.modify_metric_ranges(**metric_ranges_data)

        self.assertTrue(updated)
        self.mock_session.execute.assert_called_once()

    def test_modify_metric_ranges_with_limit_ranges_to_add_should_call_db_session_execute(
        self,
    ):
        metric_ranges_data = {
            "metric_key": "new_bookings_metric",
            "label": "million",
            "ranges_to_add": [
                {"min_value": 30, "max_value": 40},
                {"min_value": None, "max_value": 30},
                {"min_value": 40, "max_value": None},
            ],
            "ranges_to_delete": ["123"],
            "ranges_to_update": [],
        }

        updated = self.repository.modify_metric_ranges(**metric_ranges_data)

        self.assertTrue(updated)
        self.mock_session.execute.assert_called_once()

    def test_modify_metric_ranges_ranges_to_delete_is_wrong_should_call_db_session_execute(
        self,
    ):
        metric_ranges_data = {
            "metric_key": "new_bookings_metric",
            "label": "million",
            "ranges_to_add": [
                {"min_value": 30, "max_value": 40},
            ],
            "ranges_to_delete": 1,
            "ranges_to_update": [],
        }

        with self.assertRaises(Exception) as context:
            self.repository.modify_metric_ranges(**metric_ranges_data)

        self.assertEqual(
            str(context.exception), "Invalid format to delete metric_ranges"
        )
        self.mock_session.execute.assert_not_called()

    def test_modify_metric_ranges_with_invalid_data_format_should_raise_exception(
        self,
    ):
        metric_ranges_data = {
            "metric_key": "new_bookings_metric",
            "label": "million",
            "ranges_to_add": 1,
            "ranges_to_delete": ["123"],
            "ranges_to_update": [{"id": "1", "min_value": 20, "max_value": 30}],
        }
        with self.assertRaises(Exception) as context:
            self.repository.modify_metric_ranges(**metric_ranges_data)

        self.assertEqual(
            str(context.exception), "Invalid format to update metric_ranges"
        )
        self.mock_session.execute.assert_not_called()

    def test_modify_metric_ranges_with_invalid_transaction_exec_should_not_modify_metric_ranges(
        self,
    ):
        metric_ranges_data = {
            "metric_key": "new_bookings_metric",
            "label": "million",
            "ranges_to_add": [{"min_value": 30, "max_value": 40}],
            "ranges_to_delete": ["123"],
            "ranges_to_update": [{"id": "1", "min_value": 20, "max_value": 30}],
        }
        self.mock_session.execute.side_effect = Exception("error with query exec")

        updated = self.repository.modify_metric_ranges(**metric_ranges_data)

        self.assertFalse(updated)
        self.mock_session.execute.assert_called_once()
        self.mock_session.rollback.assert_called()
