# Serverless Customer Data Pipeline on AWS

An event-driven data engineering pipeline that automatically ingests, cleans, catalogs, and makes queryable a customer dataset, built entirely on serverless AWS services.

## Architecture

```
[upload.py] ──> (S3 Landing Bucket) ──> [AWS Lambda]
                                              │ triggers
                                              ▼
                                    [AWS Glue ETL Job]
                                    (PySpark: dedupe, clean phone numbers)
                                              │
                                              ▼
                                  (S3 Cleaned Bucket — Parquet)
                                              │ triggers
                                              ▼
                                    [AWS Glue Crawler]
                                              │
                                              ▼
                                  (AWS Glue Data Catalog)
                                              │
                                              ▼
                                    [Amazon Athena — SQL]
```

**Flow:**
1. `upload.py` uploads `customers.csv` to an S3 landing bucket using `boto3`.
2. The S3 `ObjectCreated` event (filtered to `.csv` files) triggers an AWS Lambda function.
3. Lambda parses the S3 event payload, validates the file name, and starts an AWS Glue ETL job, passing the bucket and key as job arguments.
4. The Glue ETL job (PySpark) reads the raw CSV, removes duplicate records, normalizes phone numbers to a clean 10-digit string format, and writes the result to a separate S3 bucket in Apache Parquet format.
5. On completion, the ETL job triggers an AWS Glue Crawler, which scans the cleaned Parquet data and updates the schema in the AWS Glue Data Catalog.
6. The cataloged data is queried directly with standard SQL in Amazon Athena, no database server required.

## AWS Services Used

| Service | Role |
|---|---|
| **Amazon S3** | Landing bucket for raw uploads; separate bucket/prefix for cleaned Parquet output |
| **AWS Lambda** | Event-driven orchestrator; triggers the ETL job on file arrival |
| **AWS Glue (ETL Job)** | PySpark job for deduplication and data cleaning |
| **AWS Glue (Crawler)** | Automatic schema discovery and Data Catalog updates |
| **AWS Glue Data Catalog** | Central metadata store, table definitions |
| **Amazon Athena** | Serverless SQL querying over the Parquet data |
| **IAM** | Scoped execution roles for Lambda, Glue Job, and Crawler |

## Repository Contents

```
.
├── upload.py                  # Local client: uploads CSV to S3 landing bucket
├── lambda_function.py         # Lambda: parses S3 event, triggers Glue ETL job
├── etl_job.py                 # Glue PySpark script: dedupe, clean, write Parquet, trigger crawler
└── README.md
```

## Setup

### 1. S3 Buckets
- Create a landing bucket (e.g. `customer-trigger`) for raw CSV uploads.
- Within it (or in a separate bucket), create a `cleaned/` prefix for ETL output.

### 2. IAM Roles
- **Lambda execution role:** `s3:GetObject` on the landing bucket, `glue:StartJobRun` on the Glue job.
- **Glue job role:** read access to the landing bucket, write access to the cleaned prefix, `glue:StartCrawler`.
- **Glue crawler role:** read access to the cleaned prefix, permissions to create/update tables in the Data Catalog.

### 3. AWS Glue ETL Job
- Create a job named to match `GLUE_JOB_NAME` in `lambda_function.py`.
- Paste in `etl_job.py`.
- Add job parameters (used as defaults for manual runs; overridden by Lambda on real triggers):
  - `--s3_input_bucket` → your landing bucket name
  - `--s3_input_key` → `customers.csv`
- Set `output_path` inside the script to your cleaned S3 location.

### 4. AWS Glue Crawler
- Create a crawler pointed at the **cleaned** S3 prefix (not the raw CSV).
- Target database: e.g. `customer_analytics_db`.
- Trigger type: on demand (started programmatically by the ETL job).

### 5. AWS Lambda
- Deploy `lambda_function.py`.
- Add an S3 trigger on the landing bucket, event type `All object create events`, **suffix filter `.csv`** (this prevents the Parquet output from re-triggering the pipeline).
- Attach the IAM role described above.

### 6. Amazon Athena
- Set a query result location (a dedicated S3 bucket).
- Query the cataloged table, e.g.:
  ```sql
  SELECT * FROM "customer_analytics_db"."<table_name>" LIMIT 10;
  ```

## Data Transformations

The ETL job applies two transformations to the raw customer data:

- **Deduplication** — drops duplicate records based on `Customer Id`.
- **Phone number normalization** — strips extensions, punctuation, and non-digit characters from `Phone 1` and `Phone 2`, keeping the last 10 digits as a clean string (preserving leading zeros, which raw CSV parsing would otherwise drop).

Output is written as Parquet with Snappy compression, which is significantly faster and cheaper to query in Athena than scanning raw CSV.

## Design Notes / Lessons Learned

- **S3 event payloads are lists.** `event['Records']` is always an array, even for a single file upload — accessing it as `event['Records']['s3']...` throws a `TypeError`. The Lambda loops over `event.get('Records', [])` to handle single or batched events safely.
- **Glue Studio's visual editor does not support parameterized S3 paths** (`${...}` placeholders fail validation). The final version uses the Script editor, building the input path directly from `getResolvedOptions()` in PySpark instead.
- **Crawler source must point at the cleaned data, not the raw CSV**, or Athena tables reflect unprocessed data. Pointing a crawler at a bucket *root* instead of a specific object/prefix can also merge unrelated files into one malformed table — the crawler's data source should always be scoped as tightly as possible.
- **Avoiding trigger loops:** since the cleaned Parquet output could theoretically re-trigger the same S3 event pattern, the Lambda's trigger is filtered by `.csv` suffix so only genuine new uploads start the pipeline.

## Possible Next Steps

- Add an SQS Dead Letter Queue to the Lambda function to catch and preserve malformed files instead of failing silently.
- Move bucket/table names out of hardcoded strings into Lambda environment variables.
- Deploy the entire stack with Infrastructure as Code (AWS SAM or CDK) instead of manual console configuration.
- Scope IAM policies down from broad managed policies (e.g. `AmazonS3FullAccess`) to least-privilege, resource-specific permissions.
