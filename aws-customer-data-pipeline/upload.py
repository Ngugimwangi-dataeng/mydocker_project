import boto3
import os
from botocore.exceptions import ClientError

# --- Configuration ---
BUCKET_NAME = "cstomer-trigger"       # your S3 landing bucket
LOCAL_FILE_PATH = "customers.csv"     # path to the file on your machine
S3_KEY = "customers.csv"              # destination key in the bucket

print("Loading Data Upload Client...")


def upload_file(local_path, bucket, s3_key):
    """
    Uploads a local file to the S3 landing bucket using boto3.
    This triggers the downstream Lambda -> Glue ETL -> Crawler pipeline.
    """
    if not os.path.isfile(local_path):
        print(f"File not found: {local_path}")
        return False

    s3_client = boto3.client("s3")

    try:
        print(f"Uploading '{local_path}' to 's3://{bucket}/{s3_key}'...")
        s3_client.upload_file(local_path, bucket, s3_key)
        print("Upload successful. Pipeline should trigger automatically.")
        return True

    except ClientError as e:
        print(f"Upload failed: {e}")
        return False


if __name__ == "__main__":
    upload_file(LOCAL_FILE_PATH, BUCKET_NAME, S3_KEY)
