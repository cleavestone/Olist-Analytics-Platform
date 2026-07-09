with date_spine as (

    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="cast('2015-01-01' as date)",
        end_date="cast('2028-01-01' as date)"
    ) }}

),

renamed as (

    select
        cast(date_day as date) as date_day,
        extract(year from date_day) as year,
        extract(month from date_day) as month,
        extract(day from date_day) as day_of_month,
        extract(dow from date_day) as day_of_week,
        to_char(date_day, 'Day') as day_name,
        to_char(date_day, 'Month') as month_name,
        extract(quarter from date_day) as quarter,
        case when extract(dow from date_day) in (0, 6) then true else false end as is_weekend

    from date_spine

)

select * from renamed