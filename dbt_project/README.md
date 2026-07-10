# dbt Transformations

A [dbt](https://www.getdbt.com/) project transforming Olist e-commerce data through a **medallion architecture** (Bronze → Silver → Gold). Part of the [Olist ELT Platform](https://github.com/cleavestone/olist-elt-platform).

## Architecture

```
bronze.orders          ──▶ silver.stg_orders        ──▶ gold.dim_customers
bronze.customers       ──▶ silver.stg_customers     ──▶ gold.dim_sellers
bronze.sellers         ──▶ silver.stg_sellers       ──▶ gold.dim_products
bronze.products        ──▶ silver.stg_products      ──▶ gold.dim_date
bronze.order_items     ──▶ silver.stg_order_items   ──▶ gold.fct_orders
bronze.order_payments  ──▶ silver.stg_order_payments─▶ gold.fct_order_items
bronze.order_reviews   ──▶ silver.stg_order_reviews ──▶ gold.fct_payments
                                   │
                                   ▼
                           silver.int_order_details
```

## Layers

| Layer    | Schema   | Materialization | Description                        |
|----------|----------|-----------------|------------------------------------|
| Source   | `bronze` | —               | Raw data ingested by dlt           |
| Staging  | `silver` | View            | Column renaming, light cleaning    |
| Intermed.| `silver` | View            | Denormalized order details         |
| Marts    | `gold`   | Table/Incremental| Analytics-ready dimensional models |

## Getting Started

```bash
cd olist_analytics
dbt deps
dbt build
```

## Models

**Staging** (7 views):
- `stg_orders`, `stg_customers`, `stg_sellers`, `stg_products`
- `stg_order_items`, `stg_order_payments`, `stg_order_reviews`

**Intermediate** (1 view):
- `int_order_details` — denormalized order × items × products × sellers

**Marts** (7 tables):

| Model             | Type         | Description                                  |
|-------------------|--------------|----------------------------------------------|
| `dim_customers`   | Dimension    | Customer attributes with geography           |
| `dim_sellers`     | Dimension    | Seller attributes with geography             |
| `dim_products`    | SCD Type 2   | Product attributes with full change history  |
| `dim_date`        | Dimension    | Calendar (2015–2028) with date parts         |
| `fct_orders`      | Fact (incr)  | Order-level aggregated metrics               |
| `fct_order_items` | Fact (incr)  | Line-item-level facts                        |
| `fct_payments`    | Fact (incr)  | Payment-level facts                          |

## Snapshots

`products_snapshot` — SCD Type 2 (check strategy) tracking product attribute changes.
`dim_products` is built from this snapshot; current records have `dbt_valid_to IS NULL`.

## Tests

**Schema tests**: uniqueness, not-null, accepted_values on staging models.

**Custom tests**:
- `assert_products_snapshot_has_current` — every source product has an active snapshot
- `assert_order_value_matches_payments` — referential integrity check

## Orchestration

This project runs automatically via **Kestra** every 30 minutes:
1. `dbt snapshot`
2. `dbt run`
3. `dbt test`
