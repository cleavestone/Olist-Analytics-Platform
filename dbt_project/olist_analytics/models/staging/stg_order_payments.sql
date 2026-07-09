with source as (
    select * from {{ source('bronze', 'order_payments') }}
),
renamed as (
    select
        order_id,
        payment_sequential,
        payment_type,
        payment_installments,
        payment_value,
        updated_at as _source_updated_at
    from source
)
select * from renamed