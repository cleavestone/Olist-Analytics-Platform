# dlt Ingestion Pipeline

Extracts Olist e-commerce data from the FastAPI source service and loads it into the Postgres analytics warehouse using [dlt](https://dlthub.com/).

## Features

- **7 incremental resources** — one per API endpoint (customers, sellers, products, orders, order items, order payments, order reviews)
- **Incremental loading** — uses dlt's `incremental()` helper to track `updated_at` checkpoints between runs
- **Merge write disposition** — idempotent re-runs using natural primary keys
- **Cursor-based pagination** — follows `next_cursor` across API pages until exhaustion
- **Bronze schema** — all data lands in the `bronze` schema of the warehouse database

## How It Works

```
FastAPI Source (port 8000)               Warehouse Postgres (port 5434)
         │                                          │
         │  GET /orders?cursor=...                   │
         │  GET /customers?cursor=...                │
         │  ...                                      │
         └───────────── dlt pipeline ────────────────▶│
                                                      │
                                              bronze.orders
                                              bronze.customers
                                              bronze.products
                                              ...
```

## Resources

| Resource         | Endpoint          | Primary Key           |
|------------------|-------------------|-----------------------|
| `orders`         | `/orders`         | `order_id`            |
| `order_items`    | `/order_items`    | `order_id`, `order_item_id` |
| `order_payments` | `/order_payments` | `order_id`, `payment_sequential` |
| `order_reviews`  | `/order_reviews`  | `review_id`           |
| `customers`      | `/customers`      | `customer_id`         |
| `sellers`        | `/sellers`        | `seller_id`           |
| `products`       | `/products`       | `product_id`          |

## Running

```bash
# Standalone (requires API running at localhost:8000)
uv run python run_pipeline.py

# Via Docker Compose (auto-wired to the api container)
docker compose --profile manual run --rm dlt_pipeline
```

## Configuration

| Setting                       | Default               | Description                |
|-------------------------------|-----------------------|----------------------------|
| `sources.olist_api.base_url`  | `http://api:8000`     | Base URL for the API       |
| `destination.postgres.credentials` | DLT\_DESTINATION\_... | Postgres warehouse credentials |

Credentials and destination settings are managed through dlt's standard [secrets/config](https://dlthub.com/docs/general-usage/credentials) system (environment variables or `secrets.toml`).

## Design Notes

- Each resource uses `dlt.sources.incremental("updated_at", initial_value="1970-01-01T00:00:00")` to track progress
- The pipeline name is `olist_elt_pipeline`, used by dlt to persist state between runs
- API requests are made at 500-row page sizes for throughput
