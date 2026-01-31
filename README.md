# realtime-lakehouse-aws-databricks

## Data Contract

This project uses a versioned clickstream event contract to ensure consistent ingestion and transformation across the Bronze/Silver/Gold lakehouse layers.

### Schema files
- JSON Schema: [`schemas/clickstream.schema.json`](schemas/clickstream.schema.json)
- Example events: [`schemas/examples/`](schemas/examples/)
- (Optional) Avro schema: [`schemas/clickstream.avsc`](schemas/clickstream.avsc)

## Architecture
Local Python producer → S3 landing (micro-batches) → Databricks Structured Streaming → Delta Lake (Bronze/Silver/Gold) → Gold metrics tables.

## Setup
1) Install AWS CLI, Python 3.11+
2) `pip install boto3`
3) Configure AWS: `aws configure`
4) (Windows) allow scripts: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

## Run Producer (near real-time)
`.\scripts\02_run_producer.ps1`

## Verify S3 Ingestion
`.\scripts\aws_verify.ps1`

## Run Medallion Pipeline in Databricks
Run notebooks in order:
1. `databricks/notebooks/01_bronze_autoloader.py`
2. `databricks/notebooks/02_silver_stream.py`
3. `databricks/notebooks/03_gold_metrics.py`

## Verify Results
Query Bronze/Silver/Gold Delta outputs in Databricks.

## Stop & Cleanup
Stop producer: Ctrl+C  
Cleanup demo data: `.\scripts\cleanup_s3.ps1`

### Required fields (must exist for the event to be processed)
- `event_id` (UUID): globally unique event identifier (used for deduplication/idempotency)
- `schema_version` (int): schema version for contract evolution
- `event_time` (UTC timestamp): time when the event occurred (used for watermarking & late event handling)
- `ingest_time` (UTC timestamp): time when the event was produced/ingested
- `user_id` (string)
- `session_id` (string)
- `action` (enum): `view | click | add_to_cart | purchase`
- `page` (string)

### Optional fields
- `referrer` (string / null)
- `device_type` (enum): `mobile | desktop | tablet | other`
- `country` (ISO-3166-1 alpha-2)
- `ip_hash` (string): privacy-preserving identifier (no raw IP stored)
- `user_agent` (string / null)
- `source` (string / null)

### Field semantics
- `event_time` represents when the user action happened (business time).
- `ingest_time` represents when the event entered the pipeline (processing time).
- Late events are expected and handled using `event_time` watermarking in the streaming pipeline.

### Schema evolution rules
- `schema_version` increments on **non-backward-compatible** changes.
- Backward-compatible changes include adding **new optional fields** with defaults/nullability.
- Enum expansions should be done with care (downstream consumers may not handle unknown values).
- Breaking changes (renaming/removing required fields) require a version bump and a migration plan.

### Privacy & compliance notes
- This demo does not store raw personal identifiers such as full IP addresses.
- Any user/network identifiers are hashed (`ip_hash`) for privacy and safe public sharing.
