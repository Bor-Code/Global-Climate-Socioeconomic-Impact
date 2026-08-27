from dagster import asset, Definitions
import subprocess
from analyses.src import PROJECT_ROOT

@asset
def data_ingestion():
    """Phase 2: Runs the ingestion script to pull data into DuckDB."""
    script_path = PROJECT_ROOT / "analyses" / "src" / "phase2_ingestion.py"
    result = subprocess.run(["uv", "run", "python", str(script_path)], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Ingestion failed: {result.stderr}")
    return "Ingestion Complete"

@asset(deps=[data_ingestion])
def dbt_models():
    """Phase 3: Runs dbt to transform the data."""
    dbt_dir = PROJECT_ROOT / "dbt_project"
    result = subprocess.run(["uv", "run", "dbt", "run"], cwd=str(dbt_dir), capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"dbt run failed: {result.stderr}")
    return "dbt Models Built"

@asset(deps=[dbt_models])
def statistical_analysis():
    """Phase 4: Runs statistical analysis (OLS, ANOVA)."""
    script_path = PROJECT_ROOT / "analyses" / "src" / "phase4_statistical_analysis.py"
    result = subprocess.run(["uv", "run", "python", str(script_path)], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Phase 4 failed: {result.stderr}")
    return result.stdout

@asset(deps=[dbt_models])
def machine_learning():
    """Phase 5: Runs KMeans and Random Forest."""
    script_path = PROJECT_ROOT / "analyses" / "src" / "phase5_clustering.py"
    result = subprocess.run(["uv", "run", "python", str(script_path)], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Phase 5 failed: {result.stderr}")
    return result.stdout

defs = Definitions(
    assets=[data_ingestion, dbt_models, statistical_analysis, machine_learning],
)
