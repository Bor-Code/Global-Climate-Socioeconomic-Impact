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
        latest = sorted(whr_files)[-1]
        print(f"  Loading {latest.name} into raw.world_happiness...")
        conn.execute("DROP TABLE IF EXISTS raw.world_happiness")
        
        # Determine if CSV or Excel. Since pandas is needed for excel, we can use DuckDB's spatial extension for excel
        # or load via pandas. For now, try loading via pandas.
        if latest.suffix in [".xls", ".xlsx"]:
            import pandas as pd
            df = pd.read_excel(latest)
            conn.execute("CREATE TABLE raw.world_happiness AS SELECT *, ? AS _loaded_at FROM df", [loaded_at])
        else:
            conn.execute(
                f"""
                CREATE TABLE raw.world_happiness AS
                SELECT *, '{loaded_at}' AS _loaded_at
                FROM read_csv_auto('{latest}')
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
    print("Note: WHR dataset must be downloaded manually due to strict anti-bot protection on the official S3 bucket.")
    
    load_to_duckdb()


if __name__ == "__main__":
    main()
