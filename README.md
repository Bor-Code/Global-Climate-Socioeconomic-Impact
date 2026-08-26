# =============================================================================
# README.md — Placeholder (Faz 10'da akademik formata dönüştürülecek)
# =============================================================================

# 🌍 İklim Değişiminin Küresel Ekonomik ve Sosyal Refah Üzerindeki Etkisi
## Çapraz Etki Analizi (Cross-Impact Analysis)

> **Durum:** 🚧 Aktif Geliştirme — Faz 0 (Kurulum) tamamlandı.

---

## Hızlı Başlangıç

```bash
# 1. Repoyu klonla
git clone <repo-url>
cd climate-economic-wellbeing-analysis

# 2. uv ile ortam kur
uv venv && uv pip install -e ".[dev]"

# 3. Ortam değişkenlerini ayarla
cp .env.example .env

# 4. pre-commit hook'larını kur
pre-commit install

# 5. Tüm servisleri başlat
docker-compose -f docker/docker-compose.yml up --build
```

Detaylı kurulum ve metodoloji için Faz 10 tamamlandığında bu bölüm
akademik formatta güncellenecektir.

---

## Tech Stack

| Katman | Araç |
|--------|------|
| Depolama | DuckDB |
| Dönüştürme | dbt-core + dbt-duckdb |
| İşleme | Polars |
| İstatistik | statsmodels + linearmodels |
| Kümeleme | scikit-learn |
| Orkestrasyon | Dagster |
| Dashboard | Streamlit |
| CI/CD | GitHub Actions |
| Bağımlılık | uv |

## License

MIT — bkz. [LICENSE](LICENSE)
