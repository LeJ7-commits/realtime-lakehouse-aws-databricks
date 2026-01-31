from pyspark.sql.functions import *

S3_BUCKET = "lej7-s3-databricks-realtime-04140428"

SILVER_PATH = f"s3://{S3_BUCKET}/delta/silver_clickstream/"

GOLD_EVENTS_PATH = f"s3://{S3_BUCKET}/delta/gold_events_per_minute/"
GOLD_PAGES_PATH  = f"s3://{S3_BUCKET}/delta/gold_top_pages_by_country/"
GOLD_USERS_PATH  = f"s3://{S3_BUCKET}/delta/gold_active_users_5min/"

CHECKPOINT_BASE = f"s3://{S3_BUCKET}/checkpoints/gold/"

# --- one-time cleanup if you previously ran Gold with different logic ---
# dbutils.fs.rm(CHECKPOINT_BASE + "events/", True)
# dbutils.fs.rm(CHECKPOINT_BASE + "pages/", True)
# dbutils.fs.rm(CHECKPOINT_BASE + "users/", True)
# dbutils.fs.rm(GOLD_EVENTS_PATH, True)
# dbutils.fs.rm(GOLD_PAGES_PATH, True)
# dbutils.fs.rm(GOLD_USERS_PATH, True)

# ---------- STREAM READ ----------
silver_stream = spark.readStream.format("delta").load(SILVER_PATH)

# ---------- EVENTS PER MINUTE ----------
events_per_minute = (
    silver_stream
    .withWatermark("event_time", "10 minutes")
    .groupBy(window("event_time", "1 minute"))
    .count()
)

events_query = (
    events_per_minute.writeStream
        .format("delta")
        .option("checkpointLocation", CHECKPOINT_BASE + "events/")
        .trigger(availableNow=True)
        .outputMode("complete")
        .start(GOLD_EVENTS_PATH)
)

# ---------- TOP PAGES BY COUNTRY ----------
pages_by_country = (
    silver_stream
    .withWatermark("event_time", "10 minutes")
    .groupBy(
        window("event_time", "5 minutes"),
        col("country"),
        col("page")
    )
    .count()
)

pages_query = (
    pages_by_country.writeStream
        .format("delta")
        .option("checkpointLocation", CHECKPOINT_BASE + "pages/")
        .trigger(availableNow=True)
        .outputMode("complete")
        .start(GOLD_PAGES_PATH)
)

# ---------- ACTIVE USERS (5 MIN WINDOW) ----------
active_users = (
    silver_stream
    .withWatermark("event_time", "10 minutes")
    .groupBy(window("event_time", "5 minutes"))
    .agg(approx_count_distinct("user_id").alias("active_users_approx"))
)

users_query = (
    active_users.writeStream
        .format("delta")
        .option("checkpointLocation", CHECKPOINT_BASE + "users/")
        .trigger(availableNow=True)
        .outputMode("complete")
        .start(GOLD_USERS_PATH)
)

events_query.awaitTermination()
pages_query.awaitTermination()
users_query.awaitTermination()