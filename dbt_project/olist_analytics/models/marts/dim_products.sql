with snapshot as (

    select * from {{ ref('products_snapshot') }}

),

current_only as (

    select
        product_id,
        product_category_name,
        product_name_length,
        product_description_length,
        product_photos_qty,
        product_weight_g,
        product_length_cm,
        product_height_cm,
        product_width_cm,
        dbt_valid_from as valid_from,
        dbt_valid_to as valid_to

    from snapshot
    where dbt_valid_to is null

)

select * from current_only