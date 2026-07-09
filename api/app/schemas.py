from datetime import datetime
from typing import Generic, TypeVar, List, Optional

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic envelope every list endpoint returns.

    `next_cursor` is an opaque, base64-encoded string. Consumers should
    treat it as a black box: pass it back as `?cursor=...` to get the
    next page. Don't try to decode/construct it manually — the encoding
    is an implementation detail and may change.
    """
    data: List[T]
    next_cursor: Optional[str] = None
    has_more: bool = False
    count: int


class CustomerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    customer_id: str
    customer_unique_id: str
    customer_zip_code_prefix: Optional[str] = None
    customer_city: Optional[str] = None
    customer_state: Optional[str] = None
    updated_at: datetime


class SellerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    seller_id: str
    seller_zip_code_prefix: Optional[str] = None
    seller_city: Optional[str] = None
    seller_state: Optional[str] = None
    updated_at: datetime


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: str
    product_category_name: Optional[str] = None
    product_name_length: Optional[float] = None
    product_description_length: Optional[float] = None
    product_photos_qty: Optional[float] = None
    product_weight_g: Optional[float] = None
    product_length_cm: Optional[float] = None
    product_height_cm: Optional[float] = None
    product_width_cm: Optional[float] = None
    updated_at: datetime


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: str
    customer_id: str
    order_status: Optional[str] = None
    order_purchase_timestamp: Optional[datetime] = None
    order_approved_at: Optional[datetime] = None
    order_delivered_carrier_date: Optional[datetime] = None
    order_delivered_customer_date: Optional[datetime] = None
    order_estimated_delivery_date: Optional[datetime] = None
    updated_at: datetime


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: str
    order_item_id: int
    product_id: str
    seller_id: str
    shipping_limit_date: Optional[datetime] = None
    price: Optional[float] = None
    freight_value: Optional[float] = None
    updated_at: datetime


class OrderPaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: str
    payment_sequential: Optional[int] = None
    payment_type: Optional[str] = None
    payment_installments: Optional[int] = None
    payment_value: Optional[float] = None
    updated_at: datetime


class OrderReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    review_id: str
    order_id: str
    review_score: Optional[int] = None
    review_comment_title: Optional[str] = None
    review_comment_message: Optional[str] = None
    review_creation_date: Optional[datetime] = None
    review_answer_timestamp: Optional[datetime] = None
    updated_at: datetime