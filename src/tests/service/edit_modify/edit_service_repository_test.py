from unittest import TestCase
import logging
from unittest.mock import Mock, patch
from src.service.metric.metric_type_service import MetricTypesService
from src.service.edit_modify.edit_modify_repository import EditModifyRepository

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestEditModifyRepository(TestCase):
    def setUp(self):
        self.mock_session = Mock()
        self.mock_query_builder = Mock()
        self.mock_response_sql = Mock()
        self.metrics_service = MetricTypesService(
            self.mock_session, self.mock_query_builder, self.mock_response_sql, logger
        )
        self.repository = EditModifyRepository(
            self.mock_session,
            self.mock_query_builder,
            self.mock_response_sql,
            self.metrics_service,
            logger,
        )
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

    def mock_response_list_query_sql(self, response):
        attrs = {"process_query_list_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def test_get_companies_records_should_return_companies_list_when_successful_call(
        self,
    ):
        self.mock_response_list_query_sql(self.fetched_companies)

        companies = self.repository.get_companies_records({"sector": "Online media"})

        self.assertEqual(companies, self.fetched_companies)

    def test_get_companies_records_should_return_empty_dict_when_call_fails(self):
        self.mock_session.execute.side_effect = Exception("error")

        companies = self.repository.get_companies_records(dict())

        self.assertEqual(companies, dict())

    @patch("src.service.metric.metric_type_service.MetricTypesService.get_metric_types")
    def test_get_scenarios_by_type_should_return_scenarios_list_when_successful_call(
        self, mock_get_metric_type
    ):
        mock_get_metric_type.return_value = ["Actuals", "Budget"]
        scenarios_expected = [{"scenario": "Actuals-2020", "metric": "Revenue"}]
        self.mock_response_list_query_sql(scenarios_expected)

        scenarios = self.repository.get_scenarios_by_type("Actuals")

        self.assertEqual(scenarios, scenarios_expected)

    def test_get_scenarios_by_type_should_return_empty_list_when_call_fails(self):
        self.mock_session.execute.side_effect = Exception("error")

        scenarios = self.repository.get_scenarios_by_type("Actuals")

        self.assertEqual(scenarios, [])

    @patch.object(
        EditModifyRepository, "_EditModifyRepository__get_company_description_query"
    )
    def test_edit_date_should_return_true_when_query_execution_is_successful(
        self, mock_get_company_description_query
    ):
        company = self.company.copy()
        mock_get_company_description_query.return_value = ""

        edited = self.repository.edit_data([company])

        self.assertTrue(edited)

    @patch.object(EditModifyRepository, "_EditModifyRepository__get_companies_query")
    def test_edit_date_should_return_true_when_there_are_companies_queries(
        self, mock_get_companies_query
    ):
        companies = [self.fetched_companies[0]]
        mock_get_companies_query.return_value = []

        edited = self.repository.edit_data(companies)

        self.assertTrue(edited)

    @patch.object(EditModifyRepository, "_EditModifyRepository__get_companies_query")
    def test_edit_date_should_return_false_when_query_execution_fails(
        self, mock_get_companies_query
    ):
        companies = [self.fetched_companies[0]]
        mock_get_companies_query.side_effect = Exception("error")

        edited = self.repository.edit_data(companies)

        self.assertFalse(edited)

    def test__get_valid_conditions_success(self):
        self.repository._EditModifyRepository__get_company_description_query(
            "id", {"name": "Test Company"}
        )

        self.mock_query_builder.assert_not_called()
