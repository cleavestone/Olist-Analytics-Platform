with source as (
    select * from {{ source('bronze', 'order_reviews') }}
),
renamed as (
    select
        review_id,
        order_id,
        review_score,
        review_comment_title,
        review_comment_message,
        review_creation_date,
        review_answer_timestamp,
        updated_at as _source_updated_at
    from source
)
select * from renamed