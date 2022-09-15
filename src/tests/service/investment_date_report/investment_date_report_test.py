from collections import OrderedDict
from unittest import TestCase, mock
import logging
from unittest.mock import Mock
from src.service.investment_date_report.investment_date_report import (
    InvestmentDateReport,
)
from src.service.calculator.calculator_service import CalculatorService
from src.utils.company_anonymization import CompanyAnonymization

logger = logging.getLogger()
logger.setLevel(logging.INFO)
size_range = {"label": "$30-<50 million", "max_value": 50, "min_value": 30}


def get_data(metric: str, years: list, access: bool, companies: dict, **conditions):
    metrics = {
        "metric_name": "growth",
        2019: 10,
        2020: -8,
        2021: 145,
        2022: 5,
        2023: 11,
        2024: 1,
    }
    metrics["metric_name"] = metric
    return {"1": {"id": "1", "name": "Test", "metrics": metrics}}


class TestInvestmentDateReport(TestCase):
    def setUp(self):
        self.calculator = CalculatorService(logger)
        self.company_anonymization = CompanyAnonymization(object)
        self.mock_profile_range = Mock()
        self.mock_repository = Mock()
        self.mock_metric_repository = Mock()
        self.mock_metric_report_instance = Mock()
        self.report_instance = InvestmentDateReport(
            logger,
            self.calculator,
            self.mock_repository,
            self.mock_metric_repository,
            self.mock_metric_report_instance,
            self.mock_profile_range,
            self.company_anonymization,
        )
        self.companies = [
            {
                "id": "1",
                "name": "Test",
                "metrics": [
                    {
                        "metric_name": "growth",
                        "2019": "NA",
                        "2020": -8,
                        "2021": 145,
                        "2022": "NA",
                        "2023": "NA",
                        "2024": "NA",
                    }
                ],
            },
            {
                "id": "2",
                "name": "Company",
                "metrics": [
                    {
                        "metric_name": "growth",
                        "2019": 37,
                        "2020": 34,
                        "2021": 83,
                        "2022": "NA",
                        "2023": "NA",
                        "2024": "NA",
                    }
                ],
            },
        ]
        self.records = [
            {"id": "1", "name": "Test", "year": 2019, "value": None},
            {"id": "1", "name": "Test", "year": 2020, "value": -8},
            {"id": "1", "name": "Test", "year": 2021, "value": 145},
            {"id": "1", "name": "Test", "year": 2022, "value": None},
            {"id": "1", "name": "Test", "year": 2023, "value": None},
            {"id": "1", "name": "Test", "year": 2024, "value": None},
        ]
        self.sizes = [
            {"label": ">$20 million", "min_value": None, "max_value": 20},
            {"label": "$20 million - $40 million", "min_value": 20, "max_value": 40},
            {"label": "$40 million +", "min_value": 40, "max_value": None},
        ]
        self.headers = [
            "id",
            "name",
            "metric name",
            "Investment - 2",
            "Investment - 1",
            "Year of investment",
            "Investment + 1",
            "Investment + 2",
            "Investment +3",
        ]

    @mock.patch(
        "src.service.investment_date_report.investment_date_report."
        "InvestmentDateReport.get_valid_year_records"
    )
    def test_get_by_metrics_records(self, mock_get_valid_year_records):

        companies_dict = {"1": 2021}

        self.mock_metric_repository.add_company_filters.return_value = dict()
        years = [2019, 2020, 2021, 2022, 2023, 2024]
        valid_metrics = {
            2019: "NA",
            2020: -8,
            2021: 145,
            2022: "NA",
            2023: "NA",
            2024: "NA",
        }
        data = {
            "1": {
                "id": "1",
                "name": "Test",
                "metrics": {
                    2019: None,
                    2020: -8,
                    2021: 145,
                    2022: None,
                    2023: None,
                    2024: None,
                },
            },
        }

        profiles = {
            "1": {"size_cohort": "", "margin_group": ""},
        }

        self.mock_metric_report_instance.get_records.return_value = data
        self.mock_metric_report_instance.get_profiles.return_value = (
            profiles,
            self.sizes,
        )
        mock_get_valid_year_records.return_value = valid_metrics

        expected_data = {
            "1": {
                "id": "1",
                "name": "Test",
                "metrics": {
                    2019: "NA",
                    2020: -8,
                    2021: 145,
                    2022: "NA",
                    2023: "NA",
                    2024: "NA",
                    "metric_name": "growth",
                },
            }
        }

        metric_records = self.report_instance.get_by_metric_records(
            "growth", years, False, companies_dict
        )

        self.assertEqual(metric_records, expected_data)

    def test_get_valid_year_records(self):
        company = {
            "id": "1",
            "name": "Test",
            "metrics": {
                2018: 3,
                2019: 10,
                2020: -8,
                2021: 145,
                2022: 5,
                2023: 11,
                2024: 1,
            },
        }
        years = [2019, 2020, 2021, 2022, 2023, 2024]
        expected_data = {2019: 10, 2020: -8, 2021: 145, 2022: 5, 2023: 11, 2024: 1}

        metric_data = self.report_instance.get_valid_year_records(company, years)

        self.assertEqual(metric_data, expected_data)

    @mock.patch(
        "src.service.investment_date_report.investment_date_report."
        "InvestmentDateReport.get_valid_year_records"
    )
    def test_get_records_by_invest_year(self, mock_get_valid_year_records):
        company = {
            "id": "1",
            "name": "Test",
            "metrics": {
                2018: 3,
                2019: 10,
                2020: -8,
                2021: 145,
                2022: 5,
                2023: 11,
                2024: 1,
            },
        }
        companies_dict = {"1": 2021}
        valid_records = {2019: 10, 2020: -8, 2021: 145, 2022: 5, 2023: 11, 2024: 1}
        expected_data = {2019: 10, 2020: -8, 2021: 145, 2022: 5, 2023: 11, 2024: 1}

        mock_get_valid_year_records.return_value = valid_records

        metric_data = self.report_instance.get_records_by_invest_year(
            company, companies_dict
        )

        self.assertEqual(metric_data, expected_data)

    def test_sort_metric_values(self):
        metric_values = {
            "2021": 15,
            "2023": 10,
            "2018": 11,
            "2020": 20,
            "2019": 24,
            "2022": 23,
        }
        expected_metrics = OrderedDict(
            [(2018, 11), (2019, 24), (2020, 20), (2021, 15), (2022, 23), (2023, 10)]
        )

        metrics_sorted = self.report_instance.sort_metric_values(metric_values)

        self.assertEqual(metrics_sorted, expected_metrics)

    @mock.patch(
        "src.service.investment_date_report.investment_date_report."
        "InvestmentDateReport.get_by_metric_records"
    )
    def test_join_company_metrics(self, mock_get_by_metric_records):
        years = [2019, 2020, 2021, 2022, 2023, 2024]
        companies_dict = {"1": 2021}
        expected_data = {
            "1": {
                "id": "1",
                "name": "Test",
                "metrics": [
                    {
                        "metric_name": "growth",
                        2019: 10,
                        2020: -8,
                        2021: 145,
                        2022: 5,
                        2023: 11,
                        2024: 1,
                    },
                    {
                        "metric_name": "ebitda_margin",
                        2019: 10,
                        2020: -8,
                        2021: 145,
                        2022: 5,
                        2023: 11,
                        2024: 1,
                    },
                ],
            }
        }
        mock_get_by_metric_records.side_effect = get_data
        company_metrics = self.report_instance.join_company_metrics(
            ["growth", "ebitda_margin"], years, True, companies_dict
        )
        self.assertEqual(company_metrics, expected_data)

    @mock.patch(
        "src.service.investment_date_report.investment_date_report."
        "InvestmentDateReport.join_company_metrics"
    )
    def test_get_companies(self, mock_join_company_metrics):
        investments_companies = {"1": {"id": "1", "name": "Test", "invest_year": 2021}}
        data = {
            "id": "1",
            "name": "Test",
            "metrics": [
                {
                    "metric_name": "growth",
                    "2019": "NA",
                    "2020": -8,
                    "2021": 145,
                    "2022": "NA",
                    "2023": "NA",
                    "2024": "NA",
                }
            ],
        }

        self.mock_repository.get_investments.return_value = investments_companies
        mock_join_company_metrics.return_value = data

        expected_data = {
            "id": "1",
            "name": "Test",
            "metrics": [
                {
                    "metric_name": "growth",
                    "2019": "NA",
                    "2020": -8,
                    "2021": 145,
                    "2022": "NA",
                    "2023": "NA",
                    "2024": "NA",
                }
            ],
        }

        companies_data = self.report_instance.get_companies(["growth"], True)

        self.assertEqual(companies_data, expected_data)

    @mock.patch(
        "src.service.investment_date_report.investment_date_report."
        "InvestmentDateReport.get_companies"
    )
    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    def test_get_peers_by_investment_date_report_from_main(
        self, mock_set_company_permissions, mock_get_companies
    ):
        data = {
            "1": {
                "id": "821603b7-0263-4c47-83b3-00b41665faaa",
                "name": "Boxlight Corp",
                "metrics": [
                    {
                        "metric_name": "growth",
                        "2019": "NA",
                        "2020": -8,
                        "2021": 145,
                        "2022": "NA",
                        "2023": "NA",
                        "2024": "NA",
                    },
                    {
                        "metric_name": "actuals_revenue",
                        "2019": 37,
                        "2020": 34,
                        "2021": 83,
                        "2022": "NA",
                        "2023": "NA",
                        "2024": "NA",
                    },
                ],
            }
        }
        mock_get_companies.return_value = data
        self.mock_metric_report_instance.sort_peers.return_value = [*data.values()]

        peers = self.report_instance.get_peers_by_investment_date_report(
            None, "user@test.com", ["growth", "actuals_revenue"], True, True
        )

        self.assertEqual(
            peers,
            {
                "headers": self.headers,
                "company_comparison_data": {},
                "peers_comparison_data": [*data.values()],
            },
        )
        mock_set_company_permissions.assert_called()

    @mock.patch(
        "src.service.investment_date_report.investment_date_report."
        "InvestmentDateReport.get_companies"
    )
    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    def test_get_peers_by_investment_date_report_not_from_main(
        self, mock_set_company_permissions, mock_get_companies
    ):
        data = {
            "1": {
                "id": "1",
                "name": "Boxlight Corp",
                "metrics": [
                    {
                        "metric_name": "growth",
                        "2019": "NA",
                        "2020": -8,
                        "2021": 145,
                        "2022": "NA",
                        "2023": "NA",
                        "2024": "NA",
                    },
                    {
                        "metric_name": "actuals_revenue",
                        "2019": 37,
                        "2020": 34,
                        "2021": 83,
                        "2022": "NA",
                        "2023": "NA",
                        "2024": "NA",
                    },
                ],
            },
            "2": {
                "id": "2",
                "name": "Test",
                "metrics": [
                    {
                        "metric_name": "growth",
                        "2019": "NA",
                        "2020": -8,
                        "2021": 145,
                        "2022": "NA",
                        "2023": "NA",
                        "2024": "NA",
                    },
                    {
                        "metric_name": "actuals_revenue",
                        "2019": 37,
                        "2020": 34,
                        "2021": 83,
                        "2022": "NA",
                        "2023": "NA",
                        "2024": "NA",
                    },
                ],
            },
        }
        company_data = data.copy()

        mock_get_companies.return_value = company_data
        self.mock_metric_report_instance.sort_peers.return_value = [company_data["1"]]

        peers = self.report_instance.get_peers_by_investment_date_report(
            "2", "user@test.com", ["growth", "actuals_revenue"], False, True
        )

        self.assertEqual(
            peers,
            {
                "headers": self.headers,
                "company_comparison_data": data["2"],
                "peers_comparison_data": [data["1"]],
            },
        )
        mock_set_company_permissions.assert_called()

    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    def test_get_peers_by_investment_date_report_should_fail(
        self, mock_set_company_permissions
    ):
        mock_set_company_permissions.side_effect = Exception("error")

        with self.assertRaises(Exception) as context:
            self.report_instance.get_peers_by_investment_date_report(
                None, "user@test.com", ["actuals_revenue"], True, True
            )

        self.assertEqual(str(context.exception), "error")
