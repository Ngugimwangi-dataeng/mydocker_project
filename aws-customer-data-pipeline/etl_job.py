import sys
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, regexp_replace, length, when, substring
import boto3

# 1. Capture dynamic arguments passed by the Lambda trigger (or job defaults on manual runs)
args = getResolvedOptions(sys.argv, ['JOB_NAME', 's3_input_bucket', 's3_input_key'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

glue_client = boto3.client('glue')

# Name of the crawler that catalogs the cleaned output
CRAWLER_NAME = 'customer-data-crawler'

input_path = f"s3://{args['s3_input_bucket']}/{args['s3_input_key']}"
output_path = "s3://cstomer-trigger/cleaned/"  # <-- update if your cleaned location changes

print(f"Reading raw file: {input_path}")

# 2. Extract: read as strings so phone numbers keep leading zeros
df = spark.read.format("csv") \
    .option("header", "true") \
    .option("inferSchema", "false") \
    .load(input_path)

# 3. Transform: remove duplicate customer records
print("Step 1: Dropping duplicate records based on 'Customer Id'...")
df_deduped = df.dropDuplicates(["Customer Id"])


def format_phone_column(df_target, target_column):
    """Strip extensions and non-digit characters, keep the last 10 digits."""
    raw = col(target_column).cast("string")
    no_ext = regexp_replace(raw, r"(?i)\s*(x|ext\.?)\s*\d+$", "")
    digits = regexp_replace(no_ext, r"[^0-9]", "")
    formatted = when(length(digits) >= 10, substring(digits, -10, 10)).otherwise(digits)
    return df_target.withColumn(target_column, formatted)


print("Step 2: Normalizing 'Phone 1' and 'Phone 2' to 10-digit strings...")
df_transformed = format_phone_column(df_deduped, "Phone 1")
df_transformed = format_phone_column(df_transformed, "Phone 2")

# 4. Load: write cleaned data to S3 in Parquet format
print(f"Step 3: Writing cleaned data in Parquet format to: {output_path}")
df_transformed.write.format("parquet") \
    .mode("overwrite") \
    .save(output_path)

# 5. Orchestrate: trigger the crawler to refresh the Data Catalog
print(f"Step 4: Starting crawler '{CRAWLER_NAME}'...")
try:
    glue_client.start_crawler(Name=CRAWLER_NAME)
    print(f"Successfully started crawler '{CRAWLER_NAME}'.")
except glue_client.exceptions.CrawlerRunningException:
    print(f"Crawler '{CRAWLER_NAME}' is already running. Skipping trigger.")
except Exception as crawler_error:
    print(f"Failed to start crawler: {crawler_error}")

print("ETL job completed successfully.")
job.commit()
