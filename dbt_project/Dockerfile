FROM python:3.11-slim

RUN pip install --default-timeout=3600 --no-cache-dir "dbt-core>=1.11.12" "dbt-postgres>=1.10.2"

WORKDIR /app

ENTRYPOINT ["dbt"]