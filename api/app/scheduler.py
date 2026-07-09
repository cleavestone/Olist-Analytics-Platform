from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.background import BackgroundScheduler

from app.config import settings
from app.database import SessionLocal
from app.models import Customer, Seller, Product, Order, OrderItem, OrderPayment, OrderReview

# (model, column to order the held-back pool by)
_RELEASE_PLAN = [
    (Customer, Customer.id),
    (Seller, Seller.id),
    (Product, Product.id),
    (Order, Order.order_purchase_timestamp),
    (OrderItem, OrderItem.shipping_limit_date),
    (OrderPayment, OrderPayment.id),
    (OrderReview, OrderReview.review_creation_date),
]

_scheduler = BackgroundScheduler()


def _release_batch():
    db = SessionLocal()
    base_now = datetime.now(timezone.utc).replace(tzinfo=None)
    total_released = 0
    try:
        for model, order_col in _RELEASE_PLAN:
            pending = (
                db.query(model)
                .filter(model.is_released.is_(False))
                .order_by(order_col.asc().nullslast())
                .limit(settings.drip_feed_batch_size)
                .all()
            )
            for i, row in enumerate(pending):
                row.is_released = True
                row.updated_at = base_now + timedelta(microseconds=i)
            total_released += len(pending)
        db.commit()
        if total_released:
            print(f"[drip-feed] released {total_released} rows at {base_now.isoformat()}")
    finally:
        db.close()

def start_scheduler():
    if _scheduler.running:
        return
    _scheduler.add_job(
        _release_batch,
        "interval",
        seconds=settings.drip_feed_interval_seconds,
        id="drip_feed_release",
        replace_existing=True,
        max_instances=1,
    )
    _scheduler.start()
    print(
        f"[drip-feed] scheduler started — releasing up to "
        f"{settings.drip_feed_batch_size} rows/table every "
        f"{settings.drip_feed_interval_seconds}s"
    )