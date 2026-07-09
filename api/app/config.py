from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configuration for the Olist source API.

    DATABASE_URL points at the API's OWN backing database — this is
    intentionally separate from the analytics warehouse Postgres instance
    that dlt will load into. This service just SERVES data, it does not
    do any analytics transformation.
    """

    database_url: str = "postgresql://olist_api:olist_api@api_db:5432/olist_api"

    # How many rows to release from the "pending" pool each drip-feed tick
    drip_feed_batch_size: int = 200

    # How often the background job runs (seconds)
    drip_feed_interval_seconds: int = 300  # every 5 minutes

    # Default / max page size for pagination
    default_page_size: int = 100
    max_page_size: int = 500

    class Config:
        env_file = ".env"


settings = Settings()