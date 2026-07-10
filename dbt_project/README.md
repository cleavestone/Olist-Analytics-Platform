# Olist Analytics — dbt Project

The transformation layer of the **Olist ELT Analytics Platform**.

This project transforms raw data loaded into the **Bronze** layer by the `dlt_pipeline` into analytics-ready dimensional models using **dbt-core**.

The project implements a complete **Medallion Architecture (Bronze → Silver → Gold)** featuring:

* Staging models
* Data quality testing
* Slowly Changing Dimensions (SCD Type 2)
* Incremental fact tables
* Star schema modeling
* Documentation and lineage generation

---

# Project Architecture

```text
                     Bronze Schema
          (Raw tables loaded by dlt)
                           │
                           ▼
                  Staging Models (Silver)
        ─────────────────────────────────────
        • stg_customers
        • stg_sellers
        • stg_products
        • stg_orders
        • stg_order_items
        • stg_order_payments
        • stg_order_reviews
                           │
                           ▼
              Data Quality Tests
         • unique
         • not_null
         • accepted_values
                           │
                           ▼
                 SCD Type 2 Snapshot
                 products_snapshot
                           │
                           ▼
                   Gold Star Schema
        ─────────────────────────────────────
        Dimensions
        • dim_date
        • dim_customers
        • dim_sellers
        • dim_products (SCD2)

        Facts
        • fct_orders
        • fct_order_items
        • fct_payments
```

---

# Medallion Architecture

## Bronze

The Bronze layer contains raw data ingested by the `dlt_pipeline`.

Characteristics:

* One-to-one copy of the source API
* Minimal transformations
* Merge-based incremental loading
* Operational data preserved

---

## Silver

The Silver layer standardizes and validates the raw data.

Responsibilities include:

* Data cleaning
* Type casting
* Renaming columns
* Data quality testing
* Business-friendly staging models

Every staging model is materialized as a **view**.

---

## Gold

The Gold layer contains analytics-ready models built using dimensional modeling principles.

### Dimension Tables

* `dim_date`
* `dim_customers`
* `dim_sellers`
* `dim_products` *(SCD Type 2)*

### Fact Tables

* `fct_orders`
* `fct_order_items`
* `fct_payments`

All fact tables are incrementally maintained using merge strategies.

---

# Setup

Install dependencies:

```bash
uv sync

uv run dbt deps
```

The project depends on:

* `dbt-core`
* `dbt-postgres`
* `dbt-utils`

---

## Configure the dbt Profile

Create or update:

```text
~/.dbt/profiles.yml
```

Connection options:

* **Host machine**

```text
localhost:5434
```

* **Docker network**

```text
warehouse_db:5432
```

Verify the connection:

```bash
uv run dbt debug
```

---

# Running the Project

Run the complete transformation pipeline.

```bash
uv run dbt snapshot

uv run dbt run

uv run dbt test
```

Execution order matters.

The snapshot must run first because downstream models depend on it.

---

# Custom Schema Naming

By default, dbt prefixes custom schemas using the active target schema.

For example:

```text
dbt_dev_silver
```

instead of

```text
silver
```

This project overrides the default behavior using:

```text
macros/get_custom_schema.sql
```

allowing:

```yaml
schema: silver
schema: gold
```

to generate exactly those schema names.

---

# Slowly Changing Dimensions (SCD Type 2)

## products_snapshot

The project tracks historical product changes using dbt snapshots.

Snapshot file:

```text
snapshots/products_snapshot.sql
```

Tracked attributes include:

* Product category
* Weight
* Height
* Width
* Length

---

## Why Use `strategy='check'`?

Although the source API continuously updates the operational `updated_at` column during drip-feed releases, most product attributes remain unchanged.

Using:

```sql
strategy='timestamp'
```

would incorrectly create a new historical version every time the operational timestamp changed.

Instead the snapshot uses:

```sql
strategy='check'
```

which only creates a new version when monitored business attributes actually change.

This eliminates false SCD records while preserving genuine history.

---

## Current Product Dimension

`dim_products` exposes only the latest version:

```sql
where dbt_valid_to is null
```

Historical versions remain available in:

```text
products_snapshot
```

for point-in-time analysis.

---

# Incremental Fact Tables

The following models are incremental:

* `fct_orders`
* `fct_order_items`
* `fct_payments`

Each model uses merge-based incremental loading.

Typical configuration:

```sql
{{ config(
    materialized='incremental',
    unique_key=...,
    incremental_strategy='merge'
) }}

{% if is_incremental() %}
where _source_updated_at >
(
    select max(_source_updated_at)
    from {{ this }}
)
{% endif %}
```

---

## Incremental Behavior

The implementation has been verified end-to-end.

### Initial Run

Performs a full load.

```text
SELECT ...
```

### Subsequent Run (No New Data)

Produces:

```text
MERGE 0
```

demonstrating that dbt correctly skips unchanged data instead of rebuilding the table.

---

## Current Limitation

`fct_orders` currently determines incremental changes using only:

```text
stg_orders._source_updated_at
```

Therefore:

* updates to payments
* updates to order items

will not automatically trigger reprocessing of the corresponding order record.

A more complete implementation would compare the latest timestamp across every joined source table.

---

# Late-Arriving Dimensions

The FastAPI source system intentionally releases each table independently.

As a result:

* Orders may appear before customers
* Order items may appear before products
* Payments may appear before orders

This accurately simulates late-arriving dimensions commonly encountered in production data warehouses.

---

## Expected Test Failures

Temporary failures may appear in:

* Relationship tests
* Referential integrity checks
* Order value reconciliation tests
* Product snapshot validation tests

These failures are expected during the inconsistency window and serve as **data quality monitors**, not transformation bugs.

---

## Production Mitigations

Typical approaches include:

* Load dimensions before facts
* Increase pipeline frequency
* Monitor test failure trends
* Retry downstream transformations

Improving the drip-feed scheduling strategy is a planned enhancement.

---

# Data Quality Testing

The project contains **39 automated tests** covering:

### Generic Tests

* `unique`
* `not_null`
* `accepted_values`
* `relationships`

---

### Accepted Values

Examples include:

* Payment type
* Review score

---

### Relationship Tests

Verify referential integrity between:

* Fact tables
* Dimension tables

---

### Custom Singular Tests

The project also includes custom SQL tests validating:

* Order totals equal payment totals
* Every SCD snapshot has a current active record

---

# Documentation

Generate project documentation:

```bash
uv run dbt docs generate
```

Serve documentation locally:

```bash
uv run dbt docs serve
```

The generated documentation includes:

* Model documentation
* Column documentation
* Data lineage
* Dependency graph
* Bronze → Silver → Gold flow
* Snapshot lineage
* Star schema visualization

---

# Project Highlights

This project demonstrates production-grade analytics engineering techniques including:

* Medallion Architecture
* Dimensional Modeling
* Star Schema Design
* Slowly Changing Dimensions (SCD Type 2)
* Incremental Fact Loading
* Merge Strategies
* dbt Snapshots
* Data Quality Testing
* Referential Integrity Validation
* Automated Documentation
* Lineage Generation
* Production-Oriented ELT Design
