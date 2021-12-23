from unittest import TestCase
from src.utils.response_sql import ResponseSQL


class TestResponseBuilder(TestCase):
    def setUp(self):
        self.response_sql_instance = ResponseSQL()
        self.record = {
            "id": "f0e51d91-a55a-4f3b-9312-d2bab03b8020",
            "name": "Revenue",
            "value": "12",
            "type": "standard",
            "data_type": "currency",
            "period_id": "f308846b-e937-4f0d-9346-cc6312ae67fb",
            "company_id": "2e877aea-afc0-4aa1-80eb-094dd3c3aae1",
            "company_name": "company test",
        }
        pass

    def test_process_query_result_success(self):
        records = [self.record]

        response = self.response_sql_instance.process_query_result(records)

        self.assertEqual(response, self.record)

    def test_process_query_result_with_empty_response(self):
        records = []

        response = self.response_sql_instance.process_query_result(records)

        self.assertEqual(response, {})

    def test_process_query_list_results_success(self):
        records = [self.record]

        response = self.response_sql_instance.process_query_list_results(records)

        self.assertEqual(response, [self.record])

    def test_process_query_list_results_with_empty_response(self):
        records = []

        response = self.response_sql_instance.process_query_list_results(records)

        self.assertEqual(response, [])

    def test_process_query_average_result_with_average_in_dict(self):
        expected_average = {"average": 123}

        response = self.response_sql_instance.process_query_average_result(
            [expected_average]
        )

        self.assertEqual(response, expected_average)

    def test_process_query_average_result_without_average_in_dict(self):
        record = {"average": None}
        expected_average = dict()

        response = self.response_sql_instance.process_query_average_result([record])

        self.assertEqual(response, expected_average)

    def test_process_scenarios_list_results_with_one_scenario_success(self):
        records = [self.record]
        expected_record = [
            {
                "company": {
                    "id": self.record.get("company_id"),
                    "name": self.record.get("company_name"),
                },
                "scenarios": [self.record],
            }
        ]

        response = self.response_sql_instance.process_scenarios_list_results(records)
        self.assertEqual(response, expected_record)

    def test_process_scenarios_list_results_with_more_than_one_scenario_success(self):
        record2 = self.record.copy()
        record2["id"] = "g0e51d91-a55a-4f3b-9312-d2bab03b8020"
        records = [self.record, record2]
        expected_record = [
            {
                "company": {
                    "id": self.record.get("company_id"),
                    "name": self.record.get("company_name"),
                },
                "scenarios": [self.record, record2],
            }
        ]

        response = self.response_sql_instance.process_scenarios_list_results(records)
        self.assertEqual(response, expected_record)

    def test_process_metrics_group_by_size_cohort_results_success(self):
        records = [
            {"size_cohort": "1", "growth": "12"},
            {"size_cohort": "2", "growth": "178"},
            {"size_cohort": "1", "margin": "34"},
        ]
        expected_record = {
            "1": [
                {"size_cohort": "1", "growth": "12"},
                {"size_cohort": "1", "margin": "34"},
            ],
            "2": [{"size_cohort": "2", "growth": "178"}],
        }

        response = (
            self.response_sql_instance.process_metrics_group_by_size_cohort_results(
                records
            )
        )
        self.assertEqual(response, expected_record)

    def test_process_metrics_group_by_size_cohort_results_with_empty_list(self):
        records = []
        expected_record = {}

        response = (
            self.response_sql_instance.process_metrics_group_by_size_cohort_results(
                records
            )
        )
        self.assertEqual(response, expected_record)

    def test_proccess_comparison_results_update_success_dict(self):
        records = [{"id": "id", "name": "test"}, {"id": "id", "extra": "test"}]
        expected_out = {"id": {"id": "id", "name": "test", "extra": "test"}}

        response = self.response_sql_instance.proccess_comparison_results(records)

        self.assertEqual(response, expected_out)

    def test_proccess_comparison_results_with_empty_list(self):
        records = []

        response = self.response_sql_instance.proccess_comparison_results(records)

        self.assertEqual(response, dict())
