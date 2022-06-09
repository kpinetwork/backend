import logging
from unittest import TestCase, mock
from unittest.mock import Mock
from update_data_service import (
    UpdateDataService,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestUpdateDataService(TestCase):
    def setUp(self):
        self.company = {
            "id": "1244",
            "name": "Sample Company 2",
            "sector": "software",
            "Vertical": "education",
            "invest_profile_name": "public",
            "is_public": True,
        }
        self.metric = {
            "id": "123",
            "name": "Sample metric",
            "value": 4,
            "type": "currency",
            "data_type": "currency",
            "period_id": "1234",
            "company_id": "134",
        }
        self.mock_session = Mock()
        self.mock_query_builder = Mock()
        self.mock_response_sql = Mock()
        self.update_data_service_instance = UpdateDataService(
            self.mock_session, self.mock_query_builder, logger, self.mock_response_sql
        )
        return

    @mock.patch("update_data_service.UpdateDataService.get_queries_joined")
    def test_update_data_success(self, mock_get_queries_joined):
        mock_get_queries_joined.return_value = """
        UPDATE company
        VALUES("123", "Sample Company","Software", "Education", "Public", true)
        """

        self.update_data_service_instance.update_data([self.company], [self.metric])

        self.update_data_service_instance.session.execute.assert_called_once()

    def test_update_data_failed(self):
        self.update_data_service_instance.session.execute.side_effect = Exception(
            "error"
        )
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                self.update_data_service_instance.update_data([], [])
            )

            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.update_data_service_instance.session.execute.assert_called_once()
