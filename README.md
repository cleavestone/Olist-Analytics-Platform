# Olist ELT Platform

A modern ELT (Extract, Load, Transform) platform built around the [Olist Brazilian E-commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce). It simulates a production source system with realistic data arrival patterns and processes it through a complete analytics pipeline.

## Architecture

```
┌──────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│  Olist CSVs  │───▶│  FastAPI Source   │───▶│  dlt Ingestion      │
│  (seed data) │    │  (drip-feed API)  │    │  (incremental load) │
└──────────────┘    └──────────────────┘    └─────────────────────┘
                                                   │
                                                   ▼
                                           ┌─────────────────────┐
                                           │  dbt Transformations │
                                           │  Bronze → Silver →   │
                                           │  Gold (medallion)    │
                                           └─────────────────────┘
```

## Project Structure

```
olist-elt-platform/
├── api/                  # FastAPI source service
├── dlt_pipeline/         # dlt ingestion pipeline
├── dbt_project/          # dbt transformations
└── docker-compose.yml    # Infrastructure orchestration
```

## Tech Stack

| Component       | Technology                    |
|-----------------|-------------------------------|
| Source API      | FastAPI, SQLAlchemy, Postgres |
| Ingestion       | dlt (data load tool)          |
| Transformations | dbt (data build tool)         |
| Orchestration   | Docker Compose                |
| Package Manager | uv                            |

## Quick Start

1. **Place Olist CSV files** in `api/data/raw/`
2. **Start infrastructure:**

```bash
docker compose up -d api_db warehouse_db
```

3. **Seed the API database:**

```bash
docker compose run --rm api uv run python -m scripts.load_csv_to_db
```

4. **Start the API:**

```bash
docker compose up -d api
```

5. **Run the ingestion pipeline:**

```bash
docker compose --profile manual run --rm dlt_pipeline
```

6. **Run dbt transformations:**

```bash
cd dbt_project/olist_analytics
dbt run
```

## Packages

| Package           | Description                                      | Ports |
|-------------------|--------------------------------------------------|-------|
| `api`             | FastAPI service exposing Olist data with drip-feed | 8000  |
| `dlt_pipeline`    | Incremental data ingestion from API to warehouse  | —     |
| `dbt_project`     | SQL transformations following medallion architecture | —  |
| `api_db`          | Postgres database for source API                  | 5433  |
| `warehouse_db`    | Postgres database for analytics warehouse          | 5434  |

## Design Highlights

- **Drip-feed mechanism**: Rows are progressively released over time so incremental pipelines always have new data to process
- **Cursor-based pagination**: Opaque, base64-encoded cursors for reliable incremental extraction
- **Medallion architecture**: Bronze (raw) → Silver (cleaned) → Gold (analytics-ready) data organization
- **Merge write disposition**: Idempotent re-runs for production reliability
