from unittest import TestCase, mock
import logging
from unittest.mock import Mock
from src.service.dynamic_report.dynamic_report import DynamicReport
from src.service.by_metric_report.by_metric_report import ByMetricReport
from src.service.investment_peers_report.investment_year_report import (
    InvestmentYearReport,
)
from src.service.comparison_vs_peers.comparison_vs_peers_service import (
    ComparisonvsPeersService,
)
from src.service.calculator.calculator_report import CalculatorReport
from src.service.calculator.calculator_service import CalculatorService
from src.utils.company_anonymization import CompanyAnonymization

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestDynamicReport(TestCase):
    def setUp(self):
        self.calculator = CalculatorService(logger)
        self.company_anonymization = CompanyAnonymization(object)
        self.mock_profile_range = Mock()
        self.mock_repository = Mock()
        self.mock_response_sql = Mock()
        self.calculator_report = CalculatorReport(
            logger, self.calculator, self.mock_profile_range, self.company_anonymization
        )
        self.metric_report = ByMetricReport(
            logger,
            self.calculator,
            self.mock_repository,
            self.mock_profile_range,
            self.company_anonymization,
        )
        self.investment_report = InvestmentYearReport(
            logger, self.calculator_report, self.mock_repository
        )
        self.calendar_report = ComparisonvsPeersService(
            logger, self.calculator_report, self.mock_repository
        )
        self.report_instance = DynamicReport(
            logger,
            self.metric_report,
            self.investment_report,
            self.calendar_report,
        )
        self.company = {
            "id": "0123456",
            "name": "Company Test",
            "sector": "Computer Hardware",
            "vertical": "Life Sciences",
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
        self.sizes = [
            {"label": ">$20 million", "min_value": None, "max_value": 20},
            {"label": "$20 million - $40 million", "min_value": 20, "max_value": 40},
            {"label": "$40 million +", "min_value": 40, "max_value": None},
        ]
        self.data = {
            "1": {"id": "1", "name": "Test", "metrics": {2020: 1, 2021: 2}},
            "2": {"id": "2", "name": "Company", "metrics": {2020: 4, 2021: -1}},
        }
        self.investment = {"company_id": "1", "invest_year": 2020, "round": 1}

    @mock.patch(
        "src.service.by_metric_report.by_metric_report.ByMetricReport.get_records"
    )
    @mock.patch(
        "src.service.by_metric_report.by_metric_report.ByMetricReport.get_profiles"
    )
    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    def test_get_dynamic_report_should_return_dynamic_metrics_with_calendar_year(
        self, mock_set_company_permissions, mock_get_profiles, mock_get_records
    ):
        expected_response = {
            "header": ["name", "actuals-revenue"],
            "company_comparison_data": {},
            "peers_comparison_data": [
                {"id": "2", "name": "Company", "actuals-revenue": 4},
                {"id": "1", "name": "Test", "actuals-revenue": 1},
            ],
        }
        profiles = {
            "1": {"size_cohort": "", "margin_group": ""},
            "2": {"size_cohort": "", "margin_group": ""},
        }
        mock_get_records.return_value = self.data
        mock_get_profiles.return_value = (profiles, self.sizes)
        self.mock_repository.get_functions_metric.return_value = {"actuals_revenue": {}}

        response = self.report_instance.get_dynamic_report(
            None, "user@mail.com", "actuals-revenue", 2020, None, False, True
        )

        mock_set_company_permissions.assert_called()
        self.assertEqual(response, expected_response)

    @mock.patch(
        "src.service.by_metric_report.by_metric_report.ByMetricReport.get_records"
    )
    @mock.patch(
        "src.service.by_metric_report.by_metric_report.ByMetricReport.get_profiles"
    )
    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    def test_get_dynamic_report_should_when_there_is_no_metric(
        self, mock_set_company_permissions, mock_get_profiles, mock_get_records
    ):
        expected_response = {
            "header": ["name", "actuals-revenue"],
            "company_comparison_data": {},
            "peers_comparison_data": [
                {"id": "2", "name": "Company", "actuals-revenue": "NA"},
                {"id": "1", "name": "Test", "actuals-revenue": 1},
            ],
        }
        profiles = {
            "1": {"size_cohort": "", "margin_group": ""},
            "2": {"size_cohort": "", "margin_group": ""},
        }
        mock_get_records.return_value = {
            "1": {"id": "1", "name": "Test", "metrics": {2020: 1, 2021: 2}},
            "2": {"id": "2", "name": "Company", "metrics": {}},
        }
        mock_get_profiles.return_value = (profiles, self.sizes)
        self.mock_repository.get_functions_metric.return_value = {"actuals_revenue": {}}

        response = self.report_instance.get_dynamic_report(
            None, "user@mail.com", "actuals-revenue", 2020, None, False, True
        )

        mock_set_company_permissions.assert_called()
        self.assertEqual(response, expected_response)

    @mock.patch(
        "src.service.by_metric_report.by_metric_report.ByMetricReport.get_records"
    )
    @mock.patch(
        "src.service.by_metric_report.by_metric_report.ByMetricReport.get_profiles"
    )
    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    def test_get_dynamic_report_should_return_dynamic_metrics_with_invest_year(
        self, mock_set_company_permissions, mock_get_profiles, mock_get_records
    ):
        expected_response = {
            "header": ["name", "actuals-revenue"],
            "company_comparison_data": {},
            "peers_comparison_data": [
                {"id": "2", "name": "Company", "actuals-revenue": -1},
                {"id": "1", "name": "Test", "actuals-revenue": 1},
            ],
        }
        profiles = {
            "1": {"size_cohort": "", "margin_group": ""},
            "2": {"size_cohort": "", "margin_group": ""},
        }
        investments = {
            "1": {"company_id": "1", "invest_year": 2020, "round": 1},
            "2": {"company_id": "2", "invest_year": 2021, "round": 1},
        }
        mock_get_records.return_value = self.data
        mock_get_profiles.return_value = (profiles, self.sizes)
        years = [2020]
        self.mock_repository.get_years.return_value = years
        self.mock_repository.get_functions_metric.return_value = {"actuals_revenue": {}}
        self.mock_repository.get_investments.return_value = investments

        response = self.report_instance.get_dynamic_report(
            None, "user@mail.com", "actuals-revenue", None, 0, False, True
        )

        mock_set_company_permissions.assert_called()
        self.assertEqual(response, expected_response)

    @mock.patch(
        "src.service.by_metric_report.by_metric_report.ByMetricReport.get_records"
    )
    @mock.patch(
        "src.service.by_metric_report.by_metric_report.ByMetricReport.get_profiles"
    )
    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    def test_get_dynamic_report_should_return_dynamic_metrics_with_company_id(
        self, mock_set_company_permissions, mock_get_profiles, mock_get_records
    ):
        expected_response = {
            "header": ["name", "actuals-revenue"],
            "company_comparison_data": {
                "id": "1",
                "name": "Test",
                "actuals-revenue": 1,
            },
            "peers_comparison_data": [
                {"id": "2", "name": "Company", "actuals-revenue": 4},
            ],
        }
        profiles = {
            "1": {"size_cohort": "", "margin_group": ""},
            "2": {"size_cohort": "", "margin_group": ""},
        }
        mock_get_records.return_value = self.data
        mock_get_profiles.return_value = (profiles, self.sizes)
        self.mock_repository.get_functions_metric.return_value = {"actuals_revenue": {}}

        response = self.report_instance.get_dynamic_report(
            "1", "user@mail.com", "actuals-revenue", 2020, None, False, True
        )

        mock_set_company_permissions.assert_called()
        self.assertEqual(response, expected_response)

    @mock.patch(
        "src.service.by_metric_report.by_metric_report.ByMetricReport.get_records"
    )
    @mock.patch(
        "src.service.by_metric_report.by_metric_report.ByMetricReport.get_profiles"
    )
    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    def test_get_dynamic_report_should_return_by_metric_report(
        self, mock_set_company_permissions, mock_get_profiles, mock_get_records
    ):
        expected_response = {
            "header": ["name", 2020, 2021],
            "company_comparison_data": {},
            "peers_comparison_data": [
                {"id": "2", "name": "Company", "metrics": {2020: 4, 2021: -1}},
                {"id": "1", "name": "Test", "metrics": {2020: 1, 2021: 2}},
            ],
        }
        profiles = {
            "1": {"size_cohort": "", "margin_group": ""},
            "2": {"size_cohort": "", "margin_group": ""},
        }
        years = [2020, 2021]
        self.mock_repository.get_years.return_value = years
        mock_get_records.return_value = self.data
        mock_get_profiles.return_value = (profiles, self.sizes)
        self.mock_repository.get_functions_metric.return_value = {"rule_of_40": {}}

        response = self.report_instance.get_dynamic_report(
            None, "user@mail.com", "rule_of_40", None, None, False, True
        )

        mock_set_company_permissions.assert_called()
        self.assertEqual(response, expected_response)

    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    def test_get_dynamic_report_should_return_investment_report(
        self, mock_set_company_permissions
    ):
        expecte_response = {
            "header": [
                "name",
                "sector",
                "vertical",
                "revenue",
                "growth",
                "ebitda_margin",
                "revenue_vs_budget",
                "ebitda_vs_budget",
                "rule_of_40",
            ],
            "company_comparison_data": {},
            "peers_comparison_data": [
                {
                    "id": "0123456",
                    "name": "Company Test",
                    "sector": "Computer Hardware",
                    "vertical": "Life Sciences",
                    "revenue": 40,
                    "growth": 7,
                    "ebitda_margin": -38,
                    "revenue_vs_budget": 114,
                    "ebitda_vs_budget": 125,
                    "rule_of_40": -31,
                    "size_cohort": "NA",
                    "margin_group": "NA",
                    "gross_profit": -80,
                    "gross_margin": -2,
                    "sales_and_marketing": 125,
                    "general_and_admin": 150,
                    "research_and_development": 175,
                }
            ],
        }
        company = self.company.copy()
        company.update(self.scenarios)
        self.mock_repository.get_base_metrics.return_value = {company["id"]: company}

        response = self.report_instance.get_dynamic_report(
            None, "user@mail.com", None, None, 1, False, True
        )

        mock_set_company_permissions.assert_called()
        self.assertEqual(response, expecte_response)

    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    def test_get_dynamic_report_should_return_calendar_report(
        self, mock_set_company_permissions
    ):
        company = self.company.copy()
        company.update(self.scenarios)
        self.mock_repository.get_base_metrics.return_value = {company["id"]: company}
        expected_result = {
            "header": [
                "name",
                "sector",
                "vertical",
                "revenue",
                "growth",
                "ebitda_margin",
                "revenue_vs_budget",
                "ebitda_vs_budget",
                "rule_of_40",
            ],
            "company_comparison_data": {},
            "peers_comparison_data": [
                {
                    "id": "0123456",
                    "name": "Company Test",
                    "sector": "Computer Hardware",
                    "vertical": "Life Sciences",
                    "revenue": 40,
                    "growth": 7,
                    "ebitda_margin": -38,
                    "revenue_vs_budget": 114,
                    "ebitda_vs_budget": 125,
                    "rule_of_40": -31,
                    "size_cohort": "NA",
                    "margin_group": "NA",
                    "gross_profit": -80,
                    "gross_margin": -2,
                    "sales_and_marketing": 125,
                    "general_and_admin": 150,
                    "research_and_development": 175,
                }
            ],
        }

        response = self.report_instance.get_dynamic_report(
            None, "user@mail.com", None, 2020, None, False, True
        )

        mock_set_company_permissions.assert_called()
        self.assertEqual(response, expected_result)

    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    def test_get_dynamic_report_fail(self, mock_set_company_permissions):
        mock_set_company_permissions.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            self.report_instance.get_dynamic_report(
                None, "user@mail.com", "actuals_revenue", 2020, None, False, True
            )

        self.assertEqual(str(context.exception), "error")
        mock_set_company_permissions.assert_called()
