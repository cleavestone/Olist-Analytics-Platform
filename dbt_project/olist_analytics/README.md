# Olist Analytics (dbt)

A [dbt](https://www.getdbt.com/) project transforming Olist e-commerce data through a medallion architecture (Bronze → Silver → Gold). Part of the [Olist ELT Platform](https://github.com/cleavestone/olist-elt-platform).

## Models

**Staging** (silver schema, views):
- `stg_orders`, `stg_customers`, `stg_sellers`, `stg_products`
- `stg_order_items`, `stg_order_payments`, `stg_order_reviews`

**Intermediate** (silver schema, view):
- `int_order_details` — denormalized order × items × products × sellers

**Marts** (gold schema, tables):

| Model             | Type         | Description                                  |
|-------------------|--------------|----------------------------------------------|
| `dim_customers`   | Dimension    | Customer geography                           |
| `dim_sellers`     | Dimension    | Seller geography                             |
| `dim_products`    | SCD Type 2   | Product attributes with full history         |
| `dim_date`        | Dimension    | Calendar (2015–2028)                         |
| `fct_orders`      | Fact (incr)  | Order-level aggregated metrics               |
| `fct_order_items` | Fact (incr)  | Line-item-level facts                        |
| `fct_payments`    | Fact (incr)  | Payment-level facts                          |

## Running

```bash
dbt deps
dbt build      # run + snapshot + test
dbt snapshot   # SCD Type 2 only
dbt docs generate
dbt docs serve
```

## Sources

Data is sourced from the `bronze` schema, populated by the dlt ingestion pipeline.
