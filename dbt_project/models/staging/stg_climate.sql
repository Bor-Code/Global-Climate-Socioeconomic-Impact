with owid as (
    select
        country as country_name,
        iso_code,
        year,
        co2_per_capita,
        co2,
        temperature_change_from_co2,
        ghg_per_capita
    from {{ source('raw_owid', 'owid_co2') }}
)
select * from owid
