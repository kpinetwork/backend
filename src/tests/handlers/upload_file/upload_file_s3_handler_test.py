import json
from src.tests.data.data_reader import read
from unittest import TestCase, mock
from src.handlers.upload_file.upload_file_s3_handler import handler
import src.handlers.upload_file.upload_file_s3_handler as upload_data_handler


class TestUploadDataS3TriggerHandler(TestCase):
    def setUp(self):
        self.event = read("sample_event_upload_data.json")
        self.filename = "file.csv"

    @mock.patch("src.handlers.upload_file.upload_file_s3_handler.boto3")
    @mock.patch.object(upload_data_handler, "upload_file")
    def test_upload_data_success_should_return_200_response(
        self, mock_upload_file, mock_boto3
    ):
        filename = "file.csv"
        mock_upload_file.return_value = filename

        response = handler(self.event, {})

        mock_boto3.assert_not_called()
        self.assertEqual(response.get("statusCode"), 200)
        self.assertEqual(
            response.get("body"), json.dumps({"uploaded": True, "filename": filename})
        )

    @mock.patch("src.handlers.upload_file.upload_file_s3_handler.boto3")
    def test_handler_fail_no_body_400_response(self, mock_boto3):
        error_message = "No data provided"
        response = handler({}, {})

        mock_boto3.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
        self.assertEqual(response.get("body"), json.dumps({"error": error_message}))

    @mock.patch("src.handlers.upload_file.upload_file_s3_handler.boto3")
    def test_handler_without_user_id_should_return_success(self, mock_boto3):
        event = {"body": '{"file": "data", "fileName": "file.csv" }'}

        response = handler(event, {})
        body = json.loads(response.get("body"))
        file_parts = body.get("filename").split("::")

        mock_boto3.assert_not_called()
        self.assertEqual(response.get("statusCode"), 200)
        self.assertEqual(len(file_parts), 2)

    @mock.patch("src.handlers.upload_file.upload_file_s3_handler.boto3")
    def test_handler_without_valid_data_should_fail(self, mock_boto3):
        event = {"body": '{"file": null, "fileName": "file.csv" }'}

        response = handler(event, {})

        mock_boto3.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)

    @mock.patch("src.handlers.upload_file.upload_file_s3_handler.boto3")
    def test_handler_without_valid_extension_file_should_fail(self, mock_boto3):
        event = {"body": '{"file": "data", "fileName": "file.txt" }'}

        response = handler(event, {})

        mock_boto3.assert_not_called()
        self.assertEqual(response.get("statusCode"), 400)
