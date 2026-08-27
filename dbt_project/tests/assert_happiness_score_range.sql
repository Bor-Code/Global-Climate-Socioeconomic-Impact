-- Mutluluk skoru teorik olarak 0 ile 10 arasında olmalıdır.
-- 0'dan küçük veya 10'dan büyük skor varsa test hata verir.

select *
from {{ ref('fct_climate_economy') }}
where happiness_score < 0 or happiness_score > 10
