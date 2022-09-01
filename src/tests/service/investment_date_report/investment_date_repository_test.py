from unittest import TestCase
import logging
from unittest.mock import Mock
from src.service.investment_date_report.investment_date_repository import (
    InvestmentDateReportRepository,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestInvestmentDateRepository(TestCase):
    def setUp(self):
        self.mock_session = Mock()
        self.mock_query_builder = Mock()
        self.mock_response_sql = Mock()
        self.mock_profile_range = Mock()
        self.repository = InvestmentDateReportRepository(
            self.mock_session, self.mock_query_builder, self.mock_response_sql, logger
        )
        self.company = {
            "id": "0123456",
            "name": "Company Test",
            "sector": "Computer Hardware",
            "vertical": "Life Sciences",
            "inves_profile_name": "Early stage VC",
            "size_cohort": "$30-<50 million",
            "margin_group": "Low growth",
        }
        self.scenarios = {
            "id": "0123456",
            "type": "Actuals",
            "scenario": "Actuals-2020",
            "metric": "Revenue",
            "value": 40,
        }

        self.metrics = {
            "actuals_revenue": 40,
            "actuals_ebitda": None,
            "prior_actuals_revenue": None,
            "prior_actuals_ebitda": None,
            "budget_revenue": None,
            "budget_ebitda": None,
        }
        self.investment = {"company_id": "0123456", "invest_year": 2020, "round": 1}

    def mock_response_query_sql(self, response):
        attrs = {"process_query_result.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def mock_response_list_query_sql(self, response):
        attrs = {"process_query_list_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def mock_base_metric_results(self, response):
        attrs = {"proccess_base_metrics_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def test_get_investments_success(self):
        expected_investments = {self.investment["company_id"]: self.investment}
        self.mock_response_list_query_sql([self.investment])

        investments = self.repository.get_investments()

        self.assertEqual(investments, expected_investments)

    def test_get_investments_should_fail(self):
        self.repository.session.execute.side_effect = Exception("error")

        investments = self.repository.get_investments()

        self.assertEqual(investments, dict())

    def test_get_years_success(self):
        invest_year = list()
        invest_year.append(self.investment["invest_year"])
        expected_years = [2018, 2019, 2020, 2021, 2022, 2023]

        years = self.repository.get_years(invest_year)

        self.assertEqual(years, expected_years)
