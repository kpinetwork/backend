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

    def test_get_range_from_value_without_valid_value(self):

        response = self.profile_range_instance.get_range_from_value(
            "NA", ranges=[self.ranges]
        )

        self.assertEqual(response, "NA")

    def test_get_range_from_value_without_ranges(self):
        self.mock_response_list_query_sql(self.ranges)

        response = self.profile_range_instance.get_range_from_value(40)

        self.assertEqual(response, "$30-<50 million")

    @parameterized.expand(
        [
            [
                [-4, 9, 41, 26, 46, -7, -5, 11, 33, 42],
                [-4.2, 10.2, 28.799999999999997, 41.2],
            ],
            [[1, 2, 3], [1, 2, 3]],
        ]
    )
    def test_get_intervals(self, values, expected_intervals):

        intervals = self.profile_range_instance.get_intervals(values)

        self.assertEqual(intervals, expected_intervals)

    @parameterized.expand(
        [
            [
                [1, 10, 30],
                [
                    {"label": "<$1 million", "min_value": None, "max_value": 1},
                    {"label": "$1-<$10 million", "min_value": 1, "max_value": 10},
                    {"label": "$10-<$30 million", "min_value": 10, "max_value": 30},
                    {"label": "$30 million+", "min_value": 30, "max_value": None},
                ],
            ],
            [
                [10, 25],
                [
                    {"label": "<$10 million", "min_value": None, "max_value": 10},
                    {"label": "$10-<$25 million", "min_value": 10, "max_value": 25},
                    {"label": "$25 million+", "min_value": 25, "max_value": None},
                ],
            ],
            [[], []],
        ]
    )
    def test_build_ranges_from_values(self, values, expected_ranges):

        ranges = self.profile_range_instance.build_ranges_from_values(values)

        self.assertEqual(ranges, expected_ranges)
