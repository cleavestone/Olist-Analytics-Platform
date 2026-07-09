with source as (
    select * from {{ source('bronze', 'order_items') }}
),
renamed as (
    select
        order_id,
        order_item_id,
        product_id,
        seller_id,
        shipping_limit_date,
        price,
        freight_value,
        updated_at as _source_updated_at
    from source
)
select * from renamed