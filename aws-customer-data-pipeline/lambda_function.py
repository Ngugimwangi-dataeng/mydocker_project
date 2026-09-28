import json
import urllib.parse
import boto3

# Initialize the AWS Glue client outside the handler for better performance
glue_client = boto3.client('glue')

# Name of the Glue ETL job this function triggers
GLUE_JOB_NAME = 'ETLJOB'

print('Loading Data Engineering Trigger Function with Glue ETL Integration...')


def lambda_handler(event, context):
    """
    Triggers automatically when a file lands in the S3 bucket.
    If the file is 'customers.csv', it starts the AWS Glue ETL job,
    passing the bucket and key as job arguments.
    """
    print("Received event: " + json.dumps(event, indent=2))

    try:
        # S3 event payloads always contain a list of records, even for a
        # single upload, so we loop rather than indexing directly.
        for record in event.get('Records', []):
            bucket = record['s3']['bucket']['name']

            # S3 encodes file names (e.g. spaces become '+'); decode back to clean text.
            file_key = urllib.parse.unquote_plus(
                record['s3']['object']['key'],
                encoding='utf-8'
            )

            print(f"Event Detected! Bucket: '{bucket}' | File Target: '{file_key}'")

            if "customers.csv" in file_key:
                print(f"Target match: 'customers.csv' identified. Starting ETL job: {GLUE_JOB_NAME}...")

                try:
                    response = glue_client.start_job_run(
                        JobName=GLUE_JOB_NAME,
                        Arguments={
                            '--s3_input_bucket': bucket,
                            '--s3_input_key': file_key
                        }
                    )
                    print(f"Successfully started Glue ETL Job. Run ID: {response['JobRunId']}")

                except Exception as job_error:
                    print(f"Failed to start Glue ETL Job: {job_error}")
                    raise job_error

            else:
                print(f"Ignored file: '{file_key}' does not match target rules.")

        return {
            'statusCode': 200,
            'body': json.dumps("Successfully processed all event records.")
        }

    except Exception as e:
        print(f"Error parsing S3 event payload: {e}")
        raise e
