# Olist ELT Platform

A modern ELT platform built around the [Olist Brazilian E-commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce). Simulates a production source system with realistic data arrival patterns and processes it through a complete analytics pipeline.

## Architecture

```text
                    Olist Dataset (Kaggle)
                             |
                             ▼
                FastAPI Source API (api/)
                • PostgreSQL (api_db)
                • Cursor-based pagination
                • Incremental filtering
                • Background drip-feed releases
                             |
                             ▼
                   dlt Incremental Pipeline
                   • Cursor-based extraction
                   • Incremental loading
                   • Merge write disposition
                             |
                             ▼
            PostgreSQL Warehouse (bronze schema)
            Raw source tables (1:1 with API)
                             |
                             ▼
                   dbt-core Transformations
                   Bronze → Silver → Gold
                             |
                             ▼
                  Kestra Orchestration
            dlt → dbt snapshot → dbt run → dbt test
                  (every 30 minutes)
                             |
                             ▼
                  Apache Superset (planned)
```

## Project Structure

```
olist-elt-platform/
├── api/              # FastAPI source service
├── dlt_pipeline/     # dlt ingestion pipeline
├── dbt_project/      # dbt transformations
├── docker-compose.yml
└── README.md
```

## Tech Stack

| Component       | Technology                    |
|-----------------|-------------------------------|
| Source API      | FastAPI, SQLAlchemy, Postgres |
| Ingestion       | dlt (data load tool)          |
| Transformations | dbt (data build tool)         |
| Orchestration   | Kestra                        |
| Visualization   | Apache Superset (planned)     |
| Package Manager | uv                            |
| Container       | Docker Compose                |

## Quick Start

### Prerequisites

- Docker & Docker Compose (v2)
- [Olist CSV files](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) in `api/data/raw/`

### Setup

```bash
# 1. Start infrastructure (API + warehouse + Kestra)
docker compose up -d

# 2. Seed the API database
docker compose exec api uv run python -m scripts.load_csv_to_db

# 3. Run ingestion
docker compose run --rm dlt_pipeline

# 4. Run dbt transformations
docker compose run --rm dbt build
```

### Access Points

| Service          | URL                              |
|------------------|----------------------------------|
| API docs         | http://localhost:8000/docs       |
| pgAdmin          | http://localhost:5050            |
| Kestra UI        | http://localhost:8081            |

## Services

| Service          | Description                            | Port  |
|------------------|----------------------------------------|-------|
| `api`            | FastAPI source with drip-feed          | 8000  |
| `api_db`         | Postgres — API database                | 5433  |
| `warehouse_db`   | Postgres — analytics warehouse         | 5434  |
| `dlt_pipeline`   | dlt ingestion (manual profile)         | —     |
| `dbt`            | dbt transformations (manual profile)   | —     |
| `kestra`         | Workflow orchestration                 | 8081  |
| `kestra_db`      | Postgres — Kestra backend              | —     |
| `pgadmin`        | Database admin UI                      | 5050  |

## Orchestration (Kestra)

The complete ELT pipeline runs every **30 minutes**:

1. **dlt ingest** — pull new data from the API into bronze schema
2. **dbt snapshot** — capture SCD Type 2 changes on products
3. **dbt run** — build silver → gold models incrementally
4. **dbt test** — validate data quality

Each step runs inside an isolated Docker container using Kestra's `docker.Run` task type.

## dbt Models

**Staging** (silver schema, views):
`stg_orders`, `stg_customers`, `stg_sellers`, `stg_products`, `stg_order_items`, `stg_order_payments`, `stg_order_reviews`

**Intermediate** (silver schema, view):
`int_order_details` — denormalized order × items × products × sellers

**Marts** (gold schema, tables):

| Model              | Type         | Description                          |
|--------------------|--------------|--------------------------------------|
| `dim_customers`    | Dimension    | Customer geography                   |
| `dim_sellers`      | Dimension    | Seller geography                     |
| `dim_products`     | SCD Type 2   | Product attributes with full history |
| `dim_date`         | Dimension    | Calendar (2015–2028)                 |
| `fct_orders`       | Fact (incr)  | Order-level aggregated metrics       |
| `fct_order_items`  | Fact (incr)  | Line-item-level facts                |
| `fct_payments`     | Fact (incr)  | Payment-level facts                  |

## Design Highlights

- **Drip-feed mechanism**: Rows progressively released so incremental pipelines always find new data
- **Cursor-based pagination**: Opaque, base64-encoded cursors for reliable incremental extraction
- **Unique timestamps**: Every row has a unique `updated_at` (offset by microseconds) to avoid dlt dedup blowup
- **Medallion architecture**: Bronze (raw) → Silver (cleaned) → Gold (analytics-ready)
- **SCD Type 2**: Product dimension tracks full attribute history via dbt snapshots
- **Incremental facts**: Fact tables use `is_incremental()` for efficient re-runs
- **Merge write disposition**: Idempotent dlt ingestion with natural primary keys

## Roadmap

- [x] Phase 1 — Source API (cursor pagination, incremental filtering, drip-feed)
- [x] Phase 2 — dlt ingestion (incremental, merge, bronze schema)
- [x] Phase 3 — dbt transformations (medallion, SCD2, star schema, incremental facts, tests)
- [x] Phase 4 — Kestra orchestration (scheduled pipeline every 30 min)
- [ ] Phase 5 — Apache Superset dashboards
- [ ] Phase 6 — CI/CD and polish
