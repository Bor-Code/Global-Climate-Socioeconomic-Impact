-- CO2 emisyon değerleri negatif olamaz.
-- Eğer co2_per_capita < 0 olan bir kayıt varsa test hata verir.

select *
from {{ ref('fct_climate_economy') }}
where co2_per_capita < 0
