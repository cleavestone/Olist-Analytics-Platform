"""
dlt source for the Olist source API.

One @dlt.resource per table. Each resource:
1. Uses dlt's incremental() helper to track the last-seen `updated_at`
   between pipeline runs (persisted in dlt's own state, not something
   we manage ourselves).
2. Follows the API's cursor-based pagination (`next_cursor`) until
   `has_more` is False, yielding each page's rows as it goes.
"""
import dlt
import requests

BASE_URL = dlt.config.get("sources.olist_api.base_url", str) or "http://localhost:8000"


def _fetch_pages(endpoint: str, updated_at_gte: str | None):
    """
    Generator that walks every page of a given endpoint, starting from
    an optional incremental checkpoint, following `next_cursor` until
    the API says there's nothing more.
    """
    cursor = None
    while True:
        params = {"limit": 500}
        if cursor:
            params["cursor"] = cursor
        elif updated_at_gte:
            params["updated_at_gte"] = updated_at_gte

        resp = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=30)
        resp.raise_for_status()
        body = resp.json()

        yield from body["data"]

        if not body["has_more"]:
            break
        cursor = body["next_cursor"]


@dlt.source
def olist_api_source():

    @dlt.resource(name="orders", write_disposition="merge", primary_key="order_id")
    def orders(updated_at=dlt.sources.incremental("updated_at", initial_value="1970-01-01T00:00:00")):
        yield from _fetch_pages("orders", updated_at.last_value)

    @dlt.resource(name="order_items", write_disposition="merge", primary_key=["order_id", "order_item_id"])
    def order_items(updated_at=dlt.sources.incremental("updated_at", initial_value="1970-01-01T00:00:00")):
        yield from _fetch_pages("order_items", updated_at.last_value)

    @dlt.resource(name="order_payments", write_disposition="merge", primary_key=["order_id", "payment_sequential"])
    def order_payments(updated_at=dlt.sources.incremental("updated_at", initial_value="1970-01-01T00:00:00")):
        yield from _fetch_pages("order_payments", updated_at.last_value)

    @dlt.resource(name="order_reviews", write_disposition="merge", primary_key="review_id")
    def order_reviews(updated_at=dlt.sources.incremental("updated_at", initial_value="1970-01-01T00:00:00")):
        yield from _fetch_pages("order_reviews", updated_at.last_value)

    @dlt.resource(name="customers", write_disposition="merge", primary_key="customer_id")
    def customers(updated_at=dlt.sources.incremental("updated_at", initial_value="1970-01-01T00:00:00")):
        yield from _fetch_pages("customers", updated_at.last_value)

    @dlt.resource(name="sellers", write_disposition="merge", primary_key="seller_id")
    def sellers(updated_at=dlt.sources.incremental("updated_at", initial_value="1970-01-01T00:00:00")):
        yield from _fetch_pages("sellers", updated_at.last_value)

    @dlt.resource(name="products", write_disposition="merge", primary_key="product_id")
    def products(updated_at=dlt.sources.incremental("updated_at", initial_value="1970-01-01T00:00:00")):
        yield from _fetch_pages("products", updated_at.last_value)

    return orders, order_items, order_payments, order_reviews, customers, sellers, products