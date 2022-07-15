from unittest import TestCase, mock
import logging
from unittest.mock import Mock
from src.service.investment_peers_report.investment_year_report import (
    InvestmentYearReport,
)
from src.service.calculator.calculator_service import CalculatorService
from src.service.calculator.calculator_report import CalculatorReport
from src.utils.company_anonymization import CompanyAnonymization

logger = logging.getLogger()
logger.setLevel(logging.INFO)
size_range = {"label": "$30-<50 million", "max_value": 50, "min_value": 30}


class TestInvestmentYearReport(TestCase):
    def setUp(self):
        self.mock_session = Mock()
        self.mock_query_builder = Mock()
        self.mock_response_sql = Mock()
        self.company_anonymization = CompanyAnonymization(object)
        self.mock_profile_range = Mock()
        self.calculator = CalculatorService(logger)
        self.report = CalculatorReport(
            logger, self.calculator, self.mock_profile_range, self.company_anonymization
        )
        self.repository = Mock()
        self.report_instance = InvestmentYearReport(
            logger, self.report, self.repository
        )
        self.company = {
            "id": "0123456",
            "name": "Company Test",
            "sector": "Computer Hardware",
            "vertical": "Life Sciences",
        }

        self.metrics = {
            "revenue": 40,
            "growth": 7,
            "ebitda_margin": -38,
            "revenue_vs_budget": 114,
            "ebitda_vs_budget": 125,
            "rule_of_40": -31,
            "gross_profit": -80,
            "gross_margin": -200,
            "sales_and_marketing": 125,
            "general_and_admin": 150,
            "research_and_development": 175,
        }

        self.scenarios = {
            "actuals_revenue": 40,
            "actuals_ebitda": -15,
            "prior_actuals_revenue": 37.5,
            "budget_revenue": 35,
            "budget_ebitda": -12,
            "actuals_cost_of_goods": 120,
            "actuals_sales_of_marketing": 50,
            "actuals_general_and_admin": 60,
            "actuals_research_and_development": 70,
        }

        self.range = {"label": "$30-<50 million", "max_value": 50, "min_value": 30}

    def mock_base_metric_results(self, response):
        attrs = {"proccess_base_metrics_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def test_remove_unused_fields(self):
        company = self.company.copy()
        company["actuals_revenue"] = 30
        company["scenario"] = "Actuals-2020"

        self.report_instance.remove_unused_fields(company)

        self.assertEqual(company, self.company)

    def test_add_calculated_metrics_with_access(self):
        data = dict()
        company = self.company.copy()
        expected_company = self.company.copy()
        company.update(self.scenarios)
        metrics = self.metrics.copy()
        metrics.update({"size_cohort": "NA", "margin_group": "NA"})
        expected_company.update(metrics)
        data[company["id"]] = company

        self.report_instance.add_calculated_metrics(data, True)

        self.assertEqual(data[company["id"]], expected_company)

    def test_add_calculated_metrics_without_access(self):
        company = self.company.copy()
        company.update(self.scenarios)
        data = {company["id"]: company}
        expected_company = self.company.copy()
        metrics = self.metrics.copy()
        metrics.update(
            {"size_cohort": "$30-<50 million", "margin_group": "$30-<50 million"}
        )
        expected_company.update(metrics)
        expected_company["revenue"] = self.range["label"]
        expected_company["name"] = "0123-xxxx"
        self.mock_profile_range.get_profile_ranges.return_value = [self.range]

        self.report_instance.add_calculated_metrics(data, False)

        self.assertEqual(data[company["id"]], expected_company)

    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    def test_get_peers_by_investment_year_from_main(self, mock_set_company_permissions):
        company = self.company.copy()
        expected_company = self.company.copy()
        metrics = self.metrics.copy()
        metrics.update({"size_cohort": "NA", "margin_group": "NA"})
        expected_company.update(metrics)
        company.update(self.scenarios)
        self.repository.get_base_metrics.return_value = {company["id"]: company}

        comparison = self.report_instance.get_peers_by_investment_year(
            None, 0, "user@email.com", True, True
        )

        self.assertEqual(
            comparison,
            {
                "company_comparison_data": {},
                "peers_comparison_data": [expected_company],
            },
        )
        mock_set_company_permissions.assert_called()

    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    def test_get_peers_by_investment_year(self, mock_set_company_permissions):
        company = self.company.copy()
        expected_company = self.company.copy()
        metrics = self.metrics.copy()
        metrics.update({"size_cohort": "NA", "margin_group": "NA"})
        expected_company.update(metrics)
        company.update(self.scenarios)
        self.repository.get_base_metrics.return_value = {company["id"]: company}

        comparison = self.report_instance.get_peers_by_investment_year(
            company["id"], 0, "user@email.com", False, True
        )

        self.assertEqual(
            comparison,
            {"company_comparison_data": expected_company, "peers_comparison_data": []},
        )
        mock_set_company_permissions.assert_called()

    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    def test_get_peers_by_investment_year_fail(self, mock_set_company_permissions):
        self.repository.get_base_metrics.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            self.report_instance.get_peers_by_investment_year(
                "123", 0, "user@email.com", True, True
            )

        self.assertEqual(str(context.exception), "error")
        mock_set_company_permissions.assert_called()
