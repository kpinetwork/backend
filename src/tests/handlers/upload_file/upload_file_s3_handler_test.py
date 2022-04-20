import json
from src.tests.data.data_reader import read
from unittest import TestCase, mock
from src.handlers.upload_file.upload_file_s3_handler import handler, upload_file
import src.handlers.upload_file.upload_file_s3_handler as upload_data_handler


class TestUploadDataS3TriggerHandler(TestCase):
    def setUp(self):
        self.event = read("sample_event_upload_data.json")

    @mock.patch("src.handlers.upload_file.upload_file_s3_handler.boto3")
    @mock.patch.object(upload_data_handler, "upload_file")
    def test_upload_data_success_should_return_200_response(
        self, mock_upload_file, mock_boto3
    ):
        response = handler(self.event, {})

        mock_upload_file.return_value = None
        mock_boto3.assert_not_called()
        self.assertEqual(response.get("statusCode"), 200)
        self.assertEqual(response.get("body"), json.dumps({"uploaded": True}))

    @mock.patch("src.handlers.upload_file.upload_file_s3_handler.boto3")
    @mock.patch.object(upload_data_handler, "upload_file")
    def test_handler_fail_no_body_400_response(self, mock_upload_file, mock_boto3):
        error_message = "No data provided"
        response = handler({}, {})

        mock_upload_file.assert_not_called()
        mock_boto3.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))

    @mock.patch("src.handlers.upload_file.upload_file_s3_handler.boto3")
    def test_upload_data_sucess(self, mock_boto3):
        response = upload_file("Bucket_name", {"file": "test", "fileName": "test.csv"})

        mock_boto3.assert_not_called()
        self.assertEqual(response, None)

    @mock.patch("src.handlers.upload_file.upload_file_s3_handler.boto3")
    def test_upload_data_fail_no_file_400_response(self, mock_boto3):
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                upload_file("Bucket_name", {"body": '{"notFile": "file.txt"}'})
            )
            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.company_service_instance.session.execute.assert_called_once()
            mock_boto3.assert_not_called()

    @mock.patch("src.handlers.upload_file.upload_file_s3_handler.boto3")
    def test_upload_data_fail_with_wrong_extension_400_response(self, mock_boto3):
        with self.assertRaises(Exception) as context:
            exception = self.assertRaises(
                upload_file("Bucket_name", {"file": "file", "fileName": "test.txt"})
            )
            self.assertTrue("error" in context.exception)
            self.assertEqual(exception, Exception)
            self.company_service_instance.session.execute.assert_called_once()
            mock_boto3.assert_not_called()
