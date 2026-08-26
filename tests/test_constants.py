import pytest
from analyses.src import (
    ANALYSIS_END_YEAR,
    ANALYSIS_START_YEAR,
    EXTERNAL_DIR,
    PROJECT_ROOT,
    RANDOM_SEED,
    RAW_DIR,
)


class TestProjectConstants:
    def test_random_seed_is_integer(self):
        assert isinstance(RANDOM_SEED, int)

    def test_random_seed_default(self):
        assert RANDOM_SEED == 42

    def test_analysis_years_are_valid(self):
        assert 1990 <= ANALYSIS_START_YEAR <= 2030
        assert 1990 <= ANALYSIS_END_YEAR <= 2030
        assert ANALYSIS_START_YEAR < ANALYSIS_END_YEAR

    def test_analysis_window_minimum_length(self):
        assert (ANALYSIS_END_YEAR - ANALYSIS_START_YEAR) >= 5


class TestProjectStructure:
    def test_project_root_exists(self):
        assert PROJECT_ROOT.exists()

    def test_raw_dir_exists(self):
        assert RAW_DIR.exists()

    def test_external_dir_exists(self):
        assert EXTERNAL_DIR.exists()

    def test_country_overrides_csv_exists(self):
        csv_path = EXTERNAL_DIR / "country_overrides.csv"
        assert csv_path.exists(), f"Crosswalk file not found: {csv_path}"

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
    @pytest.fixture
    def overrides_path(self):
        return EXTERNAL_DIR / "country_overrides.csv"

    def test_csv_has_required_columns(self, overrides_path):
        import csv

        with overrides_path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            columns = reader.fieldnames or []

        required = {"source_name", "source_dataset", "iso_alpha3", "canonical_name"}
        assert required.issubset(set(columns)), f"Missing columns: {required - set(columns)}"

    def test_csv_not_empty(self, overrides_path):
        import csv

        with overrides_path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [r for r in reader if r.get("iso_alpha3")]

        assert len(rows) > 0, "country_overrides.csv is empty or all iso_alpha3 fields are blank"
