import logging
from unittest.mock import Mock
from unittest import TestCase, mock
from parameterized import parameterized

from src.service.quarters_report.quarters_report import QuartersReport
from src.utils.company_anonymization import CompanyAnonymization

logger = logging.getLogger()
logger.setLevel(logging.INFO)
size_range = {"label": "$30-<50 million", "max_value": 50, "min_value": 30}


class TestQuartersReport(TestCase):
    def setUp(self):
        self.mock_repository = Mock()
        self.mock_profile_range = Mock()
        self.company_anonymization = CompanyAnonymization(object)
        self.report_instance = QuartersReport(
            logger,
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
                "period_name": "3",
                "average": 2,
                "full_year_average": 3,
                "full_year": 0,
                "count_periods": 2,
            },
        )
        self.mock_repository.get_metric_records_by_quarters.return_value = records
        self.mock_repository.get_functions_metric.return_value = {"actuals-revenue": {}}
        expected_response = {
            "subheaders": [
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
            "headers": [
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
                        "Q1": 20.0,
                        "Q2": "NA",
                        "Q3": "NA",
                        "Q4": "NA",
                        "full_year": "NA",
                        "3": 20.0,
                    },
                    {
                        "year": 2021,
                        "Q1": "NA",
                        "Q2": "NA",
                        "Q3": "NA",
                        "Q4": "NA",
                        "full_year": "NA",
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
                            "full_year": "NA",
                        },
                        {
                            "year": 2021,
                            "Q1": "NA",
                            "Q2": 22.0,
                            "Q3": "NA",
                            "Q4": "NA",
                            "full_year": "NA",
                            "vs": "NA",
                        },
                    ],
                }
            ],
            "averages": [
                {"Q1": 2.0},
                {"Q2": "NA"},
                {"Q3": "NA"},
                {"Q4": "NA"},
                {"Full Year": 3.0},
                {"3": 2.0},
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
            "year_year",
            "revenue",
            "actuals",
            ["2020", "2021"],
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
            "year_year",
            "revenue",
            "actuals",
            ["2020", "2021"],
            False,
            False,
        )

        mock_set_company_permissions.assert_called()
        mock_anonymize_companies_values.assert_called()

    # @mock.patch(
    #     "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    # )
    # def test_get_quarters_peers_with_actuals_plus_budget_scenario_should_return_quarters_report(
    #     self, mock_set_company_permissions
    # ):
    #     records = self.records.copy()
    #     records.append(
    #         {
    #             "id": "1",
    #             "name": "Test",
    #             "scenario": "Budget-2020",
    #             "metric": "Revenue",
    #             "year": 2020,
    #             "value": 20,
    #             "period_name": "3",
    #             "average": 2,
    #             "full_year_average": 3,
    #             "full_year": 0,
    #             "count_periods": 2,
    #         },
    #     )
    #     self.mock_repository.get_actuals_plus_budget_metrics_query.return_value = (
    #         records
    #     )
    #     expected_peers = {
    #         "subheaders": [
    #             "Company",
    #             "2020",
    #             "",
    #             "",
    #             "",
    #             "",
    #             "2021",
    #             "",
    #             "",
    #             "",
    #             "",
    #             "",
    #         ],
    #         "headers": [
    #             "",
    #             "Q1",
    #             "Q2",
    #             "Q3",
    #             "Q4",
    #             "Full Year",
    #             "Q1",
    #             "Q2",
    #             "Q3",
    #             "Q4",
    #             "Full Year",
    #             "vs",
    #         ],
    #         "company_comparison_data": {
    #             "id": "1",
    #             "name": "Test",
    #             "quarters": [
    #                 {
    #                     "year": "2020",
    #                     "Q1": 20.0,
    #                     "Q2": "NA",
    #                     "Q3": "NA",
    #                     "Q4": "NA",
    #                     "full_year": 20.0,
    #                 },
    #                 {
    #                     "year": "2021",
    #                     "Q1": "NA",
    #                     "Q2": "NA",
    #                     "Q3": "NA",
    #                     "Q4": "NA",
    #                     "Full Year": "NA",
    #                     "vs": "NA",
    #                 },
    #             ],
    #         },
    #         "peers_comparison_data": [
    #             {
    #                 "id": "2",
    #                 "name": "Company",
    #                 "quarters": [
    #                     {
    #                         "year": "2021",
    #                         "Q1": "NA",
    #                         "Q2": 22.0,
    #                         "Q3": "NA",
    #                         "Q4": "NA",
    #                         "full_year": 22.0,
    #                     },
    #                     {
    #                         "year": "2020",
    #                         "Q1": "NA",
    #                         "Q2": "NA",
    #                         "Q3": "NA",
    #                         "Q4": "NA",
    #                         "Full Year": "NA",
    #                         "vs": "NA",
    #                     },
    #                 ],
    #             }
    #         ],
    #         "averages": [
    #             {"Q1": 20.0},
    #             {"Q2": "NA"},
    #             {"Q3": "NA"},
    #             {"Q4": "NA"},
    #             {"Full Year": 20.0},
    #             {"Q1": "NA"},
    #             {"Q2": 22.0},
    #             {"Q3": "NA"},
    #             {"Q4": "NA"},
    #             {"Full Year": 22.0},
    #             {"vs": "NA"},
    #         ],
    #     }

    #     peers = self.report_instance.get_quarters_peers(
    #         "1",
    #         "user",
    #         "year_year",
    #         "revenue",
    #         "actuals_budget",
    #         ["2020", "2021"],
    #         False,
    #         True,
    #     )

    #     mock_set_company_permissions.assert_called()
    #     self.assertEqual(peers, expected_peers)

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
                        "full_year": "$20 million - $40 million",
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
                    {"year": 2021, "Q1": 2, "Q2": 2, "Q3": 3, "Q4": 3, "full_year": 10}
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
                    {"year": "2020", "full_year": 12.1},
                    {"year": "2021", "full_year": 4.3},
                    {"year": "2022", "full_year": 5.3},
                ],
                36.0,
            ],
            [
                2,
                [
                    {"year": "2020", "full_year": 0},
                    {"year": "2021", "full_year": 0},
                    {"year": "2022", "full_year": 5.3},
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
