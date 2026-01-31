from pyspark.sql.functions import *

S3_BUCKET = "lej7-s3-databricks-realtime-04140428"

BRONZE_PATH = f"s3://{S3_BUCKET}/delta/bronze_clickstream/"
SILVER_PATH = f"s3://{S3_BUCKET}/delta/silver_clickstream/"
CHECKPOINT_PATH = f"s3://{S3_BUCKET}/checkpoints/silver_clickstream/"
QUARANTINE_PATH = f"s3://{S3_BUCKET}/delta/quarantine_clickstream/"

bronze_stream = spark.readStream.format("delta").load(BRONZE_PATH)

# ----- streaming-safe DQ split -----
dq = bronze_stream.withColumn(
    "_is_valid",
    col("user_id").isNotNull()
    & col("event_id").isNotNull()
    & col("event_time").isNotNull()
)

valid = dq.filter(col("_is_valid")).drop("_is_valid")
invalid = dq.filter(~col("_is_valid")).drop("_is_valid")

# ----- watermark + dedupe (stateful) -----
silver = (
    valid
    .withWatermark("event_time", "10 minutes")
    .dropDuplicates(["event_id"])
)

silver_query = (
    silver.writeStream
        .format("delta")
        .option("checkpointLocation", CHECKPOINT_PATH)
        .trigger(availableNow=True)
        .outputMode("append")
        .start(SILVER_PATH)
)

quarantine_query = (
    invalid.writeStream
        .format("delta")
        .option("checkpointLocation", CHECKPOINT_PATH + "_bad/")
        .trigger(availableNow=True)
        .outputMode("append")
        .start(QUARANTINE_PATH)
)

silver_query.awaitTermination()
quarantine_query.awaitTermination()