import os
import urllib.parse


class GlueService:
    def __init__(self):
        pass

    def trigger(self, glue_client, event, logger) -> dict:
        filename = urllib.parse.unquote_plus(
            event["Records"][0]["s3"]["object"]["key"], encoding="utf-8"
        )
        env = os.environ.get("ENV")
        bucket_files = os.environ.get("BUCKET_FILES")
        job_name = "kpinetwork_job"
        try:
            logger.info("BUCKET: " + bucket_files)
            logger.info("FILENAME: " + filename)
            response = glue_client.start_job_run(
                JobName=job_name,
                Arguments={
                    "--ENV": env,
                    "--FILENAME": filename,
                    "--BUCKET": bucket_files,
                },
            )
            job_id = response["JobRunId"]
            logger.info("STARTED GLUE JOB: " + job_name)
            logger.info("GLUE JOB RUN ID: " + job_id)
            return {"job": job_name, "id": job_id}
        except Exception as e:
            print("Error processing file {}/{}".format(bucket_files, filename))
            print(e)
            raise e
