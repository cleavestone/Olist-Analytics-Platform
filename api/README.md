# Olist Source API

A FastAPI service that simulates a production source system for the Olist e-commerce dataset. It exposes data through REST endpoints with incremental extraction support and a **drip-feed mechanism** that progressively releases rows over time.

## Features

- **7 REST endpoints** covering customers, sellers, products, orders, order items, payments, and reviews
- **Cursor-based pagination** with opaque base64-encoded cursors
- **Incremental extraction** via `updated_at_gte` query parameter
- **Drip-feed scheduler** — previously-held-back rows are progressively released so incremental consumers always find genuinely new data
- **PostgreSQL-backed** with composite indexes optimized for cursor pagination queries

## Endpoints

| Method | Path               | Description               |
|--------|--------------------|---------------------------|
| GET    | `/health`          | Health check              |
| GET    | `/customers`       | List customers            |
| GET    | `/sellers`         | List sellers              |
| GET    | `/products`        | List products             |
| GET    | `/orders`          | List orders               |
| GET    | `/order_items`     | List order items          |
| GET    | `/order_payments`  | List order payments       |
| GET    | `/order_reviews`   | List order reviews        |

### Query Parameters

All list endpoints accept:

| Parameter       | Type     | Description                                          |
|-----------------|----------|------------------------------------------------------|
| `cursor`        | string   | Opaque pagination cursor from previous response      |
| `updated_at_gte`| datetime | Filter rows changed at or after this timestamp        |
| `limit`         | integer  | Page size (default: 100, max: 500)                   |

### Response Format

```json
{
  "data": [...],
  "next_cursor": "eyIyMDI0...",
  "has_more": true,
  "count": 100
}
```

## Data Flow

```
Olist CSVs → load_csv_to_db.py → API DB (Postgres)
                                      │
                                      ▼
                              FastAPI (port 8000)
                                      │
                              ←── dlt pipeline ──→
```

## Configuration

Settings are managed via `app/config.py` using `pydantic-settings`:

| Variable                    | Default  | Description                     |
|-----------------------------|----------|---------------------------------|
| `DATABASE_URL`              | postgresql://... | API backing database      |
| `drip_feed_batch_size`      | 200      | Rows released per tick per table|
| `drip_feed_interval_seconds`| 300      | Drip-feed interval (5 min)      |
| `default_page_size`         | 100      | Default pagination limit        |
| `max_page_size`             | 500      | Maximum pagination limit        |

## Seeding the Database

Place the [Olist Kaggle CSV files](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) in `api/data/raw/` and run:

```bash
uv run python -m scripts.load_csv_to_db
```

The loader applies a time shift so historical data appears recent, and marks ~20% of rows as "held back" for the drip-feed scheduler to release gradually.

## Drip-Feed Mechanism

The background scheduler (APScheduler) runs every 5 minutes and releases a batch of previously-unreleased rows per table. Each released row gets a new `updated_at` timestamp, making it visible to incremental consumers on their next poll.
