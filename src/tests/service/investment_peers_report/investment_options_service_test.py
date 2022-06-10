from unittest import TestCase, mock
import logging
from parameterized import parameterized
from unittest.mock import Mock
from src.service.investment_peers_report.investment_options_service import (
    InvestmentOptionsService,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestInvestmentOptionsService(TestCase):
    def setUp(self):
        self.mock_session = Mock()
        self.mock_query_builder = Mock()
        self.mock_response_sql = Mock()
        self.mock_profile_range = Mock()
        self.service = InvestmentOptionsService(
            self.mock_session, self.mock_query_builder, logger, self.mock_response_sql
        )
        self.invest_years = [{"invest_year": 2020}, {"invest_year": 2021}]

        self.metric_years = [
            {"metric_year": 2018},
            {"metric_year": 2020},
            {"metric_year": 2022},
        ]

    def mock_response_list_query_sql(self, response):
        attrs = {"process_query_list_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def test_get_investment_years_success(self):
        self.mock_response_list_query_sql(self.invest_years)

        years = self.service.get_investment_years()

        self.assertEqual(years, self.invest_years)

    def test_get_investment_years_should_fail(self):
        self.mock_session.execute.side_effect = Exception("error")

        years = self.service.get_investment_years()

        self.assertEqual(years, [])

    def test_get_metric_years_success(self):
        self.mock_response_list_query_sql(self.metric_years)

        years = self.service.get_metric_years()

        self.assertEqual(years, self.metric_years)

    def test_get_metric_years_should_fail(self):
        self.mock_session.execute.side_effect = Exception("error")

        years = self.service.get_metric_years()

        self.assertEqual(years, [])

    def test_get_years_from_list_of_dict(self):
        expected_years = [2020, 2021]

        years = self.service.get_years_from_list_of_dict(
            "invest_year", self.invest_years
        )

        self.assertEqual(years, expected_years)

    @mock.patch.object(InvestmentOptionsService, "get_metric_years")
    @mock.patch.object(InvestmentOptionsService, "get_investment_years")
    def test_get_years_with_investment_values(
        self, mock_get_investment_year, mock_get_metric_years
    ):
        expected_invest_years = [-3, -2, -1, 0, 1, 2]
        mock_get_investment_year.return_value = self.invest_years
        mock_get_metric_years.return_value = self.metric_years

        years = self.service.get_years()

        self.assertEqual(years, expected_invest_years)
        mock_get_investment_year.assert_called()
        mock_get_metric_years.assert_called()

    @mock.patch.object(InvestmentOptionsService, "get_metric_years")
    @mock.patch.object(InvestmentOptionsService, "get_investment_years")
    def test_get_years_without_investments(
        self, mock_get_investment_year, mock_get_metric_years
    ):
        mock_get_investment_year.return_value = []

        years = self.service.get_years()

        self.assertEqual(years, [])
        mock_get_investment_year.assert_called()
        mock_get_metric_years.assert_not_called()

    def test_get_ordinal_year(self):
        expected_name = "Second full year after investment"

        name = self.service.get_ordinal_year(2)

        self.assertEqual(name, expected_name)

    @parameterized.expand(
        [[-2, "Two years before investment"], [-1, "Year before investment"]]
    )
    def test_get_cardinal_year(self, year, expected_name):

        name = self.service.get_cardinal_year(year)

        self.assertEqual(name, expected_name)

    @parameterized.expand(
        [
            [-3, "Three years before investment"],
            [0, "Year of investment"],
            [3, "Third full year after investment"],
        ]
    )
    def test_get_year_name_option(self, year, expected_name):
        name = self.service.get_year_name_option(year)

        self.assertEqual(name, expected_name)

    @mock.patch.object(InvestmentOptionsService, "get_years")
    def test_get_years_options_should_return_dict(self, mock_get_years):
        mock_get_years.return_value = [-2, 0, 1]
        expected_options = [
            {"value": -2, "name": "Two years before investment"},
            {"value": 0, "name": "Year of investment"},
            {"value": 1, "name": "First full year after investment"},
        ]

        options = self.service.get_years_options()

        self.assertEqual(options, expected_options)
