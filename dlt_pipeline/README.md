# dlt Ingestion Pipeline

Ingests data from the [Olist source API](../api/README.md) into the
analytics warehouse's `bronze` schema, using genuine cursor-based
incremental extraction — not a one-time bulk load.

## What this does

- One `@dlt.resource` per source table (`orders`, `order_items`,
  `order_payments`, `order_reviews`, `customers`, `sellers`, `products`)
- Each resource uses `dlt.sources.incremental("updated_at", ...)` to track
  a per-resource checkpoint between runs, persisted in dlt's own state
  (stored in the destination, not managed manually)
- Pagination follows the API's `next_cursor` within each pull; the
  incremental `updated_at_gte` value only sets the *starting* point
- `write_disposition="merge"` with a primary key on every resource —
  rows are upserted, not blindly appended, since the source's drip-feed
  can re-stamp a row's `updated_at` when released

## Setup

Requires `api` and `warehouse_db` running (see root README).

```bash
uv sync
```

### Local development (running outside Docker)

`.dlt/config.toml` and `.dlt/secrets.toml` are pre-configured for
**containerized** execution (`api:8000`, `warehouse_db:5432` — Docker
service names). For quick local testing directly from a WSL2/host
terminal, temporarily point them at host-mapped ports instead:

```toml
# .dlt/config.toml
[sources.olist_api]
base_url = "http://localhost:8000"
```

```toml
# .dlt/secrets.toml
[destination.postgres.credentials]
host = "localhost"
port = 5434
```

Then run directly:

```bash
uv run python run_pipeline.py
```

### Containerized (matches how Kestra will invoke this in Phase 4)

Config is set to `api:8000` / `warehouse_db:5432` by default — this is
the intended way to run the pipeline.

```bash
docker compose build dlt_pipeline
docker compose run --rm dlt_pipeline
```

## A real bug we hit and fixed: tied-cursor dedup blowup

Early runs against `order_reviews` took **over 4 hours** before being
killed. Root cause: the drip-feed originally stamped every row in a
released batch with the *identical* `updated_at` timestamp. dlt's
incremental logic keeps a dedup bookkeeping set per unique cursor value —
with hundreds of rows sharing one timestamp, this set grew large enough
to make the pipeline effectively unusable.

**Fix**: every row released (both in the initial bulk load and the
drip-feed) now gets a unique `updated_at`, offset by microseconds within
its batch (see `api/app/scheduler.py` and
`api/scripts/load_csv_to_db.py`). Post-fix, a full run of `order_reviews`
(~99k rows) completes in ~20 seconds.

## Verifying incremental extraction works

```bash
uv run python run_pipeline.py   # first run: full load
uv run python run_pipeline.py   # second run: should log "Found 0 files",
                                 # complete in <1s if nothing new released
```

## Known limitation

Each fact-like resource's incremental filter only checks its own
`_source_updated_at`. A change to a *related* table (e.g. a payment
changing without the parent order changing) won't retrigger reprocessing
of the order itself at the dbt layer — see `dbt_project/olist_analytics/README.md`
for how this surfaces downstream.
