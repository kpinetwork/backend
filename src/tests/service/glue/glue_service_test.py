import os

from unittest import TestCase, mock
import pydash
import logging
from unittest.mock import Mock
from src.service.glue.glue_service import GlueService

logger = logging.getLogger()
logger.setLevel(logging.INFO)
test_file_name = "test.csv"
bucket_files = "kpinetwork_test_files"
env = "demo"


class TestGlueService(TestCase):
    def setUp(self):
        self.glue_service_instance = GlueService(logger)
        self.mock_event = {"Records": [{"s3": {"object": {"key": test_file_name}}}]}
        self.mock_boto_client = Mock()
        return

    @mock.patch.dict(os.environ, {"ENV": env, "BUCKET_FILES": bucket_files})
    def test_success_call_to_glue_job(self):
        self.mock_boto_client.start_job_run.return_value = {"JobRunId": "1234"}
        response = self.glue_service_instance.trigger(
            self.mock_boto_client, self.mock_event, logger
        )
        self.assertEqual(pydash.get(response, "id"), "1234")
        self.assertEqual(self.mock_boto_client.start_job_run.call_count, 1)
        self.mock_boto_client.start_job_run.assert_called_once_with(
            JobName="kpinetwork_job",
            Arguments={
                "--ENV": env,
                "--FILENAME": test_file_name,
                "--BUCKET": bucket_files,
            },
        )

    @mock.patch.dict(os.environ, {"ENV": env, "BUCKET_FILES": bucket_files})
    def test_failed_call_to_glue_job(self):
        self.mock_boto_client.start_job_run.side_effect = Exception("error")
        with self.assertRaises(Exception):
            self.assertRaises(
                self.glue_service_instance.trigger(
                    self.mock_boto_client, self.mock_event, logger
                )
            )
            self.assertEqual(self.mock_boto_client.start_job_run.call_count, 1)
