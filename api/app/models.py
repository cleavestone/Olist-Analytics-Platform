from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Index

from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String, unique=True, nullable=False)
    customer_unique_id = Column(String, nullable=False)
    customer_zip_code_prefix = Column(String)
    customer_city = Column(String)
    customer_state = Column(String)

    updated_at = Column(DateTime, nullable=False)
    is_released = Column(Boolean, default=False, nullable=False)


class Seller(Base):
    __tablename__ = "sellers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    seller_id = Column(String, unique=True, nullable=False)
    seller_zip_code_prefix = Column(String)
    seller_city = Column(String)
    seller_state = Column(String)

    updated_at = Column(DateTime, nullable=False)
    is_released = Column(Boolean, default=False, nullable=False)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String, unique=True, nullable=False)
    product_category_name = Column(String)
    product_name_length = Column(Float)
    product_description_length = Column(Float)
    product_photos_qty = Column(Float)
    product_weight_g = Column(Float)
    product_length_cm = Column(Float)
    product_height_cm = Column(Float)
    product_width_cm = Column(Float)

    updated_at = Column(DateTime, nullable=False)
    is_released = Column(Boolean, default=False, nullable=False)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String, unique=True, nullable=False)
    customer_id = Column(String, nullable=False)
    order_status = Column(String)
    order_purchase_timestamp = Column(DateTime)
    order_approved_at = Column(DateTime)
    order_delivered_carrier_date = Column(DateTime)
    order_delivered_customer_date = Column(DateTime)
    order_estimated_delivery_date = Column(DateTime)

    updated_at = Column(DateTime, nullable=False)
    is_released = Column(Boolean, default=False, nullable=False)


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String, nullable=False)
    order_item_id = Column(Integer, nullable=False)
    product_id = Column(String, nullable=False)
    seller_id = Column(String, nullable=False)
    shipping_limit_date = Column(DateTime)
    price = Column(Float)
    freight_value = Column(Float)

    updated_at = Column(DateTime, nullable=False)
    is_released = Column(Boolean, default=False, nullable=False)


class OrderPayment(Base):
    __tablename__ = "order_payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String, nullable=False)
    payment_sequential = Column(Integer)
    payment_type = Column(String)
    payment_installments = Column(Integer)
    payment_value = Column(Float)

    updated_at = Column(DateTime, nullable=False)
    is_released = Column(Boolean, default=False, nullable=False)


class OrderReview(Base):
    __tablename__ = "order_reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(String, nullable=False)
    order_id = Column(String, nullable=False)
    review_score = Column(Integer)
    review_comment_title = Column(String)
    review_comment_message = Column(String)
    review_creation_date = Column(DateTime)
    review_answer_timestamp = Column(DateTime)

    updated_at = Column(DateTime, nullable=False)
    is_released = Column(Boolean, default=False, nullable=False)


# Composite indexes supporting cursor pagination: every incremental query
# filters/orders by (updated_at, id), so that's exactly what we index.
for _model in (Customer, Seller, Product, Order, OrderItem, OrderPayment, OrderReview):
    Index(f"ix_{_model.__tablename__}_updated_at_id", _model.updated_at, _model.id)
    Index(f"ix_{_model.__tablename__}_is_released", _model.is_released)