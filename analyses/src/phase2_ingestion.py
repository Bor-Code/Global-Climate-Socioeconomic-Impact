import json
import urllib.request
from datetime import datetime
from pathlib import Path

import duckdb
import requests

from analyses.src import PROJECT_ROOT

RAW_DIR = PROJECT_ROOT / "data" / "raw"
DB_PATH = PROJECT_ROOT / "data" / "climate_wellbeing.duckdb"

WB_INDICATORS = {
    "NY.GDP.PCAP.CD": "worldbank_gdp",
    "SI.POV.GINI": "worldbank_gini",
    "SL.UEM.TOTL.ZS": "worldbank_unemployment",
    "SP.POP.TOTL": "worldbank_population",
}


def download_worldbank():
    out_dir = RAW_DIR / "worldbank"
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d")

    for code, name in WB_INDICATORS.items():
        print(f"Fetching World Bank indicator: {code} ({name})...")
        all_data = []
        page = 1
        while True:
            url = f"https://api.worldbank.org/v2/country/all/indicator/{code}?format=json&per_page=1000&date=2000:2023&page={page}"
            resp = requests.get(url, timeout=20).json()
            if len(resp) < 2 or not resp[1]:
                break
            meta, data = resp[0], resp[1]
            all_data.extend(data)
            if page >= meta["pages"]:
                break
            page += 1

        out_path = out_dir / f"{name}_{timestamp}.json"
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False)
        print(f"  Saved {len(all_data)} records to {out_path.name}")


def download_owid():
    out_dir = RAW_DIR / "owid"
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d")
    out_path = out_dir / f"owid_co2_{timestamp}.csv"

    url = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"
    print(f"Fetching OWID CO2 data from {url}...")
    urllib.request.urlretrieve(url, out_path)
    print(f"  Saved to {out_path.name}")


def load_to_duckdb():
    print(f"\nLoading raw files into DuckDB: {DB_PATH.name}...")
    conn = duckdb.connect(str(DB_PATH))
    conn.execute("CREATE SCHEMA IF NOT EXISTS raw;")

    loaded_at = datetime.now().isoformat()

    # Load World Bank JSONs
    for code, name in WB_INDICATORS.items():
        files = list((RAW_DIR / "worldbank").glob(f"{name}_*.json"))
        if not files:
            continue
        latest = sorted(files)[-1]
        print(f"  Loading {latest.name} into raw.{name}...")
        conn.execute(f"DROP TABLE IF EXISTS raw.{name}")
        conn.execute(
            f"""
            CREATE TABLE raw.{name} AS
            SELECT 
                country.id AS countryiso3code,
                country.value AS country_name,
                date,
                value,
                '{loaded_at}' AS _loaded_at
            FROM read_json_auto('{latest}')
            """
        )

    # Load OWID CO2 CSV
    owid_files = list((RAW_DIR / "owid").glob("owid_co2_*.csv"))
    if owid_files:
        latest = sorted(owid_files)[-1]
        print(f"  Loading {latest.name} into raw.owid_co2...")
        conn.execute("DROP TABLE IF EXISTS raw.owid_co2")
        conn.execute(
            f"""
            CREATE TABLE raw.owid_co2 AS
            SELECT *, '{loaded_at}' AS _loaded_at
            FROM read_csv_auto('{latest}')
            """
        )

    # Check for WHR
    whr_files = list((RAW_DIR / "whr").glob("*.xls*")) + list((RAW_DIR / "whr").glob("*.csv"))
    if whr_files:
        for file_path in whr_files:
            year = file_path.stem  # e.g., '2015'
            table_name = f"world_happiness_{year}"
            print(f"  Loading {file_path.name} into raw.{table_name}...")
            conn.execute(f"DROP TABLE IF EXISTS raw.{table_name}")
            
            if file_path.suffix in [".xls", ".xlsx"]:
                import pandas as pd
                df = pd.read_excel(file_path)
                conn.execute(f"CREATE TABLE raw.{table_name} AS SELECT *, ? AS _loaded_at FROM df", [loaded_at])
            else:
                conn.execute(
                    f"""
                    CREATE TABLE raw.{table_name} AS
                    SELECT *, '{loaded_at}' AS _loaded_at
                    FROM read_csv_auto('{file_path}')
                    """
                )
    else:
        print("  WARNING: No WHR data found in data/raw/whr. Please download it manually.")

    conn.close()
    print("Ingestion complete.")


def main():
    print("=== PHASE 2: Data Ingestion ===")
    download_worldbank()
    download_owid()
    
    print("\nNote: Berkeley Earth will be ingested directly via dbt/DuckDB external tables or a dedicated script in Phase 3 due to complexity.")
    print("Note: WHR dataset must be downloaded manually from Kaggle (e.g., 'World Happiness Report' dataset) and placed in data/raw/whr/ as a CSV file.")
    
    load_to_duckdb()


if __name__ == "__main__":
    main()
