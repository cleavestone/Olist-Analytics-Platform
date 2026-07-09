from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.pagination import apply_cursor_pagination, clamp_limit
from app.scheduler import start_scheduler

app = FastAPI(
    title="Olist Source API",
    description=(
        "Simulated production source system exposing Olist e-commerce data. "
        "Supports cursor-based pagination and incremental extraction via "
        "`updated_at_gte`, and drip-feeds previously-held-back rows over "
        "time so incremental consumers have genuinely new data to pick up "
        "on each run."
    ),
    version="1.0.0",
)


@app.on_event("startup")
def on_startup():
    start_scheduler()


@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}


def _list_endpoint(db: Session, model, schema, cursor, updated_at_gte, limit):
    limit = clamp_limit(limit)
    query = db.query(model)
    rows, next_cursor, has_more = apply_cursor_pagination(
        query, model, cursor, updated_at_gte, limit
    )
    return schemas.PaginatedResponse[schema](
        data=[schema.model_validate(r) for r in rows],
        next_cursor=next_cursor,
        has_more=has_more,
        count=len(rows),
    )


@app.get("/customers", response_model=schemas.PaginatedResponse[schemas.CustomerOut])
def list_customers(
    cursor: Optional[str] = None,
    updated_at_gte: Optional[datetime] = Query(None),
    limit: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    return _list_endpoint(db, models.Customer, schemas.CustomerOut, cursor, updated_at_gte, limit)


@app.get("/sellers", response_model=schemas.PaginatedResponse[schemas.SellerOut])
def list_sellers(
    cursor: Optional[str] = None,
    updated_at_gte: Optional[datetime] = Query(None),
    limit: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    return _list_endpoint(db, models.Seller, schemas.SellerOut, cursor, updated_at_gte, limit)


@app.get("/products", response_model=schemas.PaginatedResponse[schemas.ProductOut])
def list_products(
    cursor: Optional[str] = None,
    updated_at_gte: Optional[datetime] = Query(None),
    limit: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    return _list_endpoint(db, models.Product, schemas.ProductOut, cursor, updated_at_gte, limit)


@app.get("/orders", response_model=schemas.PaginatedResponse[schemas.OrderOut])
def list_orders(
    cursor: Optional[str] = None,
    updated_at_gte: Optional[datetime] = Query(None),
    limit: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    return _list_endpoint(db, models.Order, schemas.OrderOut, cursor, updated_at_gte, limit)


@app.get("/order_items", response_model=schemas.PaginatedResponse[schemas.OrderItemOut])
def list_order_items(
    cursor: Optional[str] = None,
    updated_at_gte: Optional[datetime] = Query(None),
    limit: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    return _list_endpoint(db, models.OrderItem, schemas.OrderItemOut, cursor, updated_at_gte, limit)


@app.get("/order_payments", response_model=schemas.PaginatedResponse[schemas.OrderPaymentOut])
def list_order_payments(
    cursor: Optional[str] = None,
    updated_at_gte: Optional[datetime] = Query(None),
    limit: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    return _list_endpoint(db, models.OrderPayment, schemas.OrderPaymentOut, cursor, updated_at_gte, limit)


@app.get("/order_reviews", response_model=schemas.PaginatedResponse[schemas.OrderReviewOut])
def list_order_reviews(
    cursor: Optional[str] = None,
    updated_at_gte: Optional[datetime] = Query(None),
    limit: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    return _list_endpoint(db, models.OrderReview, schemas.OrderReviewOut, cursor, updated_at_gte, limit)