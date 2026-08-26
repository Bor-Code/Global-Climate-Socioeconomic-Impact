"""
tests/test_constants.py
Faz 0 — temel sabit ve yapılandırma doğrulamaları.
Bu testler ham veri veya ağ erişimi gerektirmez; tamamen izole çalışır.
"""

from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# analyses/src modülünü import et
# ---------------------------------------------------------------------------
from analyses.src import (
    ANALYSIS_END_YEAR,
    ANALYSIS_START_YEAR,
    EXTERNAL_DIR,
    PROJECT_ROOT,
    RANDOM_SEED,
    RAW_DIR,
)


class TestProjectConstants:
    """Proje sabitlerinin tutarlılığını doğrula."""

    def test_random_seed_is_integer(self):
        """RANDOM_SEED bir tam sayı olmalı (reproducibility garantisi)."""
        assert isinstance(RANDOM_SEED, int)

    def test_random_seed_default(self):
        """Varsayılan RANDOM_SEED 42 olmalı."""
        assert RANDOM_SEED == 42

    def test_analysis_years_are_valid(self):
        """Analiz penceresi pozitif ve mantıklı yıllar içermeli."""
        assert 1990 <= ANALYSIS_START_YEAR <= 2030
        assert 1990 <= ANALYSIS_END_YEAR <= 2030
        assert ANALYSIS_START_YEAR < ANALYSIS_END_YEAR

    def test_analysis_window_minimum_length(self):
        """Panel analizi için en az 5 yıllık pencere olmalı."""
        assert (ANALYSIS_END_YEAR - ANALYSIS_START_YEAR) >= 5


class TestProjectStructure:
    """Kritik dizin ve dosyaların varlığını doğrula."""

    def test_project_root_exists(self):
        assert PROJECT_ROOT.exists()

    def test_raw_dir_exists(self):
        assert RAW_DIR.exists()

    def test_external_dir_exists(self):
        assert EXTERNAL_DIR.exists()

    def test_country_overrides_csv_exists(self):
        """country_overrides.csv crosswalk dosyası mevcut olmalı."""
        csv_path = EXTERNAL_DIR / "country_overrides.csv"
        assert csv_path.exists(), f"Crosswalk dosyası bulunamadı: {csv_path}"

    def test_dbt_project_yml_exists(self):
        dbt_yml = PROJECT_ROOT / "dbt_project" / "dbt_project.yml"
        assert dbt_yml.exists()

    def test_env_example_exists(self):
        env_example = PROJECT_ROOT / ".env.example"
        assert env_example.exists()

    def test_pre_commit_config_exists(self):
        pre_commit = PROJECT_ROOT / ".pre-commit-config.yaml"
        assert pre_commit.exists()


class TestCountryOverridesFormat:
    """country_overrides.csv dosyasının formatını doğrula."""

    @pytest.fixture
    def overrides_path(self):
        return EXTERNAL_DIR / "country_overrides.csv"

    def test_csv_has_required_columns(self, overrides_path):
        """CSV gerekli kolonlara sahip olmalı."""
        import csv

        with overrides_path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            columns = reader.fieldnames or []

        required = {"source_name", "source_dataset", "iso_alpha3", "canonical_name"}
        assert required.issubset(set(columns)), (
            f"Eksik kolonlar: {required - set(columns)}"
        )

    def test_csv_not_empty(self, overrides_path):
        """CSV en az bir override kaydı içermeli."""
        import csv

        with overrides_path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [r for r in reader if r.get("iso_alpha3")]  # boş iso_alpha3 hariç

        assert len(rows) > 0, "country_overrides.csv boş veya tüm iso_alpha3 alanları boş"
