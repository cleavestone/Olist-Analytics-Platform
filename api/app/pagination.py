import base64
from datetime import datetime
from typing import Optional, Tuple

from fastapi import HTTPException
from sqlalchemy import and_, or_
from sqlalchemy.orm import Query

from app.config import settings


def encode_cursor(updated_at: datetime, row_id: int) -> str:
    raw = f"{updated_at.isoformat()}|{row_id}"
    return base64.urlsafe_b64encode(raw.encode()).decode()


def decode_cursor(cursor: str) -> Tuple[datetime, int]:
    try:
        raw = base64.urlsafe_b64decode(cursor.encode()).decode()
        ts_str, id_str = raw.rsplit("|", 1)
        return datetime.fromisoformat(ts_str), int(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid cursor")


def apply_cursor_pagination(
    query: Query,
    model,
    cursor: Optional[str],
    updated_at_gte: Optional[datetime],
    limit: int,
) -> Tuple[list, Optional[str], bool]:
    """
    Applies (optional) incremental filtering + cursor pagination to a query,
    executes it, and returns (rows, next_cursor, has_more).

    Ordering is always (updated_at ASC, id ASC) — oldest-changed-first —
    which is the natural order for incremental consumers replaying change
    history from a checkpoint.
    """
    query = query.filter(model.is_released.is_(True))

    if updated_at_gte is not None:
        query = query.filter(model.updated_at >= updated_at_gte)

    if cursor:
        cur_ts, cur_id = decode_cursor(cursor)
        query = query.filter(
            or_(
                model.updated_at > cur_ts,
                and_(model.updated_at == cur_ts, model.id > cur_id),
            )
        )

    query = query.order_by(model.updated_at.asc(), model.id.asc())

    # fetch one extra row to know whether there's a next page
    rows = query.limit(limit + 1).all()

    has_more = len(rows) > limit
    rows = rows[:limit]

    next_cursor = None
    if has_more and rows:
        last = rows[-1]
        next_cursor = encode_cursor(last.updated_at, last.id)

    return rows, next_cursor, has_more


def clamp_limit(limit: Optional[int]) -> int:
    if limit is None:
        return settings.default_page_size
    return max(1, min(limit, settings.max_page_size))