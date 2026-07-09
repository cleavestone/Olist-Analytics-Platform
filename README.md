
# Olist ELT Analytics Platform

An end-to-end analytics engineering portfolio project that simulates a real-world ELT pipeline from source system to analytics-ready warehouse.

The project features a **self-built FastAPI source API**, incremental ingestion with **dlt**, transformations with **dbt-core** using a **Medallion Architecture (Bronze → Silver → Gold)**, a proper **star schema**, **Slowly Changing Dimensions (SCD Type 2)**, and **incremental fact tables**. The remaining phases include orchestration with **Kestra** and business intelligence with **Apache Superset**.

Built entirely with **open-source technologies**—no cloud infrastructure or billing required.

---

# Why This Project Exists

Most portfolio ELT projects simply load static CSV files into a warehouse and perform transformations.

This project simulates a **real production source system**, requiring the ingestion layer to solve realistic engineering challenges instead of performing a one-time data load.

The source system provides:

- Cursor-based pagination
- Incremental extraction using `updated_at`
- Background data releases (drip-feed)
- Late-arriving records

This means the ingestion pipeline must correctly handle:

- Incremental loading
- Pagination
- Merge-based upserts
- Late-arriving data
- Idempotent pipeline execution

---

# Architecture

```text
                   Olist Dataset (Kaggle)
                            │
                            ▼
               FastAPI Source API (api/)
               ─────────────────────────
               • PostgreSQL (api_db)
               • Cursor pagination
               • updated_at filtering
               • Background drip-feed
                            │
                            ▼
              dlt Incremental Pipeline
              ─────────────────────────
              • Incremental extraction
              • Merge write disposition
              • Primary key upserts
                            │
                            ▼
          PostgreSQL Warehouse (Bronze)
          ─────────────────────────────
          Raw source tables (1:1)
                            │
                            ▼
                 dbt-core Transformations
                 ────────────────────────

                Bronze
                   │
                   ▼
                Silver
        • Staging models
        • Data cleaning
        • Type casting
        • Tests
        • SCD Type 2 snapshots
                   │
                   ▼
                 Gold
        • Star schema
        • Dimension tables
        • Incremental fact tables
                   │
                   ▼
          Kestra (Planned)
        Pipeline orchestration
                   │
                   ▼
      Apache Superset (Planned)
       Analytics & Dashboards
```

---

# Tech Stack

| Layer                      | Technology                   |
| -------------------------- | ---------------------------- |
| Source System              | FastAPI + PostgreSQL         |
| Data Ingestion             | dlt                          |
| Data Warehouse             | PostgreSQL                   |
| Data Transformation        | dbt-core                     |
| Data Modeling              | Star Schema                  |
| Slowly Changing Dimensions | dbt Snapshots (SCD Type 2)   |
| Fact Loading               | Incremental Merge Models     |
| Orchestration              | Kestra*(Planned)*          |
| Business Intelligence      | Apache Superset*(Planned)* |
| Containerization           | Docker & Docker Compose      |

---

# Medallion Architecture

```
          Bronze
     Raw Source Tables
             │
             ▼
          Silver
 Cleaned & Standardized
             │
             ▼
            Gold
 Analytics-Ready Models
```

### Bronze

- Raw source data
- 1:1 copy of the API
- Incrementally loaded with dlt
- Merge write disposition
- Primary key upserts

---

### Silver

- Data cleaning
- Type casting
- Renaming
- Data quality tests
- Business-friendly models
- SCD Type 2 snapshots

---

### Gold

Analytics-ready star schema including:

Dimensions

- `dim_date`
- `dim_customers`
- `dim_sellers`
- `dim_products` (SCD Type 2)

Facts

- `fct_orders`
- `fct_order_items`
- `fct_payments`

All fact tables are built incrementally using merge strategies.

---

# Repository Structure

```text
olist-elt-platform/
│
├── api/
│   ├── README.md
│   └── FastAPI source system
│
├── dlt_pipeline/
│   ├── README.md
│   └── Incremental ingestion
│
├── dbt_project/
│   ├── README.md
│   └── Bronze → Silver → Gold transformations
│
└── docker-compose.yml
```

Each component is independently containerized and includes its own setup instructions.

---

# Quick Start

Start the infrastructure

```bash
docker compose up -d --build api_db api warehouse_db
```

Load the Kaggle dataset into the source API

```bash
docker compose exec api uv run python -m scripts.load_csv_to_db
```

Run the incremental dlt pipeline

```bash
docker compose run --rm dlt_pipeline
```

Run dbt

```bash
cd dbt_project/olist_analytics

uv run dbt snapshot
uv run dbt run
uv run dbt test
```

---

# Key Features

## Source API

- FastAPI
- PostgreSQL backend
- Cursor-based pagination
- Incremental filtering (`updated_at`)
- Background drip-feed releases
- Simulated production API

---

## Data Ingestion

- dlt resources
- Incremental extraction
- Merge write disposition
- Primary-key upserts
- Cursor-based pagination
- Idempotent loads

---

## Transformations

- dbt-core
- Staging models
- Data quality tests
- SCD Type 2 snapshots
- Incremental fact tables
- Star schema modeling

---

# Known Limitations

### Late-arriving Dimensions

The source API intentionally releases historical data independently for each table.

As a result, a fact record may occasionally arrive before its corresponding dimension record.

This behavior is intentional because it mirrors real production systems and demonstrates how analytics pipelines handle late-arriving dimensions.

Additional details are documented in:

```
dbt_project/olist_analytics/README.md
```

---

# Roadmap

## ✅ Phase 1 — Source API

- FastAPI source system
- Cursor pagination
- Incremental filtering
- Background drip-feed

---

## ✅ Phase 2 — Data Ingestion

- dlt pipeline
- Incremental extraction
- Merge write disposition
- Bronze layer
- Dockerized pipeline

---

## ✅ Phase 3 — Data Transformation

- Bronze → Silver → Gold
- Staging models
- Data quality tests
- SCD Type 2 snapshots
- Incremental fact tables
- Star schema

---

## 🚧 Phase 4 — Orchestration

- Kestra workflows
- Scheduled ELT
- Dependency management

---

## 🚧 Phase 5 — Business Intelligence

- Apache Superset
- Interactive dashboards
- Business KPIs

---

## 🚧 Phase 6 — Production Readiness

- GitHub Actions CI/CD
- Automated testing
- Documentation
- Architecture diagrams
- End-to-end case study
- Performance optimizations

---

# Project Goals

This project demonstrates production-grade analytics engineering concepts including:

- Building a realistic source system
- Incremental ELT pipelines
- Cursor-based APIs
- Change-aware ingestion
- Medallion Architecture
- Dimensional modeling
- Slowly Changing Dimensions (SCD Type 2)
- Incremental fact loading
- Data quality testing
- Containerized development
- End-to-end analytics engineering
