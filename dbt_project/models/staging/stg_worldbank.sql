with gdp as (
    select
        countryiso3code as iso_code,
        country_name,
        cast(date as integer) as year,
        value as gdp_per_capita
    from {{ source('raw_worldbank', 'worldbank_gdp') }}
    where value is not null
),
gini as (
    select
        countryiso3code as iso_code,
        cast(date as integer) as year,
        value as gini_index
    from {{ source('raw_worldbank', 'worldbank_gini') }}
),
unemployment as (
    select
        countryiso3code as iso_code,
        cast(date as integer) as year,
        value as unemployment_rate
    from {{ source('raw_worldbank', 'worldbank_unemployment') }}
),
population as (
    select
        countryiso3code as iso_code,
        cast(date as integer) as year,
        value as population
    from {{ source('raw_worldbank', 'worldbank_population') }}
)
select
    g.iso_code,
    g.country_name,
    g.year,
    g.gdp_per_capita,
    gini.gini_index,
    u.unemployment_rate,
    p.population
from gdp g
left join gini on g.iso_code = gini.iso_code and g.year = gini.year
left join unemployment u on g.iso_code = u.iso_code and g.year = u.year
left join population p on g.iso_code = p.iso_code and g.year = p.year
