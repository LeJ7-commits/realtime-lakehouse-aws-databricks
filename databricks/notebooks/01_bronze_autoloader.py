# Databricks Bronze Streaming Ingestion
# Reads micro-batch JSON files from S3 and writes Delta Bronze table

from pyspark.sql.functions import *
from pyspark.sql.types import *

# ---------- CONFIG ----------
S3_BUCKET = "lej7-s3-databricks-realtime-04140428"
LANDING_PATH = f"s3://{S3_BUCKET}/landing/clickstream/"
BRONZE_PATH = f"s3://{S3_BUCKET}/delta/bronze_clickstream/"
CHECKPOINT_PATH = f"s3://{S3_BUCKET}/checkpoints/bronze_clickstream/"

# ---------- SCHEMA (contract-first ingestion) ----------
schema = StructType([
    StructField("event_id", StringType()),
    StructField("user_id", StringType()),
    StructField("event_type", StringType()),
    StructField("country", StringType()),
    StructField("event_time", StringType()),
    StructField("page", StringType()),
])

# ---------- STREAM READ ----------
bronze_stream = (
    spark.readStream
        .format("cloudFiles")                      # Auto Loader
        .option("cloudFiles.format", "json")
        .option("cloudFiles.schemaLocation", CHECKPOINT_PATH + "_schema/")
        .option("maxFilesPerTrigger", 10)          # throttle micro-batches
        .schema(schema)
        .load(LANDING_PATH)
)

# ---------- TRANSFORM ----------
bronze_clean = (
    bronze_stream
        .withColumn("event_time", to_timestamp("event_time"))
        .withColumn("ingest_time", current_timestamp())
)

# ---------- WRITE STREAM ----------
query = (
    bronze_clean.writeStream
        .format("delta")
        .option("checkpointLocation", CHECKPOINT_PATH)
        .trigger(availableNow=True)
        .outputMode("append")
        .start(BRONZE_PATH)
)

query.awaitTermination()
