{{
    config(
        materialized='incremental',
        unique_key='order_id',
        incremental_strategy='merge'
    )
}}

with stg_orders as (

    select * from {{ ref('stg_orders') }}

),

order_items_agg as (

    select
        order_id,
        count(*) as item_count,
        sum(price) as total_items_value,
        sum(freight_value) as total_freight_value

    from {{ ref('stg_order_items') }}
    group by order_id

),

payments_agg as (

    select
        order_id,
        count(*) as payment_count,
        sum(payment_value) as total_payment_value

    from {{ ref('stg_order_payments') }}
    group by order_id

),

reviews_agg as (

    select
        order_id,
        count(*) as review_count,
        avg(review_score) as avg_review_score

    from {{ ref('stg_order_reviews') }}
    group by order_id

),

final as (

    select
        o.order_id,
        o.customer_id,
        o.order_status,
        o.order_purchase_timestamp,
        cast(o.order_purchase_timestamp as date) as order_purchase_date,
        o.order_approved_at,
        o.order_delivered_carrier_date,
        o.order_delivered_customer_date,
        o.order_estimated_delivery_date,
        extract(day from (o.order_delivered_customer_date - o.order_purchase_timestamp)) as delivery_days,

        coalesce(oi.item_count, 0) as item_count,
        coalesce(oi.total_items_value, 0) as total_items_value,
        coalesce(oi.total_freight_value, 0) as total_freight_value,
        coalesce(oi.total_items_value, 0) + coalesce(oi.total_freight_value, 0) as total_order_value,

        coalesce(p.payment_count, 0) as payment_count,
        coalesce(p.total_payment_value, 0) as total_payment_value,

        coalesce(r.review_count, 0) as review_count,
        r.avg_review_score,

        o._source_updated_at

    from stg_orders o
    left join order_items_agg oi on o.order_id = oi.order_id
    left join payments_agg p on o.order_id = p.order_id
    left join reviews_agg r on o.order_id = r.order_id

)

select * from final

{% if is_incremental() %}
    where _source_updated_at > (select max(_source_updated_at) from {{ this }})
{% endif %}