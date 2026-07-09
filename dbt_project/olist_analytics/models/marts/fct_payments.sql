{{
    config(
        materialized='incremental',
        unique_key=['order_id', 'payment_sequential'],
        incremental_strategy='merge'
    )
}}

with stg_order_payments as (

    select * from {{ ref('stg_order_payments') }}

)

select
    order_id,
    payment_sequential,
    payment_type,
    payment_installments,
    payment_value,
    _source_updated_at

from stg_order_payments

{% if is_incremental() %}
    where _source_updated_at > (select max(_source_updated_at) from {{ this }})
{% endif %}