from unittest import TestCase, mock
import logging
from unittest.mock import Mock
from src.tests.data.data_reader import read
from src.service.company_details.company_details_service import CompanyDetails
from src.service.calculator.calculator_service import CalculatorService

logger = logging.getLogger()
logger.setLevel(logging.INFO)

company_service_class = (
    "src.service.company_details.company_details_service.CompanyDetails"
)


class TestCompanyDetailsService(TestCase):
    def setUp(self):
        self.mock_session = Mock()
        self.mock_query_builder = Mock()
        self.mock_response_sql = Mock()
        self.mock_profile_range = Mock()
        self.company = read("sample_company.json")
        self.details_service_instance = CompanyDetails(
            self.mock_session,
            self.mock_response_sql,
            self.mock_response_sql,
            CalculatorService(logger),
            self.mock_profile_range,
            logger,
        )

    def get_company_description(self):
        return {
            field: self.company[field]
            for field in self.company
            if field not in ["scenarios", "size_cohort", "margin_group"]
        }

    def mock_response_query_sql(self, response: dict):
        attrs = {"process_query_result.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def mock_response_list_query_sql(self, response: list):
        attrs = {"process_query_list_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def mock_process_revenue_profile_results(self, response: tuple):
        attrs = {"process_revenue_profile_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def test_get_company_description_should_return_dict(self):
        expected_description = self.get_company_description()
        self.mock_response_query_sql(expected_description)

        description = self.details_service_instance.get_company_description(
            self.company["id"]
        )

        self.assertTrue(description, expected_description)

    def test_get_company_description_fails_should_return_empty_dict(self):
        self.mock_session.execute.side_effect = Exception("error")

        description = self.details_service_instance.get_company_description(
            self.company["id"]
        )

        self.assertEqual(description, dict())

    def test_get_profile_records_should_return_records(self):
        expected_records = (13, 20)
        self.mock_process_revenue_profile_results(expected_records)

        records = self.details_service_instance.get_profile_records(self.company["id"])

        self.assertEqual(records, expected_records)

    def test_get_profile_records_fail_should_return_None(self):
        self.mock_session.execute.side_effect = Exception("error")

        records = self.details_service_instance.get_profile_records(self.company["id"])

        self.assertIsNone(records)

    def test_get_company_profiles_without_records_should_raise_error(self):
        self.mock_process_revenue_profile_results(None)
        expected_profiles = {"size_cohort": "NA", "margin_group": "NA"}

        profiles = self.details_service_instance.get_company_profiles(
            self.company["id"]
        )

        self.assertEqual(profiles, expected_profiles)

    def get_range(self, value: float, ranges: list = None) -> str:
        for range in ranges:
            if value == range.get("min_value"):
                return range.get("label")
        return "NA"

    def test_get_company_profiles_should_return_valid_dict(self):
        sizes = [
            {"label": "$13-$20", "min_value": 13, "max_value": 20},
            {"label": "$20+", "min_value": 20, "max_value": None},
        ]
        self.mock_process_revenue_profile_results((13, 20))
        self.mock_profile_range.get_profile_ranges.return_value = sizes
        self.mock_profile_range.get_range_from_value.side_effect = self.get_range
        expected_profiles = {"size_cohort": "$13-$20", "margin_group": "NA"}

        profiles = self.details_service_instance.get_company_profiles(
            self.company["id"]
        )

        self.assertEqual(profiles, expected_profiles)

    def test_get_total_number_of_scenarios_should_return_int(self):
        expected_total = self.company["scenarios"]["total"]
        self.mock_response_query_sql({"count": expected_total})

        total = self.details_service_instance.get_total_number_of_scenarios(
            self.company["id"]
        )

        self.assertEqual(total, expected_total)

    def test_get_total_number_of_scenarios_fails_should_return_None(self):
        self.mock_session.execute.side_effect = Exception("error")

        total = self.details_service_instance.get_total_number_of_scenarios(
            self.company["id"]
        )

        self.assertIsNone(total)

    def test_convert_metric_values(self):
        metrics = self.company["scenarios"]["metrics"].copy()

        self.details_service_instance.convert_metric_values(metrics)

        self.assertEqual(metrics, self.company["scenarios"]["metrics"])

    def test_get_company_scenarios_should_return_list(self):
        expected_scenarios = self.company["scenarios"]["metrics"].copy()
        self.mock_response_list_query_sql(expected_scenarios)

        scenarios = self.details_service_instance.get_company_scenarios(
            self.company["id"], 0, 1
        )

        self.assertEqual(scenarios, expected_scenarios)

    def test_get_company_scenarios_fails_should_return_empty_list(self):
        self.mock_session.execute.side_effect = Exception("error")

        scenarios = self.details_service_instance.get_company_scenarios(
            self.company["id"], 0, 1
        )

        self.assertEqual(scenarios, [])

    @mock.patch(f"{company_service_class}.get_total_number_of_scenarios")
    @mock.patch(f"{company_service_class}.get_company_scenarios")
    @mock.patch(f"{company_service_class}.get_company_profiles")
    def test_get_company_details_with_valid_id_should_return_dict(
        self,
        mock_get_company_profiles,
        mock_get_company_scenarios,
        mock_get_total_number_of_scenarios,
    ):
        expected_company = self.company.copy()
        self.mock_response_query_sql(self.get_company_description())
        mock_get_company_profiles.return_value = {
            "size_cohort": expected_company["size_cohort"],
            "margin_group": expected_company["margin_group"],
        }
        mock_get_company_scenarios.return_value = expected_company["scenarios"][
            "metrics"
        ]
        mock_get_total_number_of_scenarios.return_value = expected_company["scenarios"][
            "total"
        ]

        company = self.details_service_instance.get_company_details(self.company["id"])

        self.assertEqual(company, expected_company)

    def test_get_company_details_fails_should_raise_exception(self):
        self.mock_response_query_sql(dict())
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.details_service_instance.get_company_details(self.company["id"])
            )

            self.assertTrue("Company not found" in context.exception)
            self.assertEqual(exception, Exception)

    def test_get_company_details_with_invalid_id_should_raise_exception(self):
        self.mock_response_query_sql(dict())
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.details_service_instance.get_company_details("")
            )

            self.assertTrue("Invalid company id" in context.exception)
            self.assertEqual(exception, Exception)
