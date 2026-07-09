with source as (
    select * from {{ source('bronze', 'customers') }}
),
renamed as (
    select
        customer_id,
        customer_unique_id,
        customer_zip_code_prefix,
        customer_city,
        customer_state,
        updated_at as _source_updated_at
    from source
)
select * from renamed