with joined as (
    select * from {{ ref('int_country_year_joined') }}
)
select
    country_name,
    year,
    iso_code,
    happiness_score,
    happiness_rank,
    social_support,
    life_expectancy,
    freedom,
    corruption,
    generosity,
    gdp_per_capita,
    gini_index,
    unemployment_rate,
    population,
    co2_per_capita,
    co2,
    temperature_change_from_co2,
    ghg_per_capita
from joined
