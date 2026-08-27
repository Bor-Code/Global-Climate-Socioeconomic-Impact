import subprocess
import os

from analyses.src import PROJECT_ROOT
from dagster import Definitions, asset


@asset
def data_ingestion():
    """Phase 2: Runs the ingestion script to pull latest data into DuckDB."""
    script_path = PROJECT_ROOT / "analyses" / "src" / "phase2_ingestion.py"
    result = subprocess.run(
        ["uv", "run", "python", str(script_path)], capture_output=True, text=True
    )
    if result.returncode != 0:
        raise Exception(f"Ingestion failed: {result.stderr}")
    return "Ingestion Complete"


@asset(deps=[data_ingestion])
def dbt_models():
    """Phase 3: Runs dbt to transform the data."""
    dbt_dir = PROJECT_ROOT / "dbt_project"
    result = subprocess.run(
        ["uv", "run", "dbt", "build"], cwd=str(dbt_dir), capture_output=True, text=True
    )
    if result.returncode != 0:
        raise Exception(f"dbt run failed: {result.stderr}")
    return "dbt Models Built"


@asset(deps=[dbt_models])
def generate_notebook():
    """Generates the Jupyter Notebook structure."""
    script_path = PROJECT_ROOT / "generate_notebook.py"
    result = subprocess.run(
        ["uv", "run", "python", str(script_path)], capture_output=True, text=True
    )
    if result.returncode != 0:
        raise Exception(f"Notebook generation failed: {result.stderr}")
    return "Notebook Generated"


@asset(deps=[generate_notebook])
def execute_notebook():
    """Executes the Jupyter Notebook inplace to populate outputs."""
    nb_path = PROJECT_ROOT / "analyses" / "Climate_Economic_Wellbeing_Analysis.ipynb"
    result = subprocess.run(
        ["uv", "run", "jupyter", "nbconvert", "--to", "notebook", "--inplace", "--execute", str(nb_path)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise Exception(f"Notebook execution failed: {result.stderr}")
    return "Notebook Executed"


@asset(deps=[execute_notebook])
def export_html():
    """Exports the executed Notebook to HTML."""
    nb_path = PROJECT_ROOT / "analyses" / "Climate_Economic_Wellbeing_Analysis.ipynb"
    result = subprocess.run(
        ["uv", "run", "jupyter", "nbconvert", "--to", "html", str(nb_path)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise Exception(f"HTML export failed: {result.stderr}")
    return "HTML Exported"


@asset(deps=[execute_notebook])
def generate_images():
    """Generates static PNG images for the README from the processed data."""
    script_path = PROJECT_ROOT / "generate_images.py"
    result = subprocess.run(
        ["uv", "run", "python", str(script_path)], capture_output=True, text=True
    )
    if result.returncode != 0:
        raise Exception(f"Image generation failed: {result.stderr}")
    return "Images Generated"


defs = Definitions(
    assets=[
        data_ingestion,
        dbt_models,
        generate_notebook,
        execute_notebook,
        export_html,
        generate_images
    ],
)
