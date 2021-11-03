from unittest import TestCase
from unittest.mock import Mock
from src.service.company.company_service import CompanyService


class TestCompanyService(TestCase):
    def setUp(self):
        self.company = {
            "id": "1ad345fg",
            "name": "Test Company",
            "from_date": "2020-01-01",
            "fiscal_year": "2020-01-01",
            "sector": "Science",
            "vertical": "Technology",
            "inves_profile_name": "Small",
        }
        self.mock_session = Mock()
        self.mock_query_sql = Mock()
        self.company_service_instance = CompanyService(
            self.mock_session, self.mock_query_sql
        )
        return

    def test_get_company_success(self):
        self.company_service_instance.session.execute.return_value = iter(
            [self.company]
        )

        get_company_out = self.company_service_instance.get_company(
            self.company.get("id")
        )

        self.assertEqual(get_company_out, self.company)
        self.company_service_instance.session.execute.assert_called_once()

    def test_get_company_with_empty_id(self):
        self.company_service_instance.session.execute.return_value = iter(
            [self.company]
        )

        get_company_out = self.company_service_instance.get_company("")

        self.assertEqual(get_company_out, dict())
        self.company_service_instance.session.execute.assert_not_called()

    def test_get_company_failed(self):
        self.company_service_instance.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.company_service_instance.get_company(self.company.get("id"))
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.company_service_instance.session.execute.assert_called_once()

    def test_get_all_companies_success(self):
        self.company_service_instance.session.execute.return_value = iter(
            [self.company]
        )

        get_all_companies_out = self.company_service_instance.get_all_companies()

        self.assertEqual(get_all_companies_out, [self.company])
        self.assertEqual(len(get_all_companies_out), len([self.company]))
        self.company_service_instance.session.execute.assert_called_once()

    def test_get_all_companies_failed(self):
        self.company_service_instance.session.execute.side_effect = Exception("error")
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.company_service_instance.get_all_companies()
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.company_service_instance.session.execute.assert_called_once()
