{{
    config(
        materialized='incremental',
        unique_key=['order_id', 'order_item_id'],
        incremental_strategy='merge'
    )
}}

with stg_order_items as (

    select * from {{ ref('stg_order_items') }}

)

select
    order_id,
    order_item_id,
    product_id,
    seller_id,
    shipping_limit_date,
    price,
    freight_value,
    price + freight_value as total_item_value,
    _source_updated_at

from stg_order_items

{% if is_incremental() %}
    where _source_updated_at > (select max(_source_updated_at) from {{ this }})
{% endif %}