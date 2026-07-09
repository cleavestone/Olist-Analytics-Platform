# Olist Source API

A production-inspired **FastAPI** service that simulates a real-world source system for analytics engineering.

Instead of reading static CSV files, this service exposes the **Olist Brazilian E-Commerce dataset** through a REST API featuring:

* Cursor-based pagination
* Incremental extraction
* Background data releases (drip-feed)
* PostgreSQL-backed storage
* Production-like API behavior

This API serves as the source system for the ELT pipeline and is consumed incrementally by **dlt**.

---

# Why Build a Source API Instead of Reading CSV Files?

Many ELT portfolio projects simply point an ingestion tool at a CSV file.

While useful for learning, this skips the real engineering challenges involved in extracting data from production systems.

This project instead simulates the kind of internal microservice an analytics engineer would typically integrate with.

The API supports:

* **Cursor-based pagination** (`next_cursor`)
* **Incremental extraction** using `updated_at_gte`
* **Background drip-feed releases**
* **Live data appearing over time**

This allows downstream ingestion tools to solve realistic problems such as:

* Pagination
* Incremental loading
* Upserts
* Late-arriving data
* Scheduled polling

rather than performing a one-time file import.

---

# Architecture

```text
                 Kaggle Olist Dataset
                         │
                         ▼
               CSV Loader Script
                         │
                         ▼
               PostgreSQL (api_db)
                         │
                         ▼
                  FastAPI Service
         ┌────────────────────────────────┐
         │                                │
         │ Cursor Pagination              │
         │ Incremental Filtering          │
         │ Background Drip-feed           │
         │ REST Endpoints                 │
         └────────────────────────────────┘
                         │
                         ▼
                  dlt Incremental Loader
```

---

# Features

## Cursor-Based Pagination

The API uses opaque cursors instead of traditional offset/limit pagination.

Example:

```http
GET /orders?cursor=eyJpZCI6...
```

Cursor pagination is significantly more reliable for continuously changing datasets because new rows arriving during pagination do not shift previously unseen records.

Each response returns:

```json
{
  "data": [...],
  "next_cursor": "opaque-string-or-null",
  "has_more": true,
  "count": 100
}
```

---

## Incremental Extraction

Every endpoint supports filtering by the latest modification timestamp.

Example:

```http
GET /orders?updated_at_gte=2026-07-01T00:00:00
```

This allows ingestion tools such as **dlt** to fetch only newly created or updated records.

---

## Background Drip-Feed

To simulate a continuously changing production database:

* Approximately **20%** of historical rows are withheld during the initial load.
* A background scheduler periodically releases additional records.
* Newly released records receive fresh `updated_at` timestamps.

As a result, every scheduled ingestion run discovers genuinely new records without fabricating data.

---

# Project Setup

## 1. Download the Dataset

Download the **Olist Brazilian E-Commerce Dataset** from Kaggle.

Place the following CSV files inside:

```text
data/raw/
```

Required files:

```text
olist_customers_dataset.csv
olist_sellers_dataset.csv
olist_products_dataset.csv
olist_orders_dataset.csv
olist_order_items_dataset.csv
olist_order_payments_dataset.csv
olist_order_reviews_dataset.csv
```

---

## 2. Start the API

Build and start the API together with its PostgreSQL database.

```bash
docker compose up -d --build api_db api
```

---

## 3. Load the Dataset

Populate the source database.

```bash
docker compose exec api uv run python -m scripts.load_csv_to_db
```

This process:

* Loads the Kaggle dataset
* Shifts historical timestamps to the current timeline
* Holds back approximately 20% of records
* Assigns unique `updated_at` timestamps
* Bulk inserts data into PostgreSQL

The loader is **idempotent** and can safely be re-run against a fresh database.

---

## 4. Test the API

Example request:

```bash
curl "http://localhost:8000/orders?limit=5"
```

Interactive Swagger documentation:

```text
http://localhost:8000/docs
```

---

# API Endpoints

| Endpoint                | Source Table                     |
| ----------------------- | -------------------------------- |
| `GET /customers`      | `olist_customers_dataset`      |
| `GET /sellers`        | `olist_sellers_dataset`        |
| `GET /products`       | `olist_products_dataset`       |
| `GET /orders`         | `olist_orders_dataset`         |
| `GET /order_items`    | `olist_order_items_dataset`    |
| `GET /order_payments` | `olist_order_payments_dataset` |
| `GET /order_reviews`  | `olist_order_reviews_dataset`  |

Every endpoint supports:

| Parameter          | Description                                |
| ------------------ | ------------------------------------------ |
| `cursor`         | Continue pagination                        |
| `updated_at_gte` | Incremental extraction                     |
| `limit`          | Number of records (default: 100, max: 500) |

---

# A Critical Design Decision

## Why Every Row Has a Unique `updated_at`

One of the most important engineering lessons from this project involved incremental extraction.

### Initial Implementation

Originally, every row released within the same batch received an identical `updated_at` timestamp.

Although this appeared realistic, it introduced an unexpected performance problem.

Since **dlt** tracks incremental progress using cursor values, thousands of rows sharing the same timestamp caused enormous bookkeeping overhead.

A complete ingestion run eventually required **over four hours** before being terminated.

---

### Final Solution

Each released row now receives a unique timestamp by offsetting its `updated_at` value by a few microseconds.

This logic is implemented in:

```text
scripts/load_csv_to_db.py
```

Functions:

* `mark_holdback_by_date`
* `mark_holdback_by_order`

and during live releases inside:

```text
app/scheduler.py
```

Function:

* `_release_batch`

This guarantees:

* Every row has a unique incremental cursor
* Business ordering is preserved
* Incremental ingestion remains highly efficient

---

# Monitoring the Drip-Feed

Follow the API logs:

```bash
docker compose logs -f api
```

Example output:

```text
[drip-feed] released 500 rows at 2026-07-10T14:30:00
```

The scheduler releases new data approximately every five minutes.

The interval is configurable in:

```text
app/config.py
```

```python
DRIP_FEED_INTERVAL_SECONDS
```

---

# Key Engineering Concepts Demonstrated

This source system intentionally models several production-grade data engineering patterns:

* RESTful API design
* Cursor-based pagination
* Incremental extraction
* Change-aware data ingestion
* PostgreSQL-backed source systems
* Background scheduling
* Late-arriving data
* Production-style timestamp management
* Idempotent data loading
* Realistic analytics engineering workflows

---

# Role Within the ELT Platform

This API represents the **source system** of the overall analytics platform.

```text
Kaggle Dataset
      │
      ▼
 FastAPI Source API
      │
      ▼
 dlt Incremental Loader
      │
      ▼
 Bronze Layer
      │
      ▼
 dbt Silver
      │
      ▼
 dbt Gold
      │
      ▼
 Superset Dashboards
```
