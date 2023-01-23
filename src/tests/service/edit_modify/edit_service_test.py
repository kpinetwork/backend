from collections import defaultdict
import logging
from unittest import TestCase, mock
from unittest.mock import Mock
from src.service.edit_modify.edit_service import EditModifyService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestEditModifyService(TestCase):
    def setUp(self):
        self.mock_repository = Mock()
        self.mock_scenario_service = Mock()
        self.mock_metric_service = Mock()
        self.edit_service = EditModifyService(
            self.mock_repository,
            self.mock_scenario_service,
            self.mock_metric_service,
            logger,
        )
        self.company = {
            "id": "9c5d17a4-186c-461e-955b-dcafd6b45fa7",
            "description": {"name": "Test Company"},
            "scenarios": [
                {
                    "scenario_id": "073b57d5-d809-449e-8c6d-148a4f96bfb6",
                    "scenario": "Actuals",
                    "year": 2021,
                    "metric": "Revenue",
                    "metric_id": "1842fe06-0ece-4038-ab6a-00eb8260b524",
                    "value": 36.15,
                    "period": "Q1",
                }
            ],
        }

        self.edit_modify_data = {
            "123": {
                "id": "123",
                "name": "Sample Company",
                "sector": "Semiconductors",
                "vertical": "Education",
                "inves_profile_name": "Public",
                "scenarios": [
                    {
                        "scenario_id": None,
                        "scenario": "Actuals",
                        "year": "2020",
                        "metric_id": None,
                        "metric": "Revenue",
                        "value": 3.4,
                        "period": "Q1",
                    },
                    {},
                    {},
                    {},
                    {},
                    {},
                    {},
                    {},
                    {},
                    {},
                    {},
                    {},
                    {},
                    {},
                    {},
                    {},
                    {},
                    {},
                    {},
                    {},
                ],
            }
        }

        self.scenario = {
            "company_id": "9c5d17a4-186c-461e-955b-dcafd6b45fa7",
            "scenario": "Actuals",
            "year": 2018,
            "metric": "Revenue",
            "value": 45.6,
            "period": "Q1",
        }

        self.fetched_companies = [
            {
                "id": "123",
                "name": "Sample Company",
                "sector": "Semiconductors",
                "vertical": "Education",
                "inves_profile_name": "Public",
                "scenario": "Actuals-2020",
                "metric": "Revenue",
                "value": 3.4,
                "period": "Q1",
            },
            {
                "id": "124",
                "name": "Test Company",
                "sector": "Online media",
                "vertical": "Real Estate",
                "inves_profile_name": "Public",
                "scenario": "Budget-2020",
                "metric": "Ebitda",
                "value": 8.4,
                "period": "Q1",
            },
        ]

        self.scenarios_by_type = [
            {"scenario": "Actuals-2020", "metric": "Revenue"},
        ]

        self.rows = {
            "headers": [
                "Unique ID",
                "Name",
                "Sector",
                "Vertical",
                "Investor Profile",
                "Actuals",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "Budget",
                "",
                "",
                "",
                "",
            ],
            "metrics": [
                "",
                "",
                "",
                "",
                "",
                "Revenue",
                "",
                "",
                "",
                "",
                "Ebitda",
                "",
                "",
                "",
                "",
                "Ebitda",
                "",
                "",
                "",
                "",
            ],
            "years": [
                "",
                "",
                "",
                "",
                "",
                "2020",
                "",
                "",
                "",
                "",
                "2020",
                "",
                "",
                "",
                "",
                "2020",
                "",
                "",
                "",
                "",
            ],
            "periods": [
                "",
                "",
                "",
                "",
                "",
                "Q1",
                "Q2",
                "Q3",
                "Q4",
                "Full-year",
                "Q1",
                "Q2",
                "Q3",
                "Q4",
                "Full-year",
                "Q1",
                "Q2",
                "Q3",
                "Q4",
                "Full-year",
            ],
        }

    def get_scenario_added(
        self, scenario: dict, added: bool, error: str = None
    ) -> dict:
        scenario_added = defaultdict(list)
        response = {
            "scenario": f"{scenario['scenario']}-{scenario['year']}",
            "metric": f"{scenario['metric']}",
            "added": added,
        }
        if error:
            response["error"] = error

        scenario_added[scenario["company_id"]] = [response]
        return scenario_added

    @mock.patch.object(EditModifyService, "_EditModifyService__add_scenarios")
    def test_add_scenarios_fail_should_raise_exception(self, mock_add_scenarios):
        mock_add_scenarios.side_effect = Exception("error")

        scenarios = self.edit_service.add_data([])

        self.assertEqual(scenarios, dict())

    def test_add_scenario_success_should_return_added_true(self):
        scenario = self.scenario.copy()
        expected_scenario = self.get_scenario_added(scenario, True)

        scenarios = self.edit_service.add_data([scenario])

        self.assertEqual(scenarios, expected_scenario)

    def test_add_scenario_fail_should_return_added_false(self):
        scenario = self.scenario.copy()
        scenario["scenario"] = "Custom"
        message = "Invalid scenario name"
        expected_scenario = self.get_scenario_added(scenario, False, message)
        self.mock_scenario_service.add_company_scenario.side_effect = Exception(message)

        scenarios = self.edit_service.add_data([scenario])

        self.assertEqual(scenarios, expected_scenario)

    def test_edit_modify_data(self):
        scenario = self.scenario.copy()
        company = self.company.copy()
        expected_result = {
            "edited": True,
            "added": self.get_scenario_added(scenario, True),
        }
        self.mock_repository.edit_data.return_value = True

        response = self.edit_service.edit_modify_data(
            {"edit": [company], "add": [scenario]}
        )

        self.assertEqual(response, expected_result)

    def test_get_data_when_query_calls_are_successful_should_return_rows(self):
        expected_response = {
            "headers": [
                "Unique ID",
                "Name",
                "Sector",
                "Vertical",
                "Investor Profile",
                "Actuals",
                "",
                "",
                "",
                "",
                "Budget",
                "",
                "",
                "",
                "",
            ],
            "metrics": [
                "",
                "",
                "",
                "",
                "",
                "Revenue",
                "",
                "",
                "",
                "",
                "Revenue",
                "",
                "",
                "",
                "",
            ],
            "years": [
                "",
                "",
                "",
                "",
                "",
                "2020",
                "",
                "",
                "",
                "",
                "2020",
                "",
                "",
                "",
                "",
            ],
            "periods": [
                "",
                "",
                "",
                "",
                "",
                "Q1",
                "Q2",
                "Q3",
                "Q4",
                "Full-year",
                "Q1",
                "Q2",
                "Q3",
                "Q4",
                "Full-year",
            ],
            "companies": {
                "123": {
                    "id": "123",
                    "name": "Sample Company",
                    "sector": "Semiconductors",
                    "vertical": "Education",
                    "inves_profile_name": "Public",
                    "scenarios": [
                        {
                            "scenario_id": None,
                            "scenario": "Actuals",
                            "year": "2020",
                            "metric_id": None,
                            "metric": "Revenue",
                            "value": 3.4,
                            "period": "Q1",
                        },
                        {},
                        {},
                        {},
                        {},
                        {},
                        {},
                        {},
                        {},
                        {},
                        {},
                        {},
                        {},
                        {},
                        {},
                    ],
                },
                "124": {
                    "id": "124",
                    "name": "Test Company",
                    "sector": "Online media",
                    "vertical": "Real Estate",
                    "inves_profile_name": "Public",
                    "scenarios": [
                        {},
                        {},
                        {},
                        {},
                        {},
                        {},
                        {},
                        {},
                        {},
                        {},
                        {},
                        {},
                        {},
                        {},
                        {},
                    ],
                },
            },
        }
        self.mock_metric_service.get_metric_types.return_value = ["Revenue"]
        self.mock_repository.get_scenarios_by_type.return_value = self.scenarios_by_type
        self.mock_repository.get_companies_records.return_value = self.fetched_companies

        response = self.edit_service.get_data()
        self.assertEqual(response, expected_response)

    def test_get_data_when_there_are_not_scenarios_should_empty_scenarios(self):
        expected_response = {
            "headers": [
                "Unique ID",
                "Name",
                "Sector",
                "Vertical",
                "Investor Profile",
            ],
            "metrics": ["", "", "", "", ""],
            "years": ["", "", "", "", ""],
            "periods": ["", "", "", "", ""],
            "companies": {
                "123": {
                    "id": "123",
                    "name": "Sample Company",
                    "sector": "Semiconductors",
                    "vertical": "Education",
                    "inves_profile_name": "Public",
                    "scenarios": [{}, {}, {}, {}, {}],
                },
                "124": {
                    "id": "124",
                    "name": "Test Company",
                    "sector": "Online media",
                    "vertical": "Real Estate",
                    "inves_profile_name": "Public",
                    "scenarios": [{}, {}, {}, {}, {}],
                },
            },
        }
        self.mock_metric_service.get_metric_types.return_value = []
        self.mock_repository.get_scenarios_by_type.return_value = []
        self.mock_repository.get_companies_records.return_value = self.fetched_companies
        response = self.edit_service.get_data()

        self.assertEqual(response, expected_response)

    def test_build_companies_rows_success(self):
        expected_response = self.edit_modify_data
        expected_response.update(
            {
                "124": {
                    "id": "124",
                    "name": "Test Company",
                    "sector": "Online media",
                    "vertical": "Real Estate",
                    "inves_profile_name": "Public",
                    "scenarios": [
                        {},
                        {},
                        {},
                        {},
                        {},
                        {},
                        {},
                        {},
                        {},
                        {},
                        {
                            "scenario_id": None,
                            "scenario": "Budget",
                            "year": "2020",
                            "metric_id": None,
                            "metric": "Ebitda",
                            "value": 8.4,
                            "period": "Q1",
                        },
                        {},
                        {},
                        {},
                        {},
                        {},
                        {},
                        {},
                        {},
                        {},
                    ],
                }
            }
        )
        self.mock_metric_service.get_metric_types.return_value = ["Revenue", "Ebitda"]

        response = self.edit_service._EditModifyService__build_companies_rows(
            self.fetched_companies,
            self.rows,
        )

        self.assertEqual(response, expected_response)

    def test_slice_row(self):
        expected_response = ["Ebitda", ""]
        row = ["Ebitda", "", "Revenue", ""]

        response = self.edit_service._EditModifyService__slice_row(row, 0, 2)

        self.assertEqual(response, expected_response)

    def test_get_scenarios_and_filters_invalid_scenario_should_return_base_scenarios(
        self,
    ):
        conditions = {"scenarios": "Actuals margin"}

        (
            scenarios,
            filters,
        ) = self.edit_service._EditModifyService__get_scenarios_and_filters(
            **conditions
        )

        self.assertEqual(scenarios, ["Actuals", "Budget"])
        self.assertEqual(
            filters, {"financial_scenario.type": ["'Actuals'", "'Budget'"]}
        )

    def test_get_scenarios_and_filters_should_dict_with_conditions(self):
        conditions = {"name": ["Sample Company"], "scenarios": ["Actuals"]}
        expected_filters = {
            "company.name": ["'Sample Company'"],
            "financial_scenario.type": ["'Actuals'"],
        }

        (
            scenarios,
            filters,
        ) = self.edit_service._EditModifyService__get_scenarios_and_filters(
            **conditions
        )

        self.assertEqual(scenarios, ["Actuals"])
        self.assertEqual(filters, expected_filters)
