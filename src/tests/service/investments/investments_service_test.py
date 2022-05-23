from unittest import TestCase
import logging
from unittest.mock import Mock
from src.service.investments.investments_service import InvestmentsService
from src.utils.company_anonymization import CompanyAnonymization

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestInvestmentsService(TestCase):
    def setUp(self):
        self.investment = {
            "company_id": "1ce0d39b-7c0e-428f-9ab6-3889ab72a154",
            "investment_date": "2021-01",
            "divestment_date": "2021-01",
            "round": 1,
            "structure": "Primary and Secondary",
            "ownership": "Minority",
            "investor_type": "Early stage VC",
        }
        self.request_body = {
            "invest": "2020-09",
            "round": 1,
            "structure": "Primary",
            "ownership": "Majority",
            "investor_type": "Public",
        }
        self.mock_session = Mock()
        self.mock_query_builder = Mock()
        self.mock_response_sql = Mock()
        self.investments_service_instance = InvestmentsService(
            self.mock_session,
            self.mock_query_builder,
            logger,
            self.mock_response_sql,
            CompanyAnonymization(object()),
        )
        return

    def mock_response_list_query_sql(self, response):
        attrs = {"process_query_list_results.return_value": response}
        self.mock_response_sql.configure_mock(**attrs)

    def test_get_company_investments_success(self):
        self.mock_response_list_query_sql([self.investment])

        get_investments_out = self.investments_service_instance.get_company_investments(
            self.investment.get("company_id")
        )

        self.assertEqual(get_investments_out, [self.investment])
        self.investments_service_instance.session.execute.assert_called_once()

    def test_get_company_investments_with_empty_response_success(self):
        self.mock_response_list_query_sql([])

        get_company_out = self.investments_service_instance.get_company_investments(
            self.investment.get("company_id")
        )

        self.assertEqual(get_company_out, [])
        self.investments_service_instance.session.execute.assert_called_once()

    def test_get_company_investment_with_empty_id(self):
        get_company_out = self.investments_service_instance.get_company_investments("")

        self.assertEqual(get_company_out, [])
        self.investments_service_instance.session.execute.assert_not_called()

    def test_get_company_failed(self):
        self.investments_service_instance.session.execute.side_effect = Exception(
            "error"
        )
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.investments_service_instance.get_company_investments(
                    self.investment.get("company_id")
                )
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.investments_service_instance.session.execute.assert_called_once()

    def test_add_investment_success_without_investor(self):
        response = self.investments_service_instance.add_investment(
            self.investment.get("company_id"), self.request_body
        )

        self.assertEqual(response, self.request_body)
        self.investments_service_instance.session.execute.assert_called_once()

    def test_add_investment_success_with_investor(self):
        request_investment = self.request_body.copy()
        request_investment.update({"investor": "Sample firm name"})

        response = self.investments_service_instance.add_investment(
            self.investment.get("company_id"), request_investment
        )

        self.assertEqual(response, request_investment)
        self.investments_service_instance.session.execute.assert_called_once()

    def test_add_investment_return_empty_value_without_id(self):
        response = self.investments_service_instance.add_investment(
            "", self.request_body
        )

        self.assertEqual(response, {})
        self.investments_service_instance.session.execute.assert_not_called()

    def test_add_investment_failed(self):
        self.investments_service_instance.session.execute.side_effect = Exception(
            "error"
        )
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.investments_service_instance.add_investment(
                    self.investment.get("company_id"), self.request_body
                )
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.investments_service_instance.session.execute.assert_called_once()
