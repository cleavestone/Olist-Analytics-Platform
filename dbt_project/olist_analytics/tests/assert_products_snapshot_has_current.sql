with source_products as (
    select distinct product_id from {{ source('bronze', 'products') }}
),

current_snapshot as (
    select distinct product_id
    from {{ ref('products_snapshot') }}
    where dbt_valid_to is null
)

select source_products.product_id
from source_products
left join current_snapshot on source_products.product_id = current_snapshot.product_id
where current_snapshot.product_id is null
