select fct.order_id
from {{ ref('fct_orders') }} fct
left join {{ ref('stg_order_items') }} items on fct.order_id = items.order_id
where items.order_id is null