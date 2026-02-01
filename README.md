# Streaming Lakehouse (AWS S3 + Databricks)

Near real-time clickstream ingestion and analytics pipeline using
**micro-batch streaming**, **Databricks Structured Streaming**, and
a **Bronze / Silver / Gold lakehouse architecture**.

---

## Architecture

Local Python event producer  
→ S3 landing zone (partitioned micro-batches)  
→ Databricks Structured Streaming  
→ Delta Lake (Bronze / Silver / Gold)  
→ Streaming-ready analytics tables

**Key characteristics**
- Near real-time ingestion via micro-batches
- Exactly-once processing using Delta Lake + checkpoints
- Late-event handling with event-time watermarking
- Fault-tolerant restarts (idempotent + replay-safe)

---

## Streaming Guarantees

This pipeline provides the following guarantees:

- **Micro-batch streaming ingestion** from S3 landing zone
- **Exactly-once semantics** via Structured Streaming checkpoints
- **Late-event tolerance** using event-time watermarking
- **Stateful deduplication** on `event_id`
- **Replay-safe restarts** (no double processing after failure)
- **Quarantine path** for invalid or schema-violating events

---

## Data Contract

This project uses a **versioned clickstream data contract** to ensure
consistent ingestion and transformation across Bronze / Silver / Gold layers.

### Schema files
- JSON Schema: [`schemas/clickstream.schema.json`](schemas/clickstream.schema.json)
- Example events: [`schemas/examples/`](schemas/examples/)
- Optional Avro schema: [`schemas/clickstream.avsc`](schemas/clickstream.avsc)

### Required fields
- `event_id` (UUID): globally unique identifier (deduplication / idempotency)
- `schema_version` (int): schema evolution control
- `event_time` (UTC): business time (used for watermarking)
- `user_id` (string)
- `action` (enum): `view | click | add_to_cart | purchase`
- `page` (string)

### Optional fields
- `referrer`
- `device_type`: `mobile | desktop | tablet | other`
- `country` (ISO-3166-1 alpha-2)
- `ip_hash` (privacy-preserving identifier)
- `user_agent`
- `source`

### Schema enforcement
- Bronze ingestion uses an **explicit schema** (no inference)
- Unexpected fields are captured in `_rescued_data`
- Invalid records are routed to a **quarantine Delta table**
- Schema drift is detected early and never silently ignored

---

## Medallion Layers

### Bronze
- Raw event ingestion from S3
- Schema enforced at read time
- Ingest timestamp added
- All records preserved (including malformed)

### Silver
- Streaming data quality checks
- Event-time watermarking
- Stateful deduplication on `event_id`
- Invalid records routed to quarantine

### Gold
- Windowed streaming aggregations
- Events per minute
- Active users (approximate distinct)
- Analytics-ready Delta tables

---

## Setup

1. Install AWS CLI and Python 3.11+
2. Install dependencies:
   ```bash
   pip install boto3
