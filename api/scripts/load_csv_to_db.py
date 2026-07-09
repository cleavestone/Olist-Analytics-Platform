"""
One-time loader: raw Olist CSVs -> API backing database.

WHAT THIS DOES
---------------
1. Reads the standard Olist Kaggle CSVs from api/data/raw/
2. Computes a single global time shift so the LATEST timestamp in the
   whole dataset lands at "now minus a hold-back window". Every date
   column in every table is shifted by the same offset, so relative
   ordering/spacing between all tables is preserved exactly.
3. For order-related tables, the most recent slice (by business date) is
   marked `is_released=False` — held back — so the drip-feed job has
   something to progressively reveal. Dimension-ish tables
   (customers/sellers/products) get a similar holdback by insertion order.
4. Bulk-inserts everything into Postgres via SQLAlchemy.

Run with:  uv run python -m scripts.load_csv_to_db
"""
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sqlalchemy import text

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.database import Base, engine  # noqa: E402
from app.models import (  # noqa: E402
    Customer, Seller, Product, Order, OrderItem, OrderPayment, OrderReview,
)

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"

HOLDBACK_FRACTION = 0.20
HOLDBACK_WINDOW_DAYS = 3

ORDER_DATE_COLS = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]


def read_csv(name: str, parse_dates=None) -> pd.DataFrame:
    path = RAW_DIR / name
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path}. Place the Olist CSVs in {RAW_DIR}"
        )
    return pd.read_csv(path, parse_dates=parse_dates)


def compute_shift(orders: pd.DataFrame) -> pd.Timedelta:
    max_ts = orders["order_purchase_timestamp"].max()
    target_latest = pd.Timestamp(datetime.now(timezone.utc)).tz_localize(None) - pd.Timedelta(
        days=HOLDBACK_WINDOW_DAYS
    )
    return target_latest - max_ts


def shift_dates(df: pd.DataFrame, cols, shift: pd.Timedelta) -> pd.DataFrame:
    for col in cols:
        if col in df.columns:
            df[col] = df[col] + shift
    return df


def mark_holdback_by_date(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    df = df.sort_values(date_col, na_position="first").reset_index(drop=True)
    cutoff_idx = int(len(df) * (1 - HOLDBACK_FRACTION))
    df["is_released"] = True
    df.loc[cutoff_idx:, "is_released"] = False
    df["updated_at"] = df[date_col] + pd.to_timedelta(df.index, unit="us")
    return df


def mark_holdback_by_order(df: pd.DataFrame) -> pd.DataFrame:
    df = df.reset_index(drop=True)
    cutoff_idx = int(len(df) * (1 - HOLDBACK_FRACTION))
    df["is_released"] = True
    df.loc[cutoff_idx:, "is_released"] = False
    now = pd.Timestamp(datetime.now(timezone.utc)).tz_localize(None) - pd.Timedelta(days=HOLDBACK_WINDOW_DAYS)
    df["updated_at"] = now + pd.to_timedelta(df.index, unit="us")
    return df


def bulk_load(df: pd.DataFrame, table_name: str):
    df.to_sql(table_name, engine, if_exists="append", index=False, method="multi", chunksize=1000)
    print(f"  loaded {len(df):>7,} rows -> {table_name}")


def main():
    print(f"Reading raw CSVs from {RAW_DIR}")

    customers = read_csv("olist_customers_dataset.csv")
    sellers = read_csv("olist_sellers_dataset.csv")
    products = read_csv("olist_products_dataset.csv")
    products = products.rename(columns={
    "product_name_lenght": "product_name_length",
    "product_description_lenght": "product_description_length",
})
    orders = read_csv("olist_orders_dataset.csv", parse_dates=ORDER_DATE_COLS)
    order_items = read_csv("olist_order_items_dataset.csv", parse_dates=["shipping_limit_date"])
    payments = read_csv("olist_order_payments_dataset.csv")
    reviews = read_csv(
        "olist_order_reviews_dataset.csv",
        parse_dates=["review_creation_date", "review_answer_timestamp"],
    )

    shift = compute_shift(orders)
    print(f"Computed global time shift: {shift}")

    orders = shift_dates(orders, ORDER_DATE_COLS, shift)
    order_items = shift_dates(order_items, ["shipping_limit_date"], shift)
    reviews = shift_dates(reviews, ["review_creation_date", "review_answer_timestamp"], shift)

    orders = mark_holdback_by_date(orders, "order_purchase_timestamp")
    order_items = mark_holdback_by_date(order_items, "shipping_limit_date")
    reviews = mark_holdback_by_date(reviews, "review_creation_date")
    payments = mark_holdback_by_order(payments)
    customers = mark_holdback_by_order(customers)
    sellers = mark_holdback_by_order(sellers)
    products = mark_holdback_by_order(products)

    print("Creating tables (if not exist)...")
    Base.metadata.create_all(engine)

    with engine.begin() as conn:
        for tbl in (
            "order_reviews", "order_payments", "order_items", "orders",
            "products", "sellers", "customers",
        ):
            conn.execute(text(f"TRUNCATE TABLE {tbl} RESTART IDENTITY CASCADE"))

    print("Loading tables...")
    bulk_load(customers, Customer.__tablename__)
    bulk_load(sellers, Seller.__tablename__)
    bulk_load(products, Product.__tablename__)
    bulk_load(orders, Order.__tablename__)
    bulk_load(order_items, OrderItem.__tablename__)
    bulk_load(payments, OrderPayment.__tablename__)
    bulk_load(reviews, OrderReview.__tablename__)

    released = sum(
        int(df["is_released"].sum())
        for df in (customers, sellers, products, orders, order_items, payments, reviews)
    )
    total = sum(
        len(df) for df in (customers, sellers, products, orders, order_items, payments, reviews)
    )
    print(f"\nDone. {released:,}/{total:,} rows released initially; "
          f"remainder will drip-feed in via the scheduler.")


if __name__ == "__main__":
    main()