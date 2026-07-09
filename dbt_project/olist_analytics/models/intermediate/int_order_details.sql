with orders as (
    select * from {{ ref('stg_orders') }}
),

customers as (
    select * from {{ ref('stg_customers') }}
),

order_items as (
    select * from {{ ref('stg_order_items') }}
),

products as (
    select * from {{ ref('dim_products') }}
),

sellers as (
    select * from {{ ref('dim_sellers') }}
)

select
    orders.order_id,
    orders.customer_id,
    customers.customer_unique_id,
    customers.customer_city,
    customers.customer_state,
    orders.order_status,
    orders.order_purchase_timestamp,
    orders.order_approved_at,
    orders.order_delivered_carrier_date,
    orders.order_delivered_customer_date,
    orders.order_estimated_delivery_date,
    order_items.order_item_id,
    order_items.product_id,
    products.product_category_name,
    order_items.seller_id,
    sellers.seller_city as seller_city,
    sellers.seller_state as seller_state,
    order_items.price,
    order_items.freight_value,
    order_items.shipping_limit_date
from orders
left join customers on orders.customer_id = customers.customer_id
left join order_items on orders.order_id = order_items.order_id
left join products on order_items.product_id = products.product_id
left join sellers on order_items.seller_id = sellers.seller_id