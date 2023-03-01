import logging
from unittest.mock import Mock
from unittest import TestCase, mock
from parameterized import parameterized

from src.service.quarters_report.quarters_report import QuartersReport
from src.utils.company_anonymization import CompanyAnonymization
from src.service.calculator.calculator_service import CalculatorService

logger = logging.getLogger()
logger.setLevel(logging.INFO)
size_range = {"label": "$30-<50 million", "max_value": 50, "min_value": 30}


class TestQuartersReport(TestCase):
    def setUp(self):
        self.mock_repository = Mock()
        self.mock_profile_range = Mock()
        self.company_anonymization = CompanyAnonymization(object)
        self.calculator = CalculatorService(logger)
        self.report_instance = QuartersReport(
            logger,
            self.calculator,
            self.mock_repository,
            self.mock_profile_range,
            self.company_anonymization,
        )
        self.records = [
            {
                "id": "1",
                "name": "Test",
                "scenario": "Actuals-2020",
                "metric": "Revenue",
                "year": 2020,
                "value": 20,
                "period_name": "Q1",
                "average": 2,
                "full_year_average": 3,
                "full_year": 0,
                "count_periods": 2,
            },
            {
                "id": "2",
                "name": "Company",
                "scenario": "Actuals-2021",
                "metric": "Revenue",
                "year": 2021,
                "value": 22,
                "period_name": "Q2",
                "average": 9,
                "full_year_average": 2,
                "full_year": 1,
                "count_periods": 4,
            },
        ]
        self.sizes = [
            {"label": ">$20 million", "min_value": None, "max_value": 20},
            {"label": "$20 million - $40 million", "min_value": 20, "max_value": 40},
            {"label": "$40 million +", "min_value": 40, "max_value": None},
        ]
        self.quarters_records = [
            {
                "id": "1",
                "name": "Test",
                "scenario": "Budget-2020",
                "metric": "Revenue",
                "year": 2020,
                "value": 20,
                "period_name": "Q2",
                "average": 2,
                "full_year_average": 3,
                "full_year": 0,
                "count_periods": 2,
            },
            {
                "id": "1",
                "name": "Test",
                "scenario": "Budget-2020",
                "metric": "Revenue",
                "year": 2020,
                "value": 20,
                "period_name": "Q3",
                "average": 2,
                "full_year_average": 3,
                "full_year": 0,
                "count_periods": 2,
            },
            {
                "id": "1",
                "name": "Test",
                "scenario": "Budget-2020",
                "metric": "Revenue",
                "year": 2020,
                "value": 20,
                "period_name": "Q4",
                "average": 2,
                "full_year_average": 3,
                "full_year": 0,
                "count_periods": 2,
            },
        ]
        self.response = {
            "headers": [
                "Company",
                "2020",
                "",
                "",
                "",
                "",
                "2021",
                "",
                "",
                "",
                "",
                "",
            ],
            "subheaders": [
                "",
                "Q1",
                "Q2",
                "Q3",
                "Q4",
                "Full Year",
                "Q1",
                "Q2",
                "Q3",
                "Q4",
                "Full Year",
                "vs",
            ],
            "company_comparison_data": {
                "id": "1",
                "name": "Test",
                "quarters": [
                    {
                        "year": "2020",
                        "Q1": 20.0,
                        "Q2": "NA",
                        "Q3": 20.0,
                        "Q4": "NA",
                        "Full Year": "NA",
                    },
                    {
                        "year": "2021",
                        "Q1": "NA",
                        "Q2": "NA",
                        "Q3": "NA",
                        "Q4": "NA",
                        "Full Year": "NA",
                        "vs": "NA",
                    },
                ],
            },
            "peers_comparison_data": [
                {
                    "id": "2",
                    "name": "Company",
                    "quarters": [
                        {
                            "year": "2020",
                            "Q1": "NA",
                            "Q2": "NA",
                            "Q3": "NA",
                            "Q4": "NA",
                            "Full Year": "NA",
                        },
                        {
                            "year": "2021",
                            "Q1": "NA",
                            "Q2": 22.0,
                            "Q3": "NA",
                            "Q4": "NA",
                            "Full Year": "NA",
                            "vs": "NA",
                        },
                    ],
                }
            ],
            "averages": [
                {"Q1": 20.0},
                {"Q2": "NA"},
                {"Q3": 20.0},
                {"Q4": "NA"},
                {"Full Year": "NA"},
                {"Q1": "NA"},
                {"Q2": 22.0},
                {"Q3": "NA"},
                {"Q4": "NA"},
                {"Full Year": "NA"},
                {"vs": "NA"},
            ],
        }

    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    def test_get_quarters_peers_with_base_scenario_when_is_sucessful_should_return_quarters_report(
        self, mock_set_company_permissions
    ):
        records = self.records.copy()
        records.append(
            {
                "id": "1",
                "name": "Test",
                "scenario": "Actuals-2020",
                "metric": "Revenue",
                "year": 2020,
                "value": 20,
                "period_name": "Q3",
                "average": 2,
                "full_year_average": 3,
                "full_year": 0,
                "count_periods": 2,
            },
        )
        self.mock_repository.get_metric_records_by_quarters.return_value = records
        self.mock_repository.get_functions_metric.return_value = {"actuals-revenue": {}}
        expected_response = {
            "headers": self.response.get("headers"),
            "subheaders": self.response.get("subheaders"),
            "company_comparison_data": {
                "id": "1",
                "name": "Test",
                "quarters": [
                    {
                        "year": 2020,
                        "Q1": 20.0,
                        "Q2": "NA",
                        "Q3": 20.0,
                        "Q4": "NA",
                        "Full Year": "NA",
                    },
                    {
                        "year": 2021,
                        "Q1": "NA",
                        "Q2": "NA",
                        "Q3": "NA",
                        "Q4": "NA",
                        "Full Year": "NA",
                        "vs": "NA",
                    },
                ],
            },
            "peers_comparison_data": [
                {
                    "id": "2",
                    "name": "Company",
                    "quarters": [
                        {
                            "year": 2020,
                            "Q1": "NA",
                            "Q2": "NA",
                            "Q3": "NA",
                            "Q4": "NA",
                            "Full Year": "NA",
                        },
                        {
                            "year": 2021,
                            "Q1": "NA",
                            "Q2": 22.0,
                            "Q3": "NA",
                            "Q4": "NA",
                            "Full Year": "NA",
                            "vs": "NA",
                        },
                    ],
                }
            ],
            "averages": [
                {"Q1": 2.0},
                {"Q2": "NA"},
                {"Q3": 2.0},
                {"Q4": "NA"},
                {"Full Year": 3.0},
                {"Q1": "NA"},
                {"Q2": 9.0},
                {"Q3": "NA"},
                {"Q4": "NA"},
                {"Full Year": 2.0},
                {"vs": "NA"},
            ],
        }

        peers = self.report_instance.get_quarters_peers(
            "1",
            "user",
            "year_to_year",
            "revenue",
            "actuals",
            ["2020", "2021"],
            None,
            False,
            True,
        )

        mock_set_company_permissions.assert_called()
        self.assertEqual(peers, expected_response)

    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    @mock.patch(
        "src.service.quarters_report.quarters_report.QuartersReport.anonymize_companies_values"
    )
    def test_get_quarters_peers_without_permission_when_is_sucessful_should_return_quarters_report(
        self, mock_anonymize_companies_values, mock_set_company_permissions
    ):
        self.mock_repository.get_metric_records_by_quarters.return_value = self.records
        self.mock_repository.get_functions_metric.return_value = {"actuals-revenue": {}}

        self.report_instance.get_quarters_peers(
            "1",
            "user",
            "year_to_year",
            "revenue",
            "actuals",
            ["2020", "2021"],
            None,
            False,
            False,
        )

        mock_set_company_permissions.assert_called()
        mock_anonymize_companies_values.assert_called()

    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    def test_get_quarters_peers_with_actuals_plus_budget_scenario_should_return_quarters_report(
        self, mock_set_company_permissions
    ):
        records = self.records.copy()
        records.append(
            {
                "id": "1",
                "name": "Test",
                "scenario": "Budget-2020",
                "metric": "Revenue",
                "year": 2020,
                "value": None,
                "period_name": "Q3",
                "average": 2,
                "full_year_average": 3,
                "full_year": 0,
                "count_periods": 2,
            },
        )
        expected_value = self.response.copy()
        expected_value["company_comparison_data"]["quarters"][0]["Q3"] = "NA"

        expected_value["averages"][2]["Q3"] = "NA"
        self.mock_repository.get_quarters_year_to_year_records.return_value = records
        self.mock_repository.get_functions_metric.return_value = {"actuals-revenue": {}}

        peers = self.report_instance.get_quarters_peers(
            "1",
            "user",
            "year_to_year",
            "revenue",
            "actuals_budget",
            ["2020", "2021"],
            "Q3",
            False,
            True,
        )

        mock_set_company_permissions.assert_called()
        self.assertEqual(peers, expected_value)

    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    def test_get_quarters_peers_with_base_scenario_LTM_should_return_quarters_report(
        self, mock_set_company_permissions
    ):
        self.mock_repository.get_metric_records_by_quarters.return_value = self.records
        self.mock_repository.get_functions_metric.return_value = {"actuals-revenue": {}}
        records = self.records.copy()
        records.extend(
            [
                {
                    "id": "2",
                    "name": "Test",
                    "scenario": "Actuals-2020",
                    "metric": "Revenue",
                    "year": 2020,
                    "value": None,
                    "period_name": "Q2",
                    "average": 2,
                    "full_year_average": 3,
                    "full_year": 0,
                    "count_periods": 3,
                },
                {
                    "id": "2",
                    "name": "Test",
                    "scenario": "Actuals-2020",
                    "metric": "Revenue",
                    "year": 2020,
                    "value": None,
                    "period_name": "Q3",
                    "average": 2,
                    "full_year_average": 3,
                    "full_year": 0,
                    "count_periods": 3,
                },
                {
                    "id": "2",
                    "name": "Test",
                    "scenario": "Actuals-2020",
                    "metric": "Revenue",
                    "year": 2020,
                    "value": None,
                    "period_name": "Q4",
                    "average": 2,
                    "full_year_average": 3,
                    "full_year": 0,
                    "count_periods": 3,
                },
            ]
        )
        expected_value = {
            "headers": [
                "Company",
                "2019",
                "",
                "",
                "2020",
                "",
                "",
                "",
                "",
                "2021",
                "",
                "",
            ],
            "subheaders": [
                "",
                "Q2",
                "Q3",
                "Q4",
                "Q1",
                "Full Year",
                "Q2",
                "Q3",
                "Q4",
                "Q1",
                "Full Year",
                "vs",
            ],
            "company_comparison_data": {
                "id": "1",
                "name": "Test",
                "quarters": [
                    {"Q2": "NA", "Q3": "NA", "Q4": "NA", "year": "2019"},
                    {
                        "Q1": 20.0,
                        "Q2": "NA",
                        "Q3": "NA",
                        "Q4": "NA",
                        "Full Year": "NA",
                        "year": "2020",
                    },
                    {"Q1": "NA", "Full Year": "NA", "vs": "NA", "year": "2021"},
                ],
            },
            "peers_comparison_data": [
                {
                    "id": "2",
                    "name": "Company",
                    "quarters": [
                        {
                            "Q2": "NA",
                            "Q3": "NA",
                            "Q4": "NA",
                            "year": "2019",
                        },
                        {
                            "Q1": "NA",
                            "Q2": "NA",
                            "Q3": "NA",
                            "Q4": "NA",
                            "Full Year": "NA",
                            "year": "2020",
                        },
                        {
                            "Q1": "NA",
                            "Full Year": "NA",
                            "vs": "NA",
                            "year": "2021",
                        },
                    ],
                }
            ],
            "averages": [
                {"Q2": "NA"},
                {"Q3": "NA"},
                {"Q4": "NA"},
                {"Q1": 2.0},
                {"Full Year": "NA"},
                {"Q2": "NA"},
                {"Q3": "NA"},
                {"Q4": "NA"},
                {"Q1": "NA"},
                {"Full Year": "NA"},
                {"vs": "NA"},
            ],
        }
        self.mock_repository.get_metric_records_by_quarters.return_value = self.records

        peers = self.report_instance.get_quarters_peers(
            "1",
            "user",
            "last_twelve_months",
            "revenue",
            "actuals",
            ["2020", "2021"],
            None,
            False,
            True,
        )

        mock_set_company_permissions.assert_called()
        self.assertEqual(peers, expected_value)

    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    def test_get_quarters_peers_actuals_plus_budget_with_full_year_should_return_quarters_report(
        self, mock_set_company_permissions
    ):
        records = self.records.copy()
        records.extend(self.quarters_records)
        self.mock_repository.get_quarters_year_to_year_records.return_value = records
        self.mock_repository.get_functions_metric.return_value = {"actuals-revenue": {}}
        expected_response = {
            "headers": self.response.get("headers"),
            "subheaders": self.response.get("subheaders"),
            "company_comparison_data": {
                "id": "1",
                "name": "Test",
                "quarters": [
                    {
                        "year": "2020",
                        "Q1": 20.0,
                        "Q2": 20.0,
                        "Q3": 20.0,
                        "Q4": 20.0,
                        "Full Year": 80.0,
                    },
                    self.response.get("company_comparison_data").get("quarters")[1],
                ],
            },
            "peers_comparison_data": [
                {
                    "id": "2",
                    "name": "Company",
                    "quarters": [
                        {
                            "year": "2020",
                            "Q1": "NA",
                            "Q2": "NA",
                            "Q3": "NA",
                            "Q4": "NA",
                            "Full Year": "NA",
                        },
                        {
                            "year": "2021",
                            "Q1": "NA",
                            "Q2": 22.0,
                            "Q3": "NA",
                            "Q4": "NA",
                            "Full Year": "NA",
                            "vs": "NA",
                        },
                    ],
                }
            ],
            "averages": [
                {"Q1": 20.0},
                {"Q2": 20.0},
                {"Q3": 20.0},
                {"Q4": 20.0},
                {"Full Year": 80.0},
                {"Q1": "NA"},
                {"Q2": 22.0},
                {"Q3": "NA"},
                {"Q4": "NA"},
                {"Full Year": "NA"},
                {"vs": "NA"},
            ],
        }

        peers = self.report_instance.get_quarters_peers(
            "1",
            "user",
            "year_to_year",
            "revenue",
            "actuals_budget",
            ["2020", "2021"],
            None,
            False,
            True,
        )
        mock_set_company_permissions.assert_called()
        self.assertEqual(peers, expected_response)

    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    def test_get_quarters_peers_actuals_budget_YTD_with_full_year_should_return_quarters_report(
        self, mock_set_company_permissions
    ):
        records = self.records.copy()
        records.extend(self.quarters_records)
        self.mock_repository.get_quarters_year_to_year_records.return_value = records
        self.mock_repository.get_functions_metric.return_value = {"actuals-revenue": {}}
        expected_data = self.response
        expected_data["averages"][1]["Full Year"] = 22.0
        expected_response = {
            "headers": expected_data.get("headers"),
            "subheaders": expected_data.get("subheaders"),
            "company_comparison_data": {
                "id": "1",
                "name": "Test",
                "quarters": [
                    {
                        "year": "2020",
                        "Q1": 20.0,
                        "Q2": 20.0,
                        "Q3": 20.0,
                        "Q4": 20.0,
                        "Full Year": 80.0,
                    },
                    expected_data.get("company_comparison_data").get("quarters")[1],
                ],
            },
            "peers_comparison_data": [
                {
                    "id": "2",
                    "name": "Company",
                    "quarters": [
                        {
                            "year": "2020",
                            "Q1": "NA",
                            "Q2": "NA",
                            "Q3": "NA",
                            "Q4": "NA",
                            "Full Year": "NA",
                        },
                        {
                            "year": "2021",
                            "Q1": "NA",
                            "Q2": 22.0,
                            "Q3": "NA",
                            "Q4": "NA",
                            "Full Year": 22.0,
                            "vs": "NA",
                        },
                    ],
                }
            ],
            "averages": [
                {"Q1": 20.0},
                {"Q2": 20.0},
                {"Q3": 20.0},
                {"Q4": 20.0},
                {"Full Year": 80.0},
                {"Q1": "NA"},
                {"Q2": 22.0},
                {"Q3": "NA"},
                {"Q4": "NA"},
                {"Full Year": 22.0},
                {"vs": "NA"},
            ],
        }

        peers = self.report_instance.get_quarters_peers(
            "1",
            "user",
            "year_to_date",
            "revenue",
            "actuals_budget",
            ["2020", "2021"],
            "Q3",
            False,
            True,
        )

        mock_set_company_permissions.assert_called()
        self.assertEqual(peers, expected_response)

    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    def test_get_quarters_peers_when_call_fails_should_raise_an_exception(
        self, mock_set_company_permissions
    ):
        mock_set_company_permissions.side_effect = Exception("error")

        with self.assertRaises(Exception) as context:
            self.report_instance.get_quarters_peers(
                "1",
                "user",
                "year_year",
                "revenue",
                "actuals",
                ["2020", "2021"],
                None,
                False,
                True,
            )

        self.assertEqual(str(context.exception), "error")

    def test_anonymize_companies_values_when_is_successful_change_name_and_quarters_values(
        self,
    ):
        anonymized_data = [
            {
                "id": "123",
                "name": "123-xxxx",
                "quarters": [
                    {
                        "year": 2021,
                        "Q1": "$20 million - $40 million",
                        "Q2": "$20 million - $40 million",
                        "Q3": "$20 million - $40 million",
                        "Q4": "$20 million - $40 million",
                        "Full Year": "$20 million - $40 million",
                    }
                ],
            }
        ]
        self.mock_profile_range.get_range_from_value.return_value = (
            "$20 million - $40 million"
        )
        companies_data = [
            {
                "id": "123",
                "name": "Company A",
                "quarters": [
                    {"year": 2021, "Q1": 2, "Q2": 2, "Q3": 3, "Q4": 3, "Full Year": 10}
                ],
            }
        ]

        self.report_instance.anonymize_companies_values("revenue", companies_data)

        self.assertEqual(companies_data, anonymized_data)
        self.mock_profile_range.get_range_from_value.assert_called()

    @parameterized.expand(
        [
            [
                1,
                [
                    {"year": "2020", "Full Year": 12.1},
                    {"year": "2021", "Full Year": 4.3},
                    {"year": "2022", "Full Year": 5.3},
                ],
                36.0,
            ],
            [
                2,
                [
                    {"year": "2020", "Full Year": 0},
                    {"year": "2021", "Full Year": 0},
                    {"year": "2022", "Full Year": 5.3},
                ],
                "NA",
            ],
        ]
    )
    def test__get_comparison_percentage(self, index, quarters, percentage):
        comparison_percentage = (
            self.report_instance._QuartersReport__get_comparison_percentage(
                index, quarters
            )
        )

        self.assertEqual(comparison_percentage, percentage)

    @parameterized.expand(
        [
            [[2, 3.1, 5, 23], 8],
            [[13, 6], 9],
        ]
    )
    def test__calculate_average(self, values, expected_average):
        calculated_averages = self.report_instance._QuartersReport__calculate_average(
            values
        )

        self.assertEqual(calculated_averages, expected_average)

    def test_filter_companies_should_return_filtered_companies(self):
        years = [2021]
        companies = [{"id": 1, "quarters": [{"year": 2021}]}]

        filtered_companies = self.report_instance.filter_companies(companies, years)

        self.assertEqual(filtered_companies, companies)

    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    def test_add_vs_property_with_full_year_data_should_return_vs_property(
        self, mock_set_company_permissions
    ):
        records = self.records.copy()
        expected_value = [
            {
                "id": "1",
                "name": "Test",
                "quarters": [
                    {
                        "year": "2020",
                        "Q1": 20.0,
                        "Q2": 20.0,
                        "Q3": 20.0,
                        "Q4": 20.0,
                        "Full Year": 80.0,
                    },
                    {
                        "year": "2021",
                        "Q1": 20.0,
                        "Q2": 20.0,
                        "Q3": 20.0,
                        "Q4": 20.0,
                        "Full Year": 80.0,
                        "vs": 100.0,
                    },
                ],
            },
            {
                "id": "2",
                "name": "Company",
                "quarters": [
                    {
                        "year": "2021",
                        "Q1": "NA",
                        "Q2": 22.0,
                        "Q3": "NA",
                        "Q4": "NA",
                        "Full Year": "NA",
                        "vs": "NA",
                    }
                ],
            },
        ]
        records.append(
            {
                "id": "1",
                "name": "Test",
                "scenario": "Actuals-2020",
                "metric": "Revenue",
                "year": 2020,
                "value": 20,
                "period_name": "Q2",
            }
        )
        records.append(
            {
                "id": "1",
                "name": "Test",
                "scenario": "Actuals-2020",
                "metric": "Revenue",
                "year": 2020,
                "value": 20,
                "period_name": "Q3",
            }
        )
        records.append(
            {
                "id": "1",
                "name": "Test",
                "scenario": "Actuals-2020",
                "metric": "Revenue",
                "year": 2020,
                "value": 20,
                "period_name": "Q4",
            }
        )
        records.append(
            {
                "id": "1",
                "name": "Test",
                "scenario": "Actuals-2021",
                "metric": "Revenue",
                "year": 2021,
                "value": 20,
                "period_name": "Q1",
            }
        )
        records.append(
            {
                "id": "1",
                "name": "Test",
                "scenario": "Actuals-2021",
                "metric": "Revenue",
                "year": 2021,
                "value": 20,
                "period_name": "Q2",
            }
        )
        records.append(
            {
                "id": "1",
                "name": "Test",
                "scenario": "Actuals-2021",
                "metric": "Revenue",
                "year": 2021,
                "value": 20,
                "period_name": "Q3",
            }
        )
        records.append(
            {
                "id": "1",
                "name": "Test",
                "scenario": "Actuals-2021",
                "metric": "Revenue",
                "year": 2021,
                "value": 20,
                "period_name": "Q4",
            }
        )

        self.mock_repository.get_quarters_year_to_year_records.return_value = records

        peers = self.report_instance.add_vs_property(
            "year_to_year", "revenue", ["2020", "2021"], "Q3", {}
        )

        self.assertEqual(peers, expected_value)

    @parameterized.expand(
        [
            [["2021", "2022"], "Q1", ["2020", "2021", "2022"]],
            [["2021", "2022"], "Q4", ["2021", "2022"]],
        ]
    )
    def test_get_year_for_ltm(self, years, period, expected_years):
        yeras_for_ltm = self.report_instance.get_year_for_ltm(years, period)

        self.assertEqual(yeras_for_ltm, expected_years)

    @parameterized.expand(
        [
            [
                ["2020", "2021", "2022"],
                "Q1",
                {
                    "2020": ["Q2", "Q3", "Q4"],
                    "2021": ["Q1", "Full Year", "Q2", "Q3", "Q4"],
                    "2022": ["Q1", "Full Year", "vs"],
                },
            ],
            [
                ["2020", "2021", "2022", "2023"],
                "Q1",
                {
                    "2020": ["Q2", "Q3", "Q4"],
                    "2021": ["Q1", "Full Year", "Q2", "Q3", "Q4"],
                    "2022": ["Q1", "Full Year", "vs", "Q2", "Q3", "Q4"],
                    "2023": ["Q1", "Full Year", "vs"],
                },
            ],
        ]
    )
    def test_build_subheaders_dict(self, years, period, expected_subheaders):
        subheaders = self.report_instance.build_subheaders_dict(period, years)

        self.assertEqual(subheaders, expected_subheaders)

    def test__update_full_year_ltm(self):
        data = {
            "1": {
                "quarters": [
                    {
                        "year": 2023,
                    }
                ]
            }
        }
        full_year_dict = {"1": {"2023": [1, 2, 3, 4]}}
        years = ["2023"]
        subheaders_dict = {"2023": ["Q1"]}
        full_year_average_dict = (
            self.report_instance._QuartersReport__update_full_year_ltm(
                data, full_year_dict, years, subheaders_dict
            )
        )

        self.assertEqual(full_year_average_dict, {"2023": [10]})

    def test__get_ltm_full_year_base_scenarios(self):
        subheaders_dict = {"2020": ["Q1"], "2021": {"Q2", "Q3", "Q4", "Full Year"}}
        year = 2020
        period = "Q1"
        company_id = "1"
        company = {"value": 12}
        quarters_per_companies = {}
        expected_quarters_per_companies = {"1": {"2021": [12.0]}}

        self.report_instance._QuartersReport__get_ltm_full_year_base_scenarios(
            subheaders_dict,
            year,
            period,
            company_id,
            company,
            quarters_per_companies,
        )

        self.assertEqual(quarters_per_companies, expected_quarters_per_companies)

    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    def test_get_quarters_peers_with_growth_metric_when_is_sucessful_should_return_quarters_report(
        self, mock_set_company_permissions
    ):
        data = self.records.copy()
        data.append(
            {
                "id": "2",
                "name": "Company",
                "scenario": "Actuals-2020",
                "metric": "Revenue",
                "year": 2020,
                "value": 44,
                "period_name": "Q2",
                "average": 9,
                "full_year_average": 2,
                "full_year": 1,
                "count_periods": 4,
            }
        )
        self.mock_repository.get_metric_records_with_base_scenarios.return_value = data
        self.mock_repository.get_functions_metric.return_value = {"actuals-revenue": {}}
        expected_value = {
            "headers": ["Company", "2020", "", "", "", "", "2021", "", "", "", "", ""],
            "subheaders": [
                "",
                "Q1",
                "Q2",
                "Q3",
                "Q4",
                "Full Year",
                "Q1",
                "Q2",
                "Q3",
                "Q4",
                "Full Year",
                "vs",
            ],
            "company_comparison_data": {
                "id": "1",
                "name": "Test",
                "quarters": [
                    {
                        "year": 2020,
                        "Q1": "NA",
                        "Q2": "NA",
                        "Q3": "NA",
                        "Q4": "NA",
                        "Full Year": "NA",
                    },
                    {
                        "year": 2021,
                        "Q1": "NA",
                        "Q2": "NA",
                        "Q3": "NA",
                        "Q4": "NA",
                        "Full Year": "NA",
                        "vs": "NA",
                    },
                ],
            },
            "peers_comparison_data": [
                {
                    "id": "2",
                    "name": "Company",
                    "quarters": [
                        {
                            "year": 2020,
                            "Q1": "NA",
                            "Q2": "NA",
                            "Q3": "NA",
                            "Q4": "NA",
                            "Full Year": "NA",
                        },
                        {
                            "year": 2021,
                            "Q1": "NA",
                            "Q2": -50.0,
                            "Q3": "NA",
                            "Q4": "NA",
                            "Full Year": "NA",
                            "vs": "NA",
                        },
                    ],
                }
            ],
            "averages": [
                {"Q1": "NA"},
                {"Q2": "NA"},
                {"Q3": "NA"},
                {"Q4": "NA"},
                {"Full Year": "NA"},
                {"Q1": "NA"},
                {"Q2": -50.0},
                {"Q3": "NA"},
                {"Q4": "NA"},
                {"Full Year": "NA"},
                {"vs": "NA"},
            ],
        }

        peers = self.report_instance.get_quarters_peers(
            "1",
            "user",
            "year_to_year",
            "growth",
            "actuals",
            ["2020", "2021"],
            None,
            False,
            True,
        )

        mock_set_company_permissions.assert_called()
        self.assertEqual(peers, expected_value)

    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    def test_get_quarters_peers_with_growth_actuals_budget_when_is_sucessful_should_return_report(
        self, mock_set_company_permissions
    ):
        data = self.records.copy()
        data.append(
            {
                "id": "2",
                "name": "Company",
                "scenario": "Actuals-2020",
                "metric": "Revenue",
                "year": 2020,
                "value": 44,
                "period_name": "Q2",
                "average": 9,
                "full_year_average": 2,
                "full_year": 1,
                "count_periods": 4,
            }
        )
        self.mock_repository.get_quarters_year_to_year_records.return_value = data
        self.mock_repository.get_functions_metric.return_value = {"actuals-revenue": {}}
        expected_value = {
            "headers": ["Company", "2020", "", "", "", "", "2021", "", "", "", "", ""],
            "subheaders": [
                "",
                "Q1",
                "Q2",
                "Q3",
                "Q4",
                "Full Year",
                "Q1",
                "Q2",
                "Q3",
                "Q4",
                "Full Year",
                "vs",
            ],
            "company_comparison_data": {
                "id": "1",
                "name": "Test",
                "quarters": [
                    {
                        "year": "2020",
                        "Q1": "NA",
                        "Q2": "NA",
                        "Q3": "NA",
                        "Q4": "NA",
                        "Full Year": "NA",
                    },
                    {
                        "year": "2021",
                        "Q1": "NA",
                        "Q2": "NA",
                        "Q3": "NA",
                        "Q4": "NA",
                        "Full Year": "NA",
                        "vs": "NA",
                    },
                ],
            },
            "peers_comparison_data": [
                {
                    "id": "2",
                    "name": "Company",
                    "quarters": [
                        {
                            "year": "2020",
                            "Q1": "NA",
                            "Q2": "NA",
                            "Q3": "NA",
                            "Q4": "NA",
                            "Full Year": "NA",
                        },
                        {
                            "year": "2021",
                            "Q1": "NA",
                            "Q2": -50.0,
                            "Q3": "NA",
                            "Q4": "NA",
                            "Full Year": "NA",
                            "vs": "NA",
                        },
                    ],
                }
            ],
            "averages": [
                {"Q1": "NA"},
                {"Q2": "NA"},
                {"Q3": "NA"},
                {"Q4": "NA"},
                {"Full Year": "NA"},
                {"Q1": "NA"},
                {"Q2": -50.0},
                {"Q3": "NA"},
                {"Q4": "NA"},
                {"Full Year": "NA"},
                {"vs": "NA"},
            ],
        }

        peers = self.report_instance.get_quarters_peers(
            "1",
            "user",
            "year_to_year",
            "growth",
            "actuals_budget",
            ["2020", "2021"],
            None,
            False,
            True,
        )

        mock_set_company_permissions.assert_called()
        self.assertEqual(peers, expected_value)

    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    def test_get_quarters_peers_rule_of_40_metric_when_is_sucessful_should_return_quarters_report(
        self, mock_set_company_permissions
    ):
        data = self.records.copy()
        data.append(
            {
                "id": "2",
                "name": "Company",
                "scenario": "Actuals-2020",
                "metric": "Revenue",
                "year": 2020,
                "value": 44,
                "period_name": "Q2",
                "average": 9,
                "full_year_average": 2,
                "full_year": 1,
                "count_periods": 4,
            }
        )
        self.mock_repository.get_metric_records_with_base_scenarios.return_value = data
        self.mock_repository.get_functions_metric.return_value = {"actuals-revenue": {}}
        expected_value = {
            "headers": ["Company", "2020", "", "", "", "", "2021", "", "", "", "", ""],
            "subheaders": [
                "",
                "Q1",
                "Q2",
                "Q3",
                "Q4",
                "Full Year",
                "Q1",
                "Q2",
                "Q3",
                "Q4",
                "Full Year",
                "vs",
            ],
            "company_comparison_data": {
                "id": "1",
                "name": "Test",
                "quarters": [
                    {
                        "year": 2020,
                        "Q1": "NA",
                        "Q2": "NA",
                        "Q3": "NA",
                        "Q4": "NA",
                        "Full Year": "NA",
                    },
                    {
                        "year": 2021,
                        "Q1": "NA",
                        "Q2": "NA",
                        "Q3": "NA",
                        "Q4": "NA",
                        "Full Year": "NA",
                        "vs": "NA",
                    },
                ],
            },
            "peers_comparison_data": [
                {
                    "id": "2",
                    "name": "Company",
                    "quarters": [
                        {
                            "year": 2020,
                            "Q1": "NA",
                            "Q2": "NA",
                            "Q3": "NA",
                            "Q4": "NA",
                            "Full Year": "NA",
                        },
                        {
                            "year": 2021,
                            "Q1": "NA",
                            "Q2": -28.0,
                            "Q3": "NA",
                            "Q4": "NA",
                            "Full Year": "NA",
                            "vs": "NA",
                        },
                    ],
                }
            ],
            "averages": [
                {"Q1": "NA"},
                {"Q2": "NA"},
                {"Q3": "NA"},
                {"Q4": "NA"},
                {"Full Year": "NA"},
                {"Q1": "NA"},
                {"Q2": -28.0},
                {"Q3": "NA"},
                {"Q4": "NA"},
                {"Full Year": "NA"},
                {"vs": "NA"},
            ],
        }

        peers = self.report_instance.get_quarters_peers(
            "1",
            "user",
            "year_to_year",
            "rule_of_40",
            "actuals",
            ["2020", "2021"],
            None,
            False,
            True,
        )

        mock_set_company_permissions.assert_called()
        self.assertEqual(peers, expected_value)

    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    def test_get_quarters_peers_rule_of_40_actuals_budget_when_is_sucessful_should_return_report(
        self, mock_set_company_permissions
    ):
        data = self.records.copy()
        data.append(
            {
                "id": "2",
                "name": "Company",
                "scenario": "Actuals-2020",
                "metric": "Revenue",
                "year": 2020,
                "value": 44,
                "period_name": "Q2",
                "average": 9,
                "full_year_average": 2,
                "full_year": 1,
                "count_periods": 4,
            }
        )
        self.mock_repository.get_quarters_year_to_year_records.return_value = data
        self.mock_repository.get_functions_metric.return_value = {"actuals-revenue": {}}
        expected_value = {
            "headers": ["Company", "2020", "", "", "", "", "2021", "", "", "", "", ""],
            "subheaders": [
                "",
                "Q1",
                "Q2",
                "Q3",
                "Q4",
                "Full Year",
                "Q1",
                "Q2",
                "Q3",
                "Q4",
                "Full Year",
                "vs",
            ],
            "company_comparison_data": {
                "id": "1",
                "name": "Test",
                "quarters": [
                    {
                        "year": "2020",
                        "Q1": "NA",
                        "Q2": "NA",
                        "Q3": "NA",
                        "Q4": "NA",
                        "Full Year": "NA",
                    },
                    {
                        "year": "2021",
                        "Q1": "NA",
                        "Q2": "NA",
                        "Q3": "NA",
                        "Q4": "NA",
                        "Full Year": "NA",
                        "vs": "NA",
                    },
                ],
            },
            "peers_comparison_data": [
                {
                    "id": "2",
                    "name": "Company",
                    "quarters": [
                        {
                            "year": "2020",
                            "Q1": "NA",
                            "Q2": "NA",
                            "Q3": "NA",
                            "Q4": "NA",
                            "Full Year": "NA",
                        },
                        {
                            "year": "2021",
                            "Q1": "NA",
                            "Q2": -28.0,
                            "Q3": "NA",
                            "Q4": "NA",
                            "Full Year": "NA",
                            "vs": "NA",
                        },
                    ],
                }
            ],
            "averages": [
                {"Q1": "NA"},
                {"Q2": "NA"},
                {"Q3": "NA"},
                {"Q4": "NA"},
                {"Full Year": "NA"},
                {"Q1": "NA"},
                {"Q2": -28.0},
                {"Q3": "NA"},
                {"Q4": "NA"},
                {"Full Year": "NA"},
                {"vs": "NA"},
            ],
        }

        peers = self.report_instance.get_quarters_peers(
            "1",
            "user",
            "year_to_year",
            "rule_of_40",
            "actuals_budget",
            ["2020", "2021"],
            None,
            False,
            True,
        )

        mock_set_company_permissions.assert_called()
        self.assertEqual(peers, expected_value)

    def test_get_no_standard_metric_records_should_fail_with_invalid_metric(self):
        with self.assertRaises(Exception) as context:
            self.report_instance.get_no_standard_metric_records(
                "year_year", "invalid", "Actuals", [2021, 2022], None, dict()
            )

        self.assertEqual(str(context.exception), "Metric not found")

    def test_process_net_retention_metrics_success_should_return_data(self):
        run_rate_revenue = {
            "1": {
                "id": 1,
                "quarters": [
                    {
                        "year": 2019,
                        "Q1": 2,
                        "Q2": 1,
                        "Q3": "NA",
                        "Q4": 5,
                        "Full Year": "NA",
                    }
                ],
            }
        }
        losses_and_downgrades = {
            "1": {
                "id": 1,
                "quarters": [
                    {
                        "year": 2020,
                        "Q1": 2,
                        "Q2": 1,
                        "Q3": "NA",
                        "Q4": 5,
                        "Full Year": "NA",
                    }
                ],
            }
        }
        expected_value = {
            "1": {
                "id": 1,
                "quarters": [
                    {
                        "year": 2020,
                        "Q1": 100,
                        "Q2": 100,
                        "Q3": "NA",
                        "Q4": 100,
                        "Full Year": "NA",
                    }
                ],
            },
            "averages": {
                "2020": {"Q1": 100, "Q2": 100, "Q3": "NA", "Q4": 100, "Full Year": "NA"}
            },
        }
        retention = self.report_instance.process_retention_metrics(
            "net_retention",
            ["2020"],
            "year_to_year",
            "actuals",
            run_rate_revenue,
            losses_and_downgrades,
            losses_and_downgrades,
            "Q4",
        )

        self.assertEqual(retention, expected_value)

    def test_get_gross_retention_records_base_scenarios_success_should_return_data(
        self,
    ):
        self.mock_repository.get_quarters_year_to_year_records.return_value = (
            self.records
        )
        expected_value = (
            [
                {
                    "id": "1",
                    "name": "Test",
                    "quarters": [
                        {
                            "year": "2020",
                            "Q1": "NA",
                            "Q2": "NA",
                            "Q3": "NA",
                            "Q4": "NA",
                            "Full Year": "NA",
                        },
                        {
                            "year": "2021",
                            "Q1": "NA",
                            "Q2": "NA",
                            "Q3": "NA",
                            "Q4": "NA",
                            "Full Year": "NA",
                            "vs": "NA",
                        },
                    ],
                },
                {
                    "id": "2",
                    "name": "Company",
                    "quarters": [
                        {
                            "year": "2020",
                            "Q1": "NA",
                            "Q2": "NA",
                            "Q3": "NA",
                            "Q4": "NA",
                            "Full Year": "NA",
                        },
                        {
                            "year": "2021",
                            "Q1": "NA",
                            "Q2": "NA",
                            "Q3": "NA",
                            "Q4": "NA",
                            "Full Year": "NA",
                            "vs": "NA",
                        },
                    ],
                },
            ],
            [
                {"Q1": "NA"},
                {"Q2": "NA"},
                {"Q3": "NA"},
                {"Q4": "NA"},
                {"Full Year": "NA"},
                {"Q1": "NA"},
                {"Q2": "NA"},
                {"Q3": "NA"},
                {"Q4": "NA"},
                {"Full Year": "NA"},
                {"vs": "NA"},
            ],
        )

        retention = self.report_instance.get_retention_records_base_scenarios(
            "gross_retention",
            "actuals_budget",
            ["2020", "2021"],
            dict(),
            "year_to_year",
        )

        self.assertEqual(retention, expected_value)

    def test_get_net_retention_records_base_scenarios_success_should_return_data(self):
        self.mock_repository.get_metric_records_with_base_scenarios.return_value = [
            self.records[0]
        ]
        expected_value = {
            "1": {
                "id": "1",
                "name": "Test",
                "quarters": [
                    {
                        "year": 2020,
                        "Q1": "NA",
                        "Q2": "NA",
                        "Q3": "NA",
                        "Q4": "NA",
                        "Full Year": "NA",
                    },
                    {
                        "year": 2021,
                        "Q1": "NA",
                        "Q2": "NA",
                        "Q3": "NA",
                        "Q4": "NA",
                        "Full Year": "NA",
                        "vs": "NA",
                    },
                ],
            },
            "averages": {
                "2020": {
                    "Q1": "NA",
                    "Q2": "NA",
                    "Q3": "NA",
                    "Q4": "NA",
                    "Full Year": "NA",
                },
                "2021": {
                    "Q1": "NA",
                    "Q2": "NA",
                    "Q3": "NA",
                    "Q4": "NA",
                    "Full Year": "NA",
                    "vs": "NA",
                },
            },
        }

        retention = self.report_instance.get_retention_records_base_scenarios(
            "net_retention", "actuals", ["2020", "2021"], dict(), "year_to_year"
        )

        self.assertEqual(retention, expected_value)

    def test_process_net_retention_with_no_data_should_return_data(self):
        losses_and_downgrades = {
            "1": {
                "id": 1,
                "quarters": [
                    {
                        "year": 2020,
                        "Q1": 2,
                        "Q2": 1,
                        "Q3": "NA",
                        "Q4": 5,
                        "Full Year": "NA",
                    }
                ],
            }
        }
        expected_value = {
            "1": {
                "id": 1,
                "quarters": [
                    {
                        "year": 2020,
                        "Q1": "NA",
                        "Q2": "NA",
                        "Q3": "NA",
                        "Q4": "NA",
                        "Full Year": "NA",
                    }
                ],
            },
            "averages": {},
        }
        retention = self.report_instance.process_retention_metrics(
            "net_retention",
            ["2019", "2020"],
            "last_twelve_months",
            "actuals",
            dict(),
            losses_and_downgrades,
            losses_and_downgrades,
            "Q4",
        )

        self.assertEqual(retention, expected_value)

    def test_process_net_retention_metrics_no_base_scenario_should_return_data(self):
        run_rate_revenue = {
            "1": {
                "id": 1,
                "quarters": [
                    {
                        "year": 2019,
                        "Q1": 2,
                        "Q2": 1,
                        "Q3": "NA",
                        "Q4": 5,
                        "Full Year": "NA",
                    },
                    {
                        "year": 2020,
                        "Q1": 9,
                        "Q2": 1,
                        "Q3": "NA",
                        "Q4": 5,
                        "Full Year": "NA",
                    },
                ],
            }
        }
        losses_and_downgrades = {
            "1": {
                "id": 1,
                "quarters": [
                    {
                        "year": 2020,
                        "Q1": 2,
                        "Q2": 1,
                        "Q3": "NA",
                        "Q4": 5,
                        "Full Year": "NA",
                    },
                    {
                        "year": 2021,
                        "Q1": 2,
                        "Q2": 1,
                        "Q3": "NA",
                        "Q4": 5,
                        "Full Year": "NA",
                    },
                ],
            }
        }
        expected_value = [
            {
                "id": 1,
                "quarters": [
                    {
                        "year": 2020,
                        "Q1": 100,
                        "Q2": 100,
                        "Q3": "NA",
                        "Q4": 100,
                        "Full Year": "NA",
                    },
                    {
                        "year": 2021,
                        "Q1": 100,
                        "Q2": 100,
                        "Q3": "NA",
                        "Q4": 100,
                        "Full Year": "NA",
                    },
                ],
            }
        ]
        retention = self.report_instance.process_retention_metrics(
            "net_retention",
            ["2019", "2020"],
            "last_twelve_months",
            "actuals_budget",
            run_rate_revenue,
            losses_and_downgrades,
            losses_and_downgrades,
            "Q4",
        )

        self.assertEqual(retention[0], expected_value)

    def test_process_new_bookings_growth_no_base_scenario_should_return_data(self):
        new_bookings = {
            "1": {
                "id": 1,
                "quarters": [
                    {
                        "year": 2018,
                        "Q1": 2,
                        "Q2": 1,
                        "Q3": "NA",
                        "Q4": 5,
                        "Full Year": "NA",
                    },
                    {
                        "year": 2019,
                        "Q1": 2,
                        "Q2": 1,
                        "Q3": "NA",
                        "Q4": 5,
                        "Full Year": "NA",
                    },
                    {
                        "year": 2020,
                        "Q1": 9,
                        "Q2": 1,
                        "Q3": "NA",
                        "Q4": 5,
                        "Full Year": "NA",
                    },
                ],
            }
        }

        expected_value = [
            {
                "id": 1,
                "quarters": [
                    {"year": 2019, "Full Year": "NA"},
                    {
                        "year": 2020,
                        "Q1": 450,
                        "Q2": 100,
                        "Q3": "NA",
                        "Q4": 100,
                        "Full Year": "NA",
                    },
                ],
            }
        ]
        retention = self.report_instance.process_new_bookings_growth(
            ["2019", "2020"],
            "last_twelve_months",
            "actuals_budget",
            new_bookings,
            "Q4",
        )

        self.assertEqual(retention[0], expected_value)

    def test_process_new_bookings_growth_base_scenario_should_return_data(self):
        new_bookings = {
            "1": {
                "id": 1,
                "quarters": [
                    {
                        "year": 2018,
                        "Q1": 2,
                        "Q2": 1,
                        "Q3": "NA",
                        "Q4": 5,
                        "Full Year": "NA",
                    },
                    {
                        "year": 2019,
                        "Q1": 2,
                        "Q2": 1,
                        "Q3": "NA",
                        "Q4": 5,
                        "Full Year": "NA",
                    },
                    {
                        "year": 2020,
                        "Q1": 9,
                        "Q2": 1,
                        "Q3": "NA",
                        "Q4": 5,
                        "Full Year": "NA",
                    },
                ],
            }
        }

        expected_value = {
            "1": {
                "id": 1,
                "quarters": [
                    {
                        "year": 2019,
                        "Q1": 100,
                        "Q2": 100,
                        "Q3": "NA",
                        "Q4": 100,
                        "Full Year": "NA",
                    },
                    {
                        "year": 2020,
                        "Q1": 450,
                        "Q2": 100,
                        "Q3": "NA",
                        "Q4": 100,
                        "Full Year": "NA",
                    },
                ],
            },
            "averages": {
                "2019": {
                    "Q1": 100,
                    "Q2": 100,
                    "Q3": "NA",
                    "Q4": 100,
                    "Full Year": "NA",
                },
                "2020": {
                    "Q1": 450,
                    "Q2": 100,
                    "Q3": "NA",
                    "Q4": 100,
                    "Full Year": "NA",
                    "vs": "NA",
                },
            },
        }
        retention = self.report_instance.process_new_bookings_growth(
            ["2019", "2020"],
            "lyear_to_year",
            "actuals",
            new_bookings,
            "Q4",
        )

        self.assertEqual(retention, expected_value)

    def test_get_new_bookings_growth_records_base_scenarios_success_should_return_data(
        self,
    ):
        self.mock_repository.get_metric_records_with_base_scenarios.return_value = [
            self.records[0]
        ]
        expected_value = {
            "1": {
                "id": "1",
                "name": "Test",
                "quarters": [
                    {
                        "year": 2020,
                        "Q1": "NA",
                        "Q2": "NA",
                        "Q3": "NA",
                        "Q4": "NA",
                        "Full Year": "NA",
                    },
                    {
                        "year": 2021,
                        "Q1": "NA",
                        "Q2": "NA",
                        "Q3": "NA",
                        "Q4": "NA",
                        "Full Year": "NA",
                        "vs": "NA",
                    },
                ],
            },
            "averages": {
                "2020": {
                    "Q1": "NA",
                    "Q2": "NA",
                    "Q3": "NA",
                    "Q4": "NA",
                    "Full Year": "NA",
                },
                "2021": {
                    "Q1": "NA",
                    "Q2": "NA",
                    "Q3": "NA",
                    "Q4": "NA",
                    "Full Year": "NA",
                    "vs": "NA",
                },
            },
        }

        new_bookings = self.report_instance.get_new_bookings_growth_records(
            "actuals", ["2020", "2021"], dict(), "year_to_year"
        )

        self.assertEqual(new_bookings, expected_value)

    def test_get_new_bookings_growth_records_no_base_scenarios_success_should_return_data(
        self,
    ):
        self.mock_repository.get_quarters_year_to_year_records.return_value = (
            self.records
        )
        expected_value = [
            {
                "id": "1",
                "name": "Test",
                "quarters": [
                    {
                        "year": "2020",
                        "Q1": "NA",
                        "Q2": "NA",
                        "Q3": "NA",
                        "Q4": "NA",
                        "Full Year": "NA",
                    },
                    {
                        "year": "2021",
                        "Q1": "NA",
                        "Q2": "NA",
                        "Q3": "NA",
                        "Q4": "NA",
                        "Full Year": "NA",
                        "vs": "NA",
                    },
                ],
            },
            {
                "id": "2",
                "name": "Company",
                "quarters": [
                    {
                        "year": "2020",
                        "Q1": "NA",
                        "Q2": "NA",
                        "Q3": "NA",
                        "Q4": "NA",
                        "Full Year": "NA",
                    },
                    {
                        "year": "2021",
                        "Q1": "NA",
                        "Q2": "NA",
                        "Q3": "NA",
                        "Q4": "NA",
                        "Full Year": "NA",
                        "vs": "NA",
                    },
                ],
            },
        ]

        new_bookings = self.report_instance.get_new_bookings_growth_records(
            "actuals_budget", ["2020", "2021"], dict(), "year_to_year"
        )

        self.assertEqual(new_bookings[0], expected_value)
