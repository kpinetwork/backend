import logging
from datetime import datetime
from unittest import TestCase, mock
from unittest.mock import Mock
from parameterized import parameterized
from src.service.scenario.scenario_service import ScenarioService

logger = logging.getLogger()
logger.setLevel(logging.INFO)

message = "Cannot add new scenario:"
next_year = datetime.now().year + 2
args = {
    "company_id": "123",
    "scenario": "Actuals",
    "year": 2020,
    "period_name": "Q1",
    "metric": "Revenue",
    "value": 56.78,
}


def get_dict_with_different_value(field: str, value: str) -> dict:
    data = args.copy()
    data[field] = value
    return data


class DummyResponse:
    def __init__(self, values: dict):
        self.values = values

    def fetchall(self):
        return self.values


class TestScenarioService(TestCase):
    def setUp(self):

        self.mock_session = Mock()
        self.mock_query_builder = Mock()
        self.mock_response_sql = Mock()
        self.mock_metric_service = Mock()
        self.scenario_service_instance = ScenarioService(
            self.mock_session, self.mock_query_builder, self.mock_metric_service, logger
        )

    def get_metric_types_response(self, response: list):
        self.mock_metric_service.get_metric_types.return_value = ["Revenue", "Ebitda"]
        return self

    @parameterized.expand(
        [
            [
                get_dict_with_different_value("scenario", "Budget margin"),
                f"{message} Invalid scenario type",
            ],
            [
                get_dict_with_different_value("metric", "Ebitda margin"),
                f"{message} Invalid metric name",
            ],
            [get_dict_with_different_value("year", 12), f"{message} Invalid year"],
            [
                get_dict_with_different_value("value", "23abc"),
                f"{message} Invalid value, must be a number",
            ],
            [
                get_dict_with_different_value("year", next_year),
                f"{message} The actual scenario year cannot be greater than the current year",
            ],
            [
                get_dict_with_different_value("period_name", "Q5"),
                f"{message} Invalid metric period",
            ],
        ]
    )
    def test_add_scenario_with_invalid_values_should_fail(
        self, args: dict, error_message: str
    ):
        self.get_metric_types_response(["Revenue", "Ebitda"])
        with self.assertRaises(Exception) as context:
            self.scenario_service_instance.add_company_scenario(**args)

        self.assertEqual(str(context.exception), error_message)

    def test_add_scenario_with_invalid_company_id_should_fail(self):
        self.get_metric_types_response(["Revenue", "Ebitda"])
        self.mock_session.execute.return_value = DummyResponse({})

        with self.assertRaises(Exception) as context:
            self.scenario_service_instance.add_company_scenario(**args)

        self.assertEqual(str(context.exception), f"{message} Company doesn't exist")

    def test_add_scenario_with_repeated_scenario_should_fail(self):
        self.get_metric_types_response(["Revenue", "Ebitda"])
        self.mock_session.execute.return_value = DummyResponse(
            {"name": "Actuals", "period_name": "Q1"}
        )

        with self.assertRaises(Exception) as context:
            self.scenario_service_instance.add_company_scenario(**args)

        self.assertEqual(str(context.exception), f"{message} Scenario already exists")

    @mock.patch.object(ScenarioService, "_ScenarioService__verify_company_data")
    def test_add_scenario_success_should_return_dict(self, mock_verify_company_data):
        fields = ["id", "name", "metric_id", "period_name"]
        expected_name = f"{args['scenario']}-{args['year']}"

        scenario = self.scenario_service_instance.add_company_scenario(**args)

        self.assertEqual([*scenario], fields)
        self.assertEqual(scenario["name"], expected_name)
