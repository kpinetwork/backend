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
        
        response = self.response_sql_instance.process_query_average_result([expected_average])
        
        self.assertEqual(response,expected_average)


    def test_process_query_average_result_without_average_in_dict(self):
        record = {"average": None}
        expected_average = dict()

        response = self.response_sql_instance.process_query_average_result([record])
        
        self.assertEqual(response,expected_average)
