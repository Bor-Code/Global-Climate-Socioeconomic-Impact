"""
analyses/src/__init__.py
Analiz modüllerinin ortak sabitleri ve yapılandırması.
"""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Proje kök dizini
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
EXTERNAL_DIR = DATA_DIR / "external"

# ---------------------------------------------------------------------------
# Reproducibility — tüm modellerde bu sabit kullanılmalı
# ---------------------------------------------------------------------------
RANDOM_SEED: int = int(os.getenv("RANDOM_SEED", "42"))

# ---------------------------------------------------------------------------
# Analiz penceresi (Faz 1'de kesinleştirilecek, şimdilik varsayılan)
# ---------------------------------------------------------------------------
ANALYSIS_START_YEAR: int = int(os.getenv("ANALYSIS_START_YEAR", "2005"))
ANALYSIS_END_YEAR: int = int(os.getenv("ANALYSIS_END_YEAR", "2022"))

# ---------------------------------------------------------------------------
# Veri kaynağı konfigürasyonları
# ---------------------------------------------------------------------------
WORLDBANK_BASE_URL: str = os.getenv(
    "WORLDBANK_BASE_URL", "https://api.worldbank.org/v2"
)
WORLDBANK_PER_PAGE: int = int(os.getenv("WORLDBANK_PER_PAGE", "1000"))

DUCKDB_PATH: str = os.getenv(
    "DUCKDB_PATH", str(DATA_DIR / "climate_wellbeing.duckdb")
)
