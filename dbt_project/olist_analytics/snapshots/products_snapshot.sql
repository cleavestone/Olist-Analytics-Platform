{% snapshot products_snapshot %}

{{
    config(
        target_schema='silver',
        unique_key='product_id',
        strategy='check',
        check_cols=['product_category_name', 'product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm'],
    )
}}

select * from {{ source('bronze', 'products') }}

{% endsnapshot %}