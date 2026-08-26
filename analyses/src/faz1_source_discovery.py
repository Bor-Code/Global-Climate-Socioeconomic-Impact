import json
import sys
from datetime import datetime
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "docs"

WB_BASE = "https://api.worldbank.org/v2"
TIMEOUT = 20


def wb_get(url):
    resp = requests.get(url, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def probe_wb_indicator(code, label):
    url = f"{WB_BASE}/country/all/indicator/{code}?format=json&per_page=1&date=2000:2023"
    try:
        data = wb_get(url)
        meta = data[0]
        sample = data[1][0] if data[1] else {}
        return {
            "label": label,
            "total_records_2000_2023": meta.get("total"),
            "sample_keys": list(sample.keys()) if sample else [],
            "sample_value": sample.get("value"),
            "sample_country": sample.get("country", {}).get("value"),
            "sample_date": sample.get("date"),
            "status": "ok",
        }
    except Exception as e:
        return {"label": label, "status": "error", "error": str(e)}


def probe_wb_country_list():
    url = f"{WB_BASE}/country?format=json&per_page=1&incomelevel=all"
    try:
        data = wb_get(url)
        meta = data[0]
        sample = data[1][0] if data[1] else {}
        return {
            "total_entities": meta.get("total"),
            "sample_keys": list(sample.keys()) if sample else [],
            "status": "ok",
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def probe_whr_kaggle():
    url = "https://raw.githubusercontent.com/rashida048/Datasets/master/World_Happiness_Report_2021.csv"
    try:
        resp = requests.get(url, timeout=TIMEOUT)
        resp.raise_for_status()
        lines = resp.text.strip().split("\n")
        header = lines[0].replace('"', "").split(",")
        return {
            "columns": header,
            "row_count": len(lines) - 1,
            "status": "ok",
            "note": "2021 WHR from public Kaggle mirror",
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def probe_whr_official():
    urls_to_try = [
        "https://happiness-report.s3.amazonaws.com/2023/DataForFigure2.1WHR2023.xls",
        "https://worldhappiness.report/ed/2023/",
    ]
    results = []
    for url in urls_to_try:
        try:
            resp = requests.head(url, timeout=10)
            results.append({"url": url, "status_code": resp.status_code, "accessible": resp.status_code < 400})
        except Exception as e:
            results.append({"url": url, "accessible": False, "error": str(e)})
    return results


def probe_berkeley_earth():
    candidates = [
        "https://berkeley-earth-temperature.s3.amazonaws.com/Global/Land_and_Ocean_summary.txt",
        "https://berkeley-earth-temperature.s3.amazonaws.com/auto-v5/Global/Complete_TAVG_complete.txt",
    ]
    for url in candidates:
        try:
            resp = requests.head(url, timeout=10)
            if resp.status_code < 400:
                return {"url": url, "accessible": True, "status_code": resp.status_code}
        except Exception:
            pass
    return {
        "accessible": False,
        "fallback": "Use World Bank EN.CLC.MDAT.ZS (mean annual temperature)",
        "note": "Berkeley Earth country-level files require direct S3 path construction",
    }


def probe_owid_co2():
    url = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"
    try:
        resp = requests.get(url, timeout=TIMEOUT, stream=True)
        resp.raise_for_status()
        header_line = next(resp.iter_lines()).decode("utf-8")
        columns = header_line.split(",")
        return {
            "source": "Our World in Data CO2 dataset",
            "url": url,
            "columns": columns,
            "column_count": len(columns),
            "status": "ok",
            "note": "country + year + co2 + co2_per_capita + temperature_change_from_co2",
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def determine_analysis_window(wb_results, whr_result, owid_result):
    issues = []
    start = 2005
    end = 2022

    if whr_result.get("status") != "ok":
        issues.append("WHR access issue - defaulting to 2005 start based on known availability")

    if owid_result.get("status") != "ok":
        issues.append("OWID CO2 access issue - fallback to WB EN.ATM.CO2E.PC")

    gini = wb_results.get("SI.POV.GINI", {})
    if gini.get("total_records_2000_2023", 0) and gini["total_records_2000_2023"] < 500:
        issues.append("Gini data sparse — will require imputation strategy in Phase 4")

    return {
        "recommended_start": start,
        "recommended_end": end,
        "window_years": end - start + 1,
        "rationale": "WHR starts 2005; WB Gini available from ~2000 but sparse before 2005; CO2 available from 1990",
        "issues": issues,
    }


def main():
    print("=== PHASE 1: Data Source Schema Validation ===\n")

    wb_indicators = {
        "NY.GDP.PCAP.CD": "GDP per capita (current USD)",
        "SI.POV.GINI": "Gini index",
        "SL.UEM.TOTL.ZS": "Unemployment rate (%)",
        "EN.ATM.CO2E.PC": "CO2 per capita (metric tons) - WB",
        "EN.CLC.MDAT.ZS": "Mean dryland area - climate proxy (WB)",
        "SP.POP.TOTL": "Total population",
    }

    print("[1/6] World Bank indicators...")
    wb_results = {}
    for code, label in wb_indicators.items():
        result = probe_wb_indicator(code, label)
        wb_results[code] = result
        status = result.get("total_records_2000_2023", "err")
        print(f"  {code}: {status} records | sample_keys={result.get('sample_keys', [])[:5]}")

    print("\n[2/6] World Bank country list...")
    wb_countries = probe_wb_country_list()
    print(f"  Total WB entities: {wb_countries.get('total_entities')} | keys={wb_countries.get('sample_keys', [])[:6]}")

    print("\n[3/6] World Happiness Report (Kaggle mirror)...")
    whr_result = probe_whr_kaggle()
    print(f"  Status: {whr_result.get('status')} | columns={whr_result.get('columns', [])[:8]}")

    print("\n[4/6] WHR official URL accessibility...")
    whr_official = probe_whr_official()
    for r in whr_official:
        print(f"  {r.get('url', '')[:60]}: accessible={r.get('accessible')}")

    print("\n[5/6] Berkeley Earth S3...")
    be_result = probe_berkeley_earth()
    print(f"  Accessible: {be_result.get('accessible')} | fallback: {be_result.get('fallback', '-')}")

    print("\n[6/6] Our World in Data CO2 (primary CO2 source)...")
    owid_result = probe_owid_co2()
    print(f"  Status: {owid_result.get('status')} | columns: {owid_result.get('column_count')} | sample: {owid_result.get('columns', [])[:8]}")

    print("\n[7/7] Determining analysis window...")
    window = determine_analysis_window(wb_results, whr_result, owid_result)
    print(f"  Window: {window['recommended_start']}–{window['recommended_end']} ({window['window_years']} years)")
    for issue in window["issues"]:
        print(f"  WARNING: {issue}")

    report = {
        "generated_at": datetime.now().isoformat(),
        "worldbank_indicators": wb_results,
        "worldbank_country_list": wb_countries,
        "whr_kaggle_mirror": whr_result,
        "whr_official_accessibility": whr_official,
        "berkeley_earth": be_result,
        "owid_co2": owid_result,
        "analysis_window": window,
    }

    out_path = OUTPUT_DIR / "faz1_kaynak_dogrulama.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\nReport saved: {out_path}")
    return report


if __name__ == "__main__":
    main()
