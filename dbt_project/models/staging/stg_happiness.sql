with data_2015 as (
    select
        "Country" as country,
        2015 as year,
        "Happiness Rank" as happiness_rank,
        "Happiness Score" as happiness_score,
        "Economy (GDP per Capita)" as gdp_per_capita,
        "Family" as social_support,
        "Health (Life Expectancy)" as life_expectancy,
        "Freedom" as freedom,
        "Trust (Government Corruption)" as corruption,
        "Generosity" as generosity
    from {{ source('raw_happiness', 'world_happiness_2015') }}
),
data_2016 as (
    select
        "Country" as country,
        2016 as year,
        "Happiness Rank" as happiness_rank,
        "Happiness Score" as happiness_score,
        "Economy (GDP per Capita)" as gdp_per_capita,
        "Family" as social_support,
        "Health (Life Expectancy)" as life_expectancy,
        "Freedom" as freedom,
        "Trust (Government Corruption)" as corruption,
        "Generosity" as generosity
    from {{ source('raw_happiness', 'world_happiness_2016') }}
),
data_2017 as (
    select
        "Country" as country,
        2017 as year,
        "Happiness.Rank" as happiness_rank,
        "Happiness.Score" as happiness_score,
        "Economy..GDP.per.Capita." as gdp_per_capita,
        "Family" as social_support,
        "Health..Life.Expectancy." as life_expectancy,
        "Freedom" as freedom,
        "Trust..Government.Corruption." as corruption,
        "Generosity" as generosity
    from {{ source('raw_happiness', 'world_happiness_2017') }}
),
data_2018 as (
    select
        "Country or region" as country,
        2018 as year,
        "Overall rank" as happiness_rank,
        "Score" as happiness_score,
        "GDP per capita" as gdp_per_capita,
        "Social support" as social_support,
        "Healthy life expectancy" as life_expectancy,
        "Freedom to make life choices" as freedom,
        "Perceptions of corruption" as corruption,
        "Generosity" as generosity
    from {{ source('raw_happiness', 'world_happiness_2018') }}
),
data_2019 as (
    select
        "Country or region" as country,
        2019 as year,
        "Overall rank" as happiness_rank,
        "Score" as happiness_score,
        "GDP per capita" as gdp_per_capita,
        "Social support" as social_support,
        "Healthy life expectancy" as life_expectancy,
        "Freedom to make life choices" as freedom,
        "Perceptions of corruption" as corruption,
        "Generosity" as generosity
    from {{ source('raw_happiness', 'world_happiness_2019') }}
),
unioned as (
    select * from data_2015
    union all
    select * from data_2016
    union all
    select * from data_2017
    union all
    select * from data_2018
    union all
    select * from data_2019
)
select 
    country,
    year,
    try_cast(happiness_rank as double) as happiness_rank,
    try_cast(happiness_score as double) as happiness_score,
    try_cast(gdp_per_capita as double) as gdp_per_capita,
    try_cast(social_support as double) as social_support,
    try_cast(life_expectancy as double) as life_expectancy,
    try_cast(freedom as double) as freedom,
    try_cast(corruption as double) as corruption,
    try_cast(generosity as double) as generosity
from unioned
