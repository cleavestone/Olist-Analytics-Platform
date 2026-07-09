# dbt Transformations

A [dbt](https://www.getdbt.com/) project that transforms raw Olist e-commerce data through a **medallion architecture** (Bronze → Silver → Gold).

## Architecture

```
Bronze (raw)                    Silver (cleaned)                 Gold (analytics-ready)
────────────                    ────────────────                 ──────────────────────
bronze.orders          ──▶     silver.stg_orders        ──▶     gold.dim_customers
bronze.customers       ──▶     silver.stg_customers     ──▶     gold.dim_sellers
bronze.sellers         ──▶     silver.stg_sellers       ──▶     gold.dim_date
bronze.products        ──▶     silver.stg_products
bronze.order_items     ──▶     silver.stg_order_items
bronze.order_payments  ──▶     silver.stg_order_payments
bronze.order_reviews   ──▶     silver.stg_order_reviews
```

## Layers

| Layer    | Schema   | Materialization | Description                        |
|----------|----------|-----------------|------------------------------------|
| Source   | `bronze` | —               | Raw data ingested by dlt           |
| Staging  | `silver` | View            | Column renaming, light cleaning    |
| Marts    | `gold`   | Table           | Analytics-ready dimensional models |

## Running

```bash
cd olist_analytics

# Install dependencies
dbt deps

# Run all models
dbt run

# Run with tests
dbt build

# Generate docs
dbt docs generate
dbt docs serve
```

## Staging Models

| Model              | Source             | Description                |
|--------------------|--------------------|----------------------------|
| `stg_orders`       | bronze.orders      | Order headers with timestamps |
| `stg_customers`    | bronze.customers   | Customer geography          |
| `stg_sellers`      | bronze.sellers     | Seller geography            |
| `stg_products`     | bronze.products    | Product attributes          |
| `stg_order_items`  | bronze.order_items | Line items with pricing    |
| `stg_order_payments`| bronze.order_payments | Payment transactions    |
| `stg_order_reviews`| bronze.order_reviews | Customer reviews         |

## Marts Models

| Model             | Description                                  |
|-------------------|----------------------------------------------|
| `dim_customers`   | Customer dimension with geography attributes |
| `dim_sellers`     | Seller dimension with geography attributes   |
| `dim_date`        | Calendar dimension (2015–2028) with date parts|

## Data Tests

Column-level tests are defined in `models/staging/_staging__models.yml` including:
- Uniqueness and not-null checks on primary keys
- Accepted values validation (e.g., payment types, review scores)

## Packages

- [dbt_utils](https://hub.getdbt.com/dbt-labs/dbt_utils/latest/) — provides the `date_spine` macro for the date dimension
