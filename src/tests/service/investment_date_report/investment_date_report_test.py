import logging
from unittest.mock import Mock
from unittest import TestCase, mock

from src.utils.company_anonymization import CompanyAnonymization
from src.service.calculator.calculator_service import CalculatorService
from src.service.investment_date_report.investment_date_report import (
    InvestmentDateReport,
)


logger = logging.getLogger()
logger.setLevel(logging.ERROR)
size_range = {"label": "$30-<50 million", "max_value": 50, "min_value": 30}


def get_data(metric: str, years: list, companies: dict, **conditions):
    years_data = {2020: -8, 2021: 145}
    metrics = {"metric_name": metric}
    metrics.update({year: years_data.get(year, "NA") for year in years})
    return {"1": {"id": "1", "name": "Test", "metrics": metrics}}


def anonymized_metric(metrics: dict, ranges: list) -> dict:
    years_data = {2020: ">$20 million", 2021: "$40 million +"}
    return {year: years_data.get(year, "NA") for year in metrics}


class TestInvestmentDateReport(TestCase):
    def setUp(self):
        self.mock_repository = Mock()
        self.mock_profile_range = Mock()
        self.mock_metric_repository = Mock()
        self.calculator = CalculatorService(logger)
        self.mock_metric_report = Mock()
        self.company_anonymization = CompanyAnonymization(object)
        self.report_instance = InvestmentDateReport(
            logger,
            self.calculator,
            self.mock_repository,
            self.mock_metric_repository,
            self.mock_metric_report,
            self.mock_profile_range,
            self.company_anonymization,
        )
        self.years = [2019, 2020, 2021, 2022, 2023, 2024]
        self.company_data = {
            "id": "1",
            "name": "Test",
            "metrics": [
                {
                    "metric_name": "growth",
                    2019: "NA",
                    2020: -8,
                    2021: 145,
                    2022: "NA",
                    2023: "NA",
                    2024: "NA",
                }
            ],
        }
        self.companies = [
            self.company_data.copy(),
            {
                "id": "2",
                "name": "Company",
                "metrics": [
                    {
                        "metric_name": "growth",
                        "2020": 34,
                        "2021": 83,
                        "2022": "NA",
                    }
                ],
            },
        ]
        self.records = [
            {"id": "1", "name": "Test", "year": 2020, "value": -8},
            {"id": "1", "name": "Test", "year": 2021, "value": 145},
            {"id": "1", "name": "Test", "year": 2022, "value": None},
        ]
        self.sizes = [
            {"label": ">$20 million", "min_value": None, "max_value": 20},
            {"label": "$20 million - $40 million", "min_value": 20, "max_value": 40},
            {"label": "$40 million +", "min_value": 40, "max_value": None},
        ]

    def test_get_valid_year_records_with_no_empty_values_should_return_years_merged(
        self,
    ):
        company = {
            "id": "1",
            "name": "Test",
            "metrics": {2020: 3},
        }
        years = self.years
        expected_records_by_year = {
            2019: "NA",
            2020: 3,
            2021: "NA",
            2022: "NA",
            2023: "NA",
            2024: "NA",
        }

        metric_year_data = self.report_instance.get_valid_year_records(company, years)

        self.assertEqual(metric_year_data, expected_records_by_year)

    def test_get_by_metrics_records_with_investment_records_should_return_companies_dict_data(
        self,
    ):
        company_metric = self.company_data.copy()
        company_metric = {"id": "1", "name": "Test", "metrics": {2020: -8, 2021: 145}}
        metric_records = {"1": company_metric}
        self.mock_metric_repository.add_filters.return_value = {}
        self.mock_metric_report.get_records.return_value = metric_records
        self.mock_metric_report.get_profiles.return_value = {}
        self.mock_metric_report.is_in_range.return_value = True
        self.mock_repository.get_years.return_value = self.years

        metric_data = self.report_instance.get_by_metric_records(
            "actuals_revenue", [2020, 2021, 2022], {"1": 2021}
        )

        self.assertEqual(
            metric_data,
            {
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
                        "metric_name": "actuals_revenue",
                    },
                }
            },
        )

    @mock.patch(
        "src.service.investment_date_report.investment_date_report."
        "InvestmentDateReport.get_by_metric_records"
    )
    def test_join_company_metrics_when_is_sucessful_should_return_list_with_two_metrics_dict(
        self, mock_get_by_metric_records
    ):
        years = [2019, 2020, 2021, 2022, 2023, 2024]
        companies_dict = {"1": 2021}
        company_metrics_data = self.company_data.copy()
        company_metrics_data["metrics"].append(
            {
                "metric_name": "ebitda_margin",
                2019: "NA",
                2020: -8,
                2021: 145,
                2022: "NA",
                2023: "NA",
                2024: "NA",
            }
        )
        expected_companies_metrics_data = {"1": company_metrics_data}
        mock_get_by_metric_records.side_effect = get_data

        company_joined_metrics = self.report_instance.join_company_metrics(
            ["growth", "ebitda_margin"], years, companies_dict
        )

        self.assertEqual(company_joined_metrics, expected_companies_metrics_data)

    def test_get_companies_data_when_is_sucessful_should_return_metrics_merged(self):
        self.mock_repository.get_investments.return_value = {
            "1": {"id": "1", "name": "Test", "invest_year": 2021}
        }
        self.mock_repository.get_years.return_value = self.years
        company_metric = {"id": "1", "name": "Test", "metrics": {2020: -8, 2021: 145}}
        metric_records = {"1": company_metric}
        self.mock_metric_report.get_records.return_value = metric_records
        expected_companies_metrics_data = {"1": self.company_data.copy()}

        companies_data = self.report_instance.get_companies_data(["growth"])

        self.assertEqual(companies_data, expected_companies_metrics_data)

    def get_company_data_with_different_metric(self, metric_name: str) -> dict:
        return {
            "id": "1",
            "name": "Test",
            "metrics": [
                {
                    "metric_name": metric_name,
                    2019: "NA",
                    2020: -8,
                    2021: 145,
                    2022: "NA",
                    2023: "NA",
                    2024: "NA",
                }
            ],
        }

    def test_anonymize_companies_data_with_input_metric_should_change_metric_values(
        self,
    ):
        companies_data = {
            "1": self.get_company_data_with_different_metric("actuals_revenue")
        }
        self.company_anonymization.companies = []
        self.mock_profile_range.get_profile_ranges.return_value = self.sizes
        self.mock_metric_report.anonymized_name.side_effect = (
            lambda company_id: company_id[0:4] + "-xxxx"
        )
        self.mock_metric_report.clear_metric_name.return_value = "revenue"
        self.mock_metric_report.anonymized_metric.side_effect = anonymized_metric
        expected_anonymized_companies_data = {
            "1": {
                "id": "1",
                "name": "1-xxxx",
                "metrics": [
                    {
                        2019: "NA",
                        2020: ">$20 million",
                        2021: "$40 million +",
                        2022: "NA",
                        2023: "NA",
                        2024: "NA",
                        "metric_name": "actuals_revenue",
                    }
                ],
            }
        }

        self.report_instance.anonymize_companies_data(
            companies_data, ["actuals_revenue"]
        )

        self.assertEqual(companies_data, expected_anonymized_companies_data)

    def test_anonymize_companies_data_with_calculated_metric_should_not_change_metric_values(
        self,
    ):
        companies_data = {"1": self.get_company_data_with_different_metric("growth")}
        self.company_anonymization.companies = []
        self.mock_profile_range.get_profile_ranges.return_value = self.sizes
        self.mock_metric_report.anonymized_name.side_effect = (
            lambda company_id: company_id[0:4] + "-xxxx"
        )
        self.mock_metric_report.clear_metric_name.return_value = "growth"
        self.mock_metric_report.anonymized_metric.side_effect = anonymized_metric
        expected_anonymized_companies_data = {
            "1": {
                "id": "1",
                "name": "1-xxxx",
                "metrics": [
                    {
                        2019: "NA",
                        2020: -8,
                        2021: 145,
                        2022: "NA",
                        2023: "NA",
                        2024: "NA",
                        "metric_name": "growth",
                    }
                ],
            }
        }

        self.report_instance.anonymize_companies_data(companies_data, ["growth"])

        self.assertEqual(companies_data, expected_anonymized_companies_data)

    def test_anonymize_companies_data_without_data_should_change_metric_values_to_empty_list(
        self,
    ):
        companies_data = {
            "1": {
                "id": "1",
                "name": "Test",
                "metrics": [],
            }
        }
        self.company_anonymization.companies = []
        self.mock_profile_range.get_profile_ranges.return_value = self.sizes
        self.mock_metric_report.anonymized_name.side_effect = (
            lambda company_id: company_id[0:4] + "-xxxx"
        )
        expected_anonymized_companies_data = {
            "1": {"id": "1", "name": "1-xxxx", "metrics": []}
        }

        self.report_instance.anonymize_companies_data(companies_data, ["growth"])

        self.assertEqual(companies_data, expected_anonymized_companies_data)

    @mock.patch(
        "src.service.investment_date_report.investment_date_report."
        "InvestmentDateReport.get_companies_data"
    )
    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    def test_get_peers_by_investment_date_report_from_universe_overview_should_return_empty_company(
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
        self.mock_metric_report.sort_peers.return_value = [*data.values()]

        peers = self.report_instance.get_peers_by_investment_date_report(
            None, "user@test.com", ["growth", "actuals_revenue"], True, True
        )

        self.assertEqual(
            peers,
            {
                "headers": self.report_instance.headers,
                "company_comparison_data": {},
                "peers_comparison_data": [*data.values()],
            },
        )
        mock_set_company_permissions.assert_called()

    @mock.patch(
        "src.service.investment_date_report.investment_date_report."
        "InvestmentDateReport.get_companies_data"
    )
    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    def test_get_peers_by_investment_date_report_from_company_report_return_company_dict(
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
        self.mock_metric_report.sort_peers.return_value = [company_data["1"]]

        peers = self.report_instance.get_peers_by_investment_date_report(
            "2", "user@test.com", ["growth", "actuals_revenue"], False, True
        )

        self.assertEqual(
            peers,
            {
                "headers": self.report_instance.headers,
                "company_comparison_data": data["2"],
                "peers_comparison_data": [data["1"]],
            },
        )
        mock_set_company_permissions.assert_called()

    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    def test_get_peers_by_investment_date_report_when_services_fail_should_raise_exception(
        self, mock_set_company_permissions
    ):
        mock_set_company_permissions.side_effect = Exception("error")

        with self.assertRaises(Exception) as context:
            self.report_instance.get_peers_by_investment_date_report(
                None, "user@test.com", ["actuals_revenue"], True, True
            )

        self.assertEqual(str(context.exception), "error")

    @mock.patch(
        "src.service.investment_date_report.investment_date_report."
        "InvestmentDateReport.get_companies_data"
    )
    @mock.patch(
        "src.service.investment_date_report.investment_date_report."
        "InvestmentDateReport.anonymize_companies_data"
    )
    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    def test_get_peers_by_report_without_permissions_and_metric_to_anonymize_call_anonymize_func(
        self,
        mock_set_company_permissions,
        mock_anonymize_companies_data,
        mock_get_companies_data,
    ):
        mock_get_companies_data.return_value = {}
        self.mock_metric_report.clear_metric_name.return_value = "revenue"

        self.report_instance.get_peers_by_investment_date_report(
            None, "user@test.com", ["actuals_revenue"], True, False
        )

        mock_anonymize_companies_data.assert_called()
        mock_set_company_permissions.assert_called()
