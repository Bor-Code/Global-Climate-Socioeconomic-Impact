import duckdb
import polars as pl
import statsmodels.api as sm
from analyses.src import PROJECT_ROOT
from scipy.stats import f_oneway, ttest_ind

DB_PATH = PROJECT_ROOT / "data" / "climate_wellbeing.duckdb"


def load_data():
    conn = duckdb.connect(str(DB_PATH))
    df = conn.execute("SELECT * FROM main_marts.fct_climate_economy").pl()
    conn.close()
    return df


def run_anova_test(df: pl.DataFrame):
    print("\n--- ANOVA: Happiness Scores Across Years ---")
    years = df["year"].unique().to_list()
    happiness_by_year = [
        df.filter(pl.col("year") == year)["happiness_score"].to_list() for year in years
    ]

    # Filter out empty lists
    happiness_by_year = [x for x in happiness_by_year if len(x) > 0]

    if len(happiness_by_year) > 1:
        f_stat, p_value = f_oneway(*happiness_by_year)
        print(f"F-statistic: {f_stat:.4f}")
        print(f"p-value: {p_value:.4f}")
        print(f"Statistically significant difference: {p_value < 0.05}")
    else:
        print("Not enough year groups for ANOVA.")


def run_t_tests(df: pl.DataFrame):
    print("\n--- T-Test: Pre-COVID vs COVID Happiness ---")
    pre_covid = df.filter(pl.col("year") < 2020)["happiness_score"].drop_nulls().to_numpy()
    during_covid = (
        df.filter((pl.col("year") >= 2020) & (pl.col("year") <= 2022))["happiness_score"]
        .drop_nulls()
        .to_numpy()
    )

    if len(pre_covid) > 0 and len(during_covid) > 0:
        t_stat, p_value = ttest_ind(pre_covid, during_covid, equal_var=False)
        print(f"t-statistic: {t_stat:.4f}")
        print(f"p-value: {p_value:.4f}")
        print(f"Statistically significant difference: {p_value < 0.05}")
        print(f"Pre-COVID mean: {pre_covid.mean():.4f}")
        print(f"During COVID mean: {during_covid.mean():.4f}")
    else:
        print("Insufficient data for Pre-COVID vs COVID T-Test.")


def run_ols_regression(df: pl.DataFrame):
    print("\n--- OLS Regression (Latest Year) ---")
    # Using the latest available year
    latest_year = df["year"].max()
    latest_data = df.filter(pl.col("year") == latest_year).drop_nulls(
        subset=[
            "happiness_score",
            "gdp_per_capita",
            "social_support",
            "life_expectancy",
            "freedom",
            "corruption",
            "generosity",
        ]
    )

    if len(latest_data) == 0:
        print(f"No complete data available for OLS in year {latest_year}")
        return

    X = latest_data.select(
        [
            "gdp_per_capita",
            "social_support",
            "life_expectancy",
            "freedom",
            "corruption",
            "generosity",
        ]
    ).to_pandas()
    y = latest_data["happiness_score"].to_pandas()

    X_with_const = sm.add_constant(X)
    model = sm.OLS(y, X_with_const).fit()
    print(model.summary())


def main():
    print("=== PHASE 4: Statistical Analysis ===")
    try:
        df = load_data()
        print(f"Loaded {len(df)} records from main_marts.fct_climate_economy.")
    except Exception as e:
        print(f"Failed to load data: {e}")
        print("Make sure Phase 3 (dbt run) has successfully completed.")
        return

    if len(df) == 0:
        print("Dataset is empty.")
        return

    run_anova_test(df)
    run_t_tests(df)
    run_ols_regression(df)


if __name__ == "__main__":
    main()
