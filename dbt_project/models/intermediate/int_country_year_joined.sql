with happiness as (
    select
        case
            when country = 'United States' then 'United States of America'
            when country = 'Congo (Kinshasa)' then 'Democratic Republic of the Congo'
            when country = 'Congo (Brazzaville)' then 'Republic of Congo'
            when country = 'North Cyprus' then 'Northern Cyprus'
            when country = 'Hong Kong S.A.R. of China' then 'Hong Kong'
            when country = 'Hong Kong S.A.R., China' then 'Hong Kong'
            when country = 'Taiwan Province of China' then 'Taiwan'
            when country = 'Palestinian Territories' then 'Palestine'
            else country
        end as country_name,
        year,
        happiness_score,
        happiness_rank,
        social_support,
        life_expectancy,
        freedom,
        corruption,
        generosity
    from {{ ref('stg_happiness') }}
),
climate as (
    select * from {{ ref('stg_climate') }}
),
worldbank as (
    select * from {{ ref('stg_worldbank') }}
)

select
    h.country_name,
    h.year,
    w.iso_code,
    h.happiness_score,
    h.happiness_rank,
    h.social_support,
    h.life_expectancy,
    h.freedom,
    h.corruption,
    h.generosity,
    w.gdp_per_capita,
    w.gini_index,
    w.unemployment_rate,
    w.population,
    c.co2_per_capita,
    c.co2,
    c.temperature_change_from_co2,
    c.ghg_per_capita
from happiness h
left join worldbank w on h.country_name = w.country_name and h.year = w.year
left join climate c on h.country_name = c.country_name and h.year = c.year
