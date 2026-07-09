# Olist Analytics (dbt)

A [dbt](https://www.getdbt.com/) project transforming Olist e-commerce data through a medallion architecture. Part of the [Olist ELT Platform](https://github.com/cleavestone/olist-elt-platform).

## Models

- **Staging** (`silver` schema, views) — Renames columns and lightly cleans raw data
- **Marts** (`gold` schema, tables) — Analytics-ready dimensional models

## Getting Started

```bash
dbt deps
dbt build
```

## Sources

Data is sourced from the `bronze` schema, populated by the dlt ingestion pipeline.
