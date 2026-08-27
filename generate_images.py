import duckdb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import polars as pl
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# Set global seaborn style for beautiful plots
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({"figure.dpi": 150})

DB_PATH = "data/climate_wellbeing.duckdb"
conn = duckdb.connect(str(DB_PATH), read_only=True)
df = conn.execute("SELECT * FROM main_marts.fct_climate_economy").pl()

latest_year = df["year"].max()
df_latest = df.filter(pl.col("year") == latest_year).to_pandas()

# 1. Map Alternative: Top 10 & Bottom 10 Happiest Countries
plt.figure(figsize=(12, 6))
top10 = df_latest.nlargest(10, "happiness_score")
bot10 = df_latest.nsmallest(10, "happiness_score")
extreme_countries = pd.concat([top10, bot10])

sns.barplot(
    data=extreme_countries,
    y="country_name",
    x="happiness_score",
    hue="happiness_score",
    palette="RdYlGn",
    legend=False,
)
plt.title(f"Top & Bottom 10 Countries by Happiness Score ({latest_year})", fontsize=14, pad=15)
plt.xlabel("Happiness Score")
plt.ylabel("")
plt.tight_layout()
plt.savefig("docs/map.png")
plt.close()

# 2. Scatter: GDP vs Happiness
plt.figure(figsize=(10, 6))
sns.scatterplot(
    data=df_latest,
    x="gdp_per_capita",
    y="happiness_score",
    hue="happiness_score",
    palette="viridis",
    size="population",
    sizes=(20, 400),
    alpha=0.7,
    legend=False,
)
plt.xscale("log")
plt.title(f"Wealth (GDP per Capita) vs Wellbeing ({latest_year})", fontsize=14, pad=15)
plt.xlabel("GDP per Capita (Log Scale)")
plt.ylabel("Happiness Score")
plt.tight_layout()
plt.savefig("docs/scatter.png")
plt.close()

# 3. Random Forest Feature Importance
df_reg = df_latest.dropna(
    subset=[
        "happiness_score",
        "gdp_per_capita",
        "social_support",
        "life_expectancy",
        "freedom",
        "corruption",
    ]
)
X = df_reg[["gdp_per_capita", "social_support", "life_expectancy", "freedom", "corruption"]]
y = df_reg["happiness_score"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

plt.figure(figsize=(10, 6))
importances = rf_model.feature_importances_
sns.barplot(x=X.columns, y=importances, hue=X.columns, palette="crest", legend=False)
plt.title("Random Forest Feature Importance for Predicting Happiness", fontsize=14, pad=15)
plt.xlabel("Features")
plt.ylabel("Importance")
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig("docs/rf_importance.png")
plt.close()

# 4. Time Series Forecast
global_trends = (
    df.to_pandas().groupby("year")["happiness_score"].mean().reset_index().sort_values("year")
)
ts_data = global_trends["happiness_score"].values
years = global_trends["year"].values

model_ts = ExponentialSmoothing(
    ts_data, trend="add", seasonal=None, initialization_method="estimated"
)
fit_model = model_ts.fit()
forecast = fit_model.forecast(6)
forecast_years = np.arange(2025, 2031)

plt.figure(figsize=(10, 6))
plt.plot(
    years,
    ts_data,
    marker="o",
    linestyle="-",
    color="#1f77b4",
    linewidth=2,
    label="Historical Global Happiness",
)
plt.plot(
    forecast_years,
    forecast,
    marker="s",
    linestyle="--",
    color="#d62728",
    linewidth=2,
    label="Forecast (2025-2030)",
)
plt.title("Global Happiness Score Forecast (2025-2030)", fontsize=14, pad=15)
plt.xlabel("Year")
plt.ylabel("Average Happiness Score")
plt.legend()
plt.grid(True, linestyle=":", alpha=0.6)
plt.tight_layout()
plt.savefig("docs/forecast.png")
plt.close()

# 5. CO2 Impact Boxplot
df_climate = df_latest.dropna(subset=["co2_per_capita", "happiness_score"])
median_co2 = df_climate["co2_per_capita"].median()
df_climate["emission_group"] = np.where(
    df_climate["co2_per_capita"] > median_co2, "High Emitters", "Low Emitters"
)

plt.figure(figsize=(8, 6))
sns.boxplot(
    data=df_climate,
    x="emission_group",
    y="happiness_score",
    hue="emission_group",
    palette={"High Emitters": "crimson", "Low Emitters": "seagreen"},
)
plt.title("Wellbeing Variance: High vs Low CO2 Emitters", fontsize=14, pad=15)
plt.xlabel("Emission Group")
plt.ylabel("Happiness Score")
plt.tight_layout()
plt.savefig("docs/co2_impact.png")
plt.close()
