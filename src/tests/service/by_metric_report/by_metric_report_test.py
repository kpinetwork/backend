import logging
from unittest.mock import Mock
from unittest import TestCase, mock
from parameterized import parameterized

from src.service.by_metric_report.by_metric_report import ByMetricReport
from src.service.calculator.calculator_service import CalculatorService
from src.utils.company_anonymization import CompanyAnonymization

logger = logging.getLogger()
logger.setLevel(logging.INFO)
size_range = {"label": "$30-<50 million", "max_value": 50, "min_value": 30}


class TestByMetricReport(TestCase):
    def setUp(self):
        self.mock_repository = Mock()
        self.mock_profile_range = Mock()
        self.calculator = CalculatorService(logger)
        self.company_anonymization = CompanyAnonymization(object)
        self.report_instance = ByMetricReport(
            logger,
            self.calculator,
            self.mock_repository,
            self.mock_profile_range,
            self.company_anonymization,
        )
        self.records = [
            {"id": "1", "name": "Test", "year": 2019, "value": 3},
            {"id": "1", "name": "Test", "year": 2020, "value": 4},
            {"id": "2", "name": "Company", "year": 2019, "value": 6},
        ]
        self.sizes = [
            {"label": ">$20 million", "min_value": None, "max_value": 20},
            {"label": "$20 million - $40 million", "min_value": 20, "max_value": 40},
            {"label": "$40 million +", "min_value": 40, "max_value": None},
        ]

    def test_get_growth_metrics_with_no_empty_year_list_should_return_dict_with_growth_year_records(
        self,
    ):
        years = [2018, 2019, 2020, 2021]
        company = {"metrics": {2020: 20, 2021: 19}}
        expected_metrics = {2018: "NA", 2019: "NA", 2020: "NA", 2021: -5}

        metrics = self.report_instance.get_growth_metrics("growth", company, years)

        self.assertEqual(metrics, expected_metrics)

    def test_get_retention_metrics_when_metric_is_gross_retention_should_calculate_metrics(
        self,
    ):
        years = [2018, 2019, 2020, 2021]
        company_run_rate_revenue = {"metrics": {2020: 82, 2021: 19}}
        company_losses_and_downgrades = {"metrics": {2020: 8, 2021: 34}}
        expected_metrics = {2018: "NA", 2019: "NA", 2020: "NA", 2021: 59}

        metrics = self.report_instance.get_retention_metrics(
            "gross_retention",
            company_run_rate_revenue,
            company_losses_and_downgrades,
            dict(),
            years,
        )

        self.assertEqual(metrics, expected_metrics)

    def test_get_retention_metrics_when_metric_is_net_retention_should_calculate_metrics(
        self,
    ):
        years = [2018, 2019, 2020, 2021]
        company_run_rate_revenue = {"metrics": {2020: 82, 2021: 19}}
        company_losses_and_downgrades = {"metrics": {2020: 8, 2021: 34}}
        company_upsells = {"metrics": {2020: 8, 2021: 12}}
        expected_metrics = {2018: "NA", 2019: "NA", 2020: "NA", 2021: 73}

        metrics = self.report_instance.get_retention_metrics(
            "net_retention",
            company_run_rate_revenue,
            company_losses_and_downgrades,
            company_upsells,
            years,
        )

        self.assertEqual(metrics, expected_metrics)

    def test_get_rule_of_40_metrics_with_valid_ebitda_and_growth_metric_return_correct_values(
        self,
    ):
        growth = {2020: 3, 2021: 5, 2022: "NA"}
        margin = {2020: -3, 2021: 15, 2022: 21}
        expected_metrics = {2020: 0, 2021: 20, 2022: "NA"}

        rule_of_40 = self.report_instance.get_rule_of_40_metrics(growth, margin)

        self.assertEqual(rule_of_40, expected_metrics)

    # def test_process_standard_metrics_with_metric_records_should_build_dict_structure(
    #     self,
    # ):
    #     expected_data = {
    #         "1": {"id": "1", "name": "Test", "metrics": {2019: 3, 2020: 4}},
    #         "2": {"id": "2", "name": "Company", "metrics": {2019: 6}},
    #     }

    #     data = self.report_instance.process_standard_metrics(self.records)

    #     self.assertEqual(data, expected_data)

    # def test_process_growth_with_metric_records_should_build_dict_structure(self):
    #     expected_growth = {
    #         "1": {
    #             "id": "1",
    #             "name": "Test",
    #             "metrics": {2019: "NA", 2020: 33, 2021: "NA"},
    #         },
    #         "2": {
    #             "id": "2",
    #             "name": "Company",
    #             "metrics": {2019: "NA", 2020: "NA", 2021: "NA"},
    #         },
    #     }

    #     data = self.report_instance.process_growth_metrics(
    #         "growth", self.records, [2019, 2020, 2021]
    #     )

    #     self.assertEqual(data, expected_growth)

    # def test_process_ratio_metrics_with_valid_metric_return_value_with_specific_decimals(
    #     self,
    # ):
    #     self.mock_repository.get_metric_records.return_value = self.records
    #     expected_growth = {
    #         "1": {
    #             "id": "1",
    #             "name": "Test",
    #             "metrics": {2019: "3.00x", 2020: "4.00x"},
    #         },
    #         "2": {
    #             "id": "2",
    #             "name": "Company",
    #             "metrics": {2019: "6.00x"},
    #         },
    #     }

    #     data = self.report_instance.process_ratio_metrics(
    #         "cac_ratio", [2019, 2020, 2021]
    #     )

    #     self.assertEqual(data, expected_growth)

    # def test_process_ratio_metrics_when_metric_value_is_none_return_na_values(self):
    #     records = self.records.copy()
    #     records = [{"id": "1", "name": "Test", "year": 2019, "value": None}]
    #     self.mock_repository.get_metric_records.return_value = records
    #     expected_growth = {
    #         "1": {
    #             "id": "1",
    #             "name": "Test",
    #             "metrics": {2019: "NA"},
    #         }
    #     }

    #     data = self.report_instance.process_ratio_metrics(
    #         "cac_ratio", [2019, 2020, 2021]
    #     )

    #     self.assertEqual(data, expected_growth)

    # def test_process_retention_when_metric_is_gross_retention_return_metrics_dict(self):
    #     expected_growth = {
    #         "1": {
    #             "id": "1",
    #             "name": "Test",
    #             "metrics": {2019: "NA", 2020: "NA", 2021: -167},
    #         }
    #     }

    #     data = self.report_instance.process_retention(
    #         "gross_retention",
    #         [{"id": "1", "name": "Test", "year": 2020, "value": 3}],
    #         [{"id": "1", "name": "Test", "year": 2021, "value": 8}],
    #         [2019, 2020, 2021],
    #         {},
    #     )

    #     self.assertEqual(data, expected_growth)
    #     self.mock_repository.get_metric_records.assert_not_called()

    # def test_process_retention_when_metric_is_net_retention_call_get_metric_records(
    #     self,
    # ):
    #     self.mock_repository.get_metric_records.return_value = self.records
    #     expected_growth = {
    #         "1": {
    #             "id": "1",
    #             "name": "Test",
    #             "metrics": {2019: "NA", 2020: -33, 2021: "NA"},
    #         }
    #     }

    #     data = self.report_instance.process_retention(
    #         "net_retention",
    #         [{"id": "1", "name": "Test", "year": 2019, "value": 3}],
    #         [{"id": "1", "name": "Test", "year": 2020, "value": 8}],
    #         [2019, 2020, 2021],
    #         {},
    #     )

    #     self.assertEqual(data, expected_growth)
    #     self.mock_repository.get_metric_records.assert_called()

    # def test_process_debt_ebitda_with_no_mepty_data_return_metrics_dict(self):
    #     self.mock_repository.get_metric_records.return_value = self.records
    #     expected_debt_ebitda = {
    #         "1": {
    #             "id": "1",
    #             "name": "Test",
    #             "metrics": {2019: 3.0, 2020: 4.0},
    #         },
    #         "2": {
    #             "id": "2",
    #             "name": "Company",
    #             "metrics": {2019: 6.0},
    #         },
    #     }

    #     data = self.report_instance.process_debt_ebitda(
    #         "debt_ebitda", [2019, 2020, 2021]
    #     )
    #     self.assertEqual(data, expected_debt_ebitda)

    # def test_process_debt_ebitda_without_metric_value_return_NA(self):
    #     records = self.records.copy()
    #     records = [{"id": "1", "name": "Test", "year": 2019, "value": None}]
    #     self.mock_repository.get_metric_records.return_value = records
    #     expected_debt_ebitda = {
    #         "1": {
    #             "id": "1",
    #             "name": "Test",
    #             "metrics": {2019: "NA"},
    #         }
    #     }

    #     data = self.report_instance.process_debt_ebitda(
    #         "debt_ebitda", [2019, 2020, 2021]
    #     )

    #     self.assertEqual(data, expected_debt_ebitda)

    def test_process_rule_of_40_with_data_return_companies_metrics_dict(self):
        expected_data = {
            "1": {
                "id": "1",
                "name": None,
                "metrics": {2019: "NA", 2020: 22, 2021: "NA"},
            }
        }
        growth = {"1": {"metrics": {2019: "NA", 2020: 23, 2021: 14}}}
        margin = {"1": {"metrics": {2019: 4, 2020: -1}}}

        data = self.report_instance.process_rule_of_40(growth, margin)

        self.assertEqual(data, expected_data)

    def get_range_from_value(self, value, ranges=None):
        logger.info(value)
        logger.info(ranges)
        return "$3 million-$30 million"

    def test_get_profiles_with_ranges_should_return_correct_range_label(self):
        self.mock_repository.get_most_recents_revenue.return_value = [
            {"id": "1", "name": "Actuals-2020", "value": 23},
            {"id": "1", "name": "Actuals-2029", "value": 21},
        ]
        self.mock_profile_range.get_profile_ranges.return_value = self.sizes
        self.mock_profile_range.get_range_from_value.side_effect = (
            self.get_range_from_value
        )
        expected_profile = {
            "1": {
                "size_cohort": "$3 million-$30 million",
                "margin_group": "$3 million-$30 million",
            }
        }

        profiles = self.report_instance.get_profiles(dict())

        self.assertEqual(profiles, expected_profile)

    # def test_get_retention_records_should_return_companies_metrics_dict(self):
    #     self.mock_repository.get_metric_records.return_value = self.records
    #     expected_data = {
    #         "1": {
    #             "id": "1",
    #             "name": "Test",
    #             "metrics": {2019: "NA", 2020: -33, 2021: "NA"},
    #         },
    #         "2": {
    #             "id": "2",
    #             "name": "Company",
    #             "metrics": {2019: "NA", 2020: "NA", 2021: "NA"},
    #         },
    #     }

    #     data = self.report_instance.get_retention_records(
    #         "gross_retention", [2019, 2020, 2021], dict()
    #     )

    #     self.assertEqual(data, expected_data)

    # def test_get_no_standard_records_with_growth_should_return_companies_metrics_dict(
    #     self,
    # ):
    #     self.mock_repository.get_metric_records.return_value = self.records
    #     expected_data = {
    #         "1": {
    #             "id": "1",
    #             "name": "Test",
    #             "metrics": {2019: "NA", 2020: 33, 2021: "NA"},
    #         },
    #         "2": {
    #             "id": "2",
    #             "name": "Company",
    #             "metrics": {2019: "NA", 2020: "NA", 2021: "NA"},
    #         },
    #     }

    #     data = self.report_instance.get_no_standard_records(
    #         "growth", [2019, 2020, 2021], dict()
    #     )

    #     self.assertEqual(data, expected_data)

    # def test_get_no_standard_records_with_retention_should_return_companies_metrics_dict(
    #     self,
    # ):
    #     self.mock_repository.get_metric_records.return_value = self.records
    #     expected_data = {
    #         "1": {
    #             "id": "1",
    #             "name": "Test",
    #             "metrics": {2019: "NA", 2020: -33, 2021: "NA"},
    #         },
    #         "2": {
    #             "id": "2",
    #             "name": "Company",
    #             "metrics": {2019: "NA", 2020: "NA", 2021: "NA"},
    #         },
    #     }

    #     data = self.report_instance.get_no_standard_records(
    #         "gross_retention", [2019, 2020, 2021], dict()
    #     )

    #     self.assertEqual(data, expected_data)

    # def test_get_no_standard_records_with_new_bookings_growth
    # _should_return_companies_metrics_dict(
    #     self,
    # ):
    #     self.mock_repository.get_metric_records.return_value = self.records
    #     expected_data = {
    #         "1": {
    #             "id": "1",
    #             "name": "Test",
    #             "metrics": {2019: "NA", 2020: 133, 2021: "NA"},
    #         },
    #         "2": {
    #             "id": "2",
    #             "name": "Company",
    #             "metrics": {2019: "NA", 2020: "NA", 2021: "NA"},
    #         },
    #     }

    #     data = self.report_instance.get_no_standard_records(
    #         "new_bookings_growth", [2019, 2020, 2021], dict()
    #     )

    #     self.assertEqual(data, expected_data)

    # def test_get_no_standard_records_with_rule_of_40_should_return_companies_metrics_dict(
    #     self,
    # ):
    #     self.mock_repository.get_metric_records.return_value = self.records
    #     expected_data = {
    #         "1": {
    #             "id": "1",
    #             "name": "Test",
    #             "metrics": {2019: "NA", 2020: 37, 2021: "NA"},
    #         },
    #         "2": {
    #             "id": "2",
    #             "name": "Company",
    #             "metrics": {2019: "NA", 2020: "NA", 2021: "NA"},
    #         },
    #     }

    #     data = self.report_instance.get_no_standard_records(
    #         "rule_of_40", [2019, 2020, 2021], dict()
    #     )

    #     self.assertEqual(data, expected_data)

    # def test_get_records_with_standard_metric_should_return_companies_metrics_dict(
    #     self,
    # ):
    #     self.mock_repository.get_metric_records.return_value = self.records
    #     self.mock_repository.get_functions_metric.return_value = {"actuals_revenue": {}}
    #     expected_data = {
    #         "1": {"id": "1", "name": "Test", "metrics": {2019: 3, 2020: 4}},
    #         "2": {"id": "2", "name": "Company", "metrics": {2019: 6}},
    #     }

    #     data = self.report_instance.get_records(
    #         "actuals_revenue", [2019, 2020, 2021], dict()
    #     )

    #     self.assertEqual(data, expected_data)

    # def test_get_records_with_debt_ebitda_should_return_companies_metrics_dict(self):
    #     self.mock_repository.get_metric_records.return_value = self.records
    #     self.mock_repository.get_functions_metric.return_value = {"debt_ebitda": {}}
    #     expected_data = {
    #         "1": {"id": "1", "name": "Test", "metrics": {2019: 3.0, 2020: 4.0}},
    #         "2": {"id": "2", "name": "Company", "metrics": {2019: 6.0}},
    #     }

    #     data = self.report_instance.get_records(
    #         "debt_ebitda", [2019, 2020, 2021], dict()
    #     )

    #     self.assertEqual(data, expected_data)

    # def test_get_records_with_ratio_metric_should_return_companies_metrics_dict(self):
    #     self.mock_repository.get_metric_records.return_value = self.records
    #     self.mock_repository.get_functions_metric.return_value = {"actuals_revenue": {}}
    #     expected_data = {
    #         "1": {"id": "1", "name": "Test", "metrics": {2019: "3.0x", 2020: "4.0x"}},
    #         "2": {"id": "2", "name": "Company", "metrics": {2019: "6.0x"}},
    #     }

    #     data = self.report_instance.get_records(
    #         "clv_cac_ratio", [2019, 2020, 2021], dict()
    #     )

    #     self.assertEqual(data, expected_data)

    # def test_get_records_with_no_standard_metric_should_return_companies_metrics_dict(
    #     self,
    # ):
    #     self.mock_repository.get_metric_records.return_value = self.records
    #     self.mock_repository.get_functions_metric.return_value = {"actuals_revenue": {}}
    #     expected_data = {
    #         "1": {
    #             "id": "1",
    #             "name": "Test",
    #             "metrics": {2019: "NA", 2020: 33, 2021: "NA"},
    #         },
    #         "2": {
    #             "id": "2",
    #             "name": "Company",
    #             "metrics": {2019: "NA", 2020: "NA", 2021: "NA"},
    #         },
    #     }

    #     data = self.report_instance.get_records("growth", [2019, 2020, 2021], dict())

    #     self.assertEqual(data, expected_data)

    def test_get_na_records_should_return_na_with_no_years_for_company_data(self):
        years = [2020, 2021]
        company = {"metrics": {2021: 3}}

        na_years = self.report_instance.get_na_year_records(company, years)

        self.assertEqual(na_years, {2020: "NA"})

    @parameterized.expand(
        [
            [{"size_cohort": ">$3 million", "margin_group": "Hyper growth"}, False],
            [{"size_cohort": ">$3 million", "margin_group": "Low growth"}, True],
            [{}, False],
        ]
    )
    def test_is_in_range_with_different_values_should_return_boolean(
        self, profile, expected_value
    ):
        conditions = {
            "size_cohort": [">$3 million", "30+"],
            "margin_group": ["Low growth"],
        }

        is_in_filters = self.report_instance.is_in_range(profile, **conditions)

        self.assertEqual(is_in_filters, expected_value)

    def test_anonymize_companies_values_when_is_successful_change_companies_name_and_metric_values(
        self,
    ):
        anonymized_companies_data = {
            "123": {
                "id": "123",
                "name": "123-xxxx",
                "metrics": {2020: "$20 million - $40 million"},
            }
        }
        self.mock_profile_range.get_range_from_value.return_value = (
            "$20 million - $40 million"
        )
        companies_data = {
            "123": {"id": "123", "name": "Company A", "metrics": {2020: 20}}
        }

        self.report_instance.anonymize_companies_values(
            "actuals_revenue", companies_data
        )

        self.assertEqual(companies_data, anonymized_companies_data)
        self.mock_profile_range.get_range_from_value.assert_called()

    @mock.patch(
        "src.service.by_metric_report.by_metric_report.ByMetricReport.get_records"
    )
    @mock.patch(
        "src.service.by_metric_report.by_metric_report.ByMetricReport.get_profiles"
    )
    def test_get_by_metric_records_when_is_sucessful_should_return_companies_metric_values(
        self, mock_get_profiles, mock_get_by_metric_records
    ):
        self.mock_repository.add_filters.return_value = dict()
        companies_data = {
            "1": {"id": "1", "name": "Test", "metrics": {2020: 1, 2021: 2}},
            "2": {"id": "2", "name": "Company", "metrics": {2020: 4, 2021: -1}},
        }
        profiles = {
            "1": {"size_cohort": "", "margin_group": ""},
            "2": {"size_cohort": "", "margin_group": ""},
        }
        mock_get_by_metric_records.return_value = companies_data
        mock_get_profiles.return_value = profiles
        expected_data = {
            "1": {"id": "1", "metrics": {2020: 1, 2021: 2}, "name": "Test"},
            "2": {"id": "2", "metrics": {2020: 4, 2021: -1}, "name": "Company"},
        }

        companies = self.report_instance.get_by_metric_records(
            "actuals_revenue", [2020, 2021]
        )

        self.assertEqual(companies, expected_data)
        mock_get_profiles.assert_called()
        mock_get_by_metric_records.assert_called()

    @mock.patch(
        "src.service.by_metric_report.by_metric_report.ByMetricReport.get_by_metric_records"
    )
    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    def test_get_by_metric_peers_when_is_called_from_universe_overview_should_return_empty_company(
        self, mock_set_company_permissions, mock_get_by_metric_records
    ):
        data = {
            "1": {"id": "1", "name": "Company A", "metrics": {2020: 1, 2021: 2}},
            "2": {"id": "2", "name": "Company B", "metrics": {2020: 4, 2021: -1}},
        }
        years = [2020, 2021]
        self.mock_repository.get_years.return_value = years
        mock_get_by_metric_records.return_value = data

        peers = self.report_instance.get_by_metric_peers(
            None, "user@test.com", "actuals_revenue", True, True
        )

        self.assertEqual(
            peers,
            {
                "years": years,
                "company_comparison_data": {},
                "peers_comparison_data": [*data.values()],
                "averages": {2020: 2, 2021: 0},
            },
        )
        mock_set_company_permissions.assert_called()

    @mock.patch(
        "src.service.by_metric_report.by_metric_report.ByMetricReport.get_by_metric_records"
    )
    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    def test_get_by_metric_peers_when_is_called_from_company_report_should_not_return_empty_company(
        self, mock_set_company_permissions, mock_get_by_metric_records
    ):
        data = {
            "1": {"id": "1", "name": "Company A", "metrics": {2020: 1, 2021: 2}},
            "2": {"id": "2", "name": "Company B", "metrics": {2020: 4, 2021: -1}},
        }
        years = [2020, 2021]
        self.mock_repository.get_years.return_value = years
        mock_get_by_metric_records.return_value = data.copy()

        peers = self.report_instance.get_by_metric_peers(
            "1", "user@test.com", "actuals_revenue", False, True
        )

        self.assertEqual(
            peers,
            {
                "years": years,
                "company_comparison_data": data["1"],
                "peers_comparison_data": [data["2"]],
                "averages": {2020: 2, 2021: 0},
            },
        )
        mock_set_company_permissions.assert_called()

    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    def test_get_by_metric_peers_when_call_fails_should_raise_an_exception(
        self, mock_set_company_permissions
    ):
        mock_set_company_permissions.side_effect = Exception("error")

        with self.assertRaises(Exception) as context:
            self.report_instance.get_by_metric_peers(
                None, "user@test.com", "actuals_revenue", True, True
            )

        self.assertEqual(str(context.exception), "error")

    @mock.patch(
        "src.service.by_metric_report.by_metric_report.ByMetricReport.get_by_metric_records"
    )
    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    def test_get_by_metric_peers_when_user_does_not_have_permissions_should_return_anynomized_data(
        self, mock_set_company_permissions, mock_get_by_metric_records
    ):
        data = {
            "1": {"id": "1", "name": "Company A", "metrics": {2020: 1}},
        }
        years = [2020, 2021]
        self.mock_repository.get_years.return_value = years
        mock_get_by_metric_records.return_value = data.copy()
        self.mock_profile_range.get_range_from_value.return_value = (
            "$20 million - $40 million"
        )
        anonymized_company = {
            "id": "1",
            "name": "1-xxxx",
            "metrics": {2020: "$20 million - $40 million"},
        }

        peers = self.report_instance.get_by_metric_peers(
            "1", "user@test.com", "actuals_revenue", False, False
        )

        self.assertEqual(
            peers,
            {
                "years": years,
                "company_comparison_data": anonymized_company,
                "peers_comparison_data": [],
                "averages": {2020: 1, 2021: "NA"},
            },
        )
        mock_set_company_permissions.assert_called()
        mock_get_by_metric_records.assert_called()

    @mock.patch(
        "src.service.by_metric_report.by_metric_report.ByMetricReport.get_by_metric_records"
    )
    @mock.patch(
        "src.utils.company_anonymization.CompanyAnonymization.set_company_permissions"
    )
    @mock.patch(
        "src.service.by_metric_report.by_metric_report.ByMetricReport.anonymize_companies_values"
    )
    def test_get_by_metric_peers_without_permission_and_with_headcount_shouldnt_call_anonymization(
        self,
        mock_anonymize_companies_values,
        mock_set_company_permissions,
        mock_get_by_metric_records,
    ):
        data = {}
        years = [2020, 2021]
        self.mock_repository.get_years.return_value = years
        mock_get_by_metric_records.return_value = data.copy()

        self.report_instance.get_by_metric_peers(
            "1", "user@test.com", "actuals_headcount", False, False
        )

        mock_set_company_permissions.assert_called()
        mock_anonymize_companies_values.assert_not_called()
