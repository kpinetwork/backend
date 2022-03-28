from unittest import TestCase
import logging
from unittest.mock import Mock
from src.utils.profile_range import ProfileRange, ProfileType
from parameterized import parameterized

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestProfileRange(TestCase):
    def setUp(self):
        self.ranges = [
            {
                "label": "$30-<50 million",
                "max_value": 50,
                "min_value": 30,
            },
            {
                "label": "100+",
                "max_value": None,
                "min_value": 100,
            },
        ]
        self.mock_session = Mock()
        self.mock_query_builder = Mock()
        self.mock_response_sql = Mock()
        self.profile_range_instance = ProfileRange(
            self.mock_session, self.mock_query_builder, logger, self.mock_response_sql
        )

    def mock_response_list_query_sql(self, response):
        attrs = {"process_query_list_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def test_get_ranges_success(self):
        self.mock_response_list_query_sql(self.ranges)

        ranges = self.profile_range_instance.get_profile_ranges(ProfileType.SIZE)

        self.assertEqual(ranges, self.ranges)

    def test_get_ranges_failed(self):
        self.profile_range_instance.session.execute.side_effect = Exception("error")

        ranges = self.profile_range_instance.get_profile_ranges(ProfileType.SIZE)

        self.assertEqual(ranges, [])

    @parameterized.expand(
        [
            [{"label": "$30-<50 million", "max_value": 50, "min_value": 30}, 31, True],
            [{"label": "100+", "max_value": None, "min_value": 100}, 120, True],
            [{"label": "100+", "max_value": None, "min_value": 100}, 10, False],
        ]
    )
    def test_verify_range(self, range, revenue, expected_out):

        response = self.profile_range_instance.verify_range(range, revenue)

        self.assertEqual(response, expected_out)
