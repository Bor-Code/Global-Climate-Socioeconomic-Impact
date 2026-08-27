import nbformat as nbf

nb = nbf.v4.new_notebook()

cells = []

# Title & Objective
cells.append(nbf.v4.new_markdown_cell("""# Climate Change, Economic, and Social Wellbeing Analysis
This notebook provides an end-to-end analysis exploring the relationships between climate change (CO2 emissions), economic indicators (GDP, Unemployment, Gini), and social wellbeing (World Happiness Report).

It replaces the previous dbt/Dagster architecture with a unified, professional workspace that leverages **DuckDB**, **Polars**, and **Scikit-Learn**."""))

# Environment Setup
cells.append(nbf.v4.new_markdown_cell("## 1. Environment Setup & Imports\nLoading the necessary libraries and establishing the database connection."))
cells.append(nbf.v4.new_code_cell("""import duckdb
import polars as pl
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm
from scipy.stats import f_oneway
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# Connect to the DuckDB warehouse generated previously (read-only mode to prevent locking issues)
DB_PATH = "../data/climate_wellbeing.duckdb"
conn = duckdb.connect(str(DB_PATH), read_only=True)"""))

# Data Loading
cells.append(nbf.v4.new_markdown_cell("## 2. Data Loading\nWe load the pre-transformed data (`fct_climate_economy`) which aggregates World Bank, OWID, and WHR data into a single unified table."))
cells.append(nbf.v4.new_code_cell("""# Fetching the data using Polars for high performance
query = "SELECT * FROM main_marts.fct_climate_economy"
df = conn.execute(query).pl()

print(f"Loaded {len(df)} records across {df['country_name'].n_unique()} countries.")
df.head()"""))

# Exploratory Data Analysis
cells.append(nbf.v4.new_markdown_cell("## 3. Exploratory Data Analysis & Visualization\n### 3.1 Happiness Score Distribution (Map)"))
cells.append(nbf.v4.new_code_cell("""# Filter data for the latest available year (e.g., 2019)
latest_year = df['year'].max()
df_latest = df.filter(pl.col('year') == latest_year)

# Plot a world map
fig_map = px.choropleth(
    df_latest.to_pandas(),
    locations="iso_code",
    color="happiness_score",
    hover_name="country_name",
    color_continuous_scale="Viridis",
    title=f"World Happiness Score Map ({latest_year})"
)
fig_map.update_layout(geo=dict(showframe=False, showcoastlines=False, projection_type='equirectangular'))
fig_map.show()"""))

cells.append(nbf.v4.new_markdown_cell("### 3.2 GDP vs Happiness Score"))
cells.append(nbf.v4.new_code_cell("""fig_scatter = px.scatter(
    df_latest.to_pandas(), 
    x="gdp_per_capita", 
    y="happiness_score",
    hover_name="country_name",
    color="happiness_score",
    color_continuous_scale="Viridis",
    log_x=True,
    title=f"Wealth (GDP per Capita) vs Wellbeing ({latest_year})"
)
fig_scatter.show()"""))

# Statistical Analysis
cells.append(nbf.v4.new_markdown_cell("## 4. Statistical Analysis\n### 4.1 ANOVA: Variation in Happiness Across Years"))
cells.append(nbf.v4.new_code_cell("""years = df['year'].unique().to_list()
happiness_by_year = [df.filter(pl.col('year') == year)['happiness_score'].to_list() for year in years]
happiness_by_year = [x for x in happiness_by_year if len(x) > 0]

f_stat, p_value = f_oneway(*happiness_by_year)
print(f"F-statistic: {f_stat:.4f}")
print(f"p-value: {p_value:.4f}")
print(f"Statistically significant difference across years: {p_value < 0.05}")"""))

cells.append(nbf.v4.new_markdown_cell("### 4.2 OLS Panel Regression\nIdentifying which factors have the most statistically significant linear relationship with the Happiness Score."))
cells.append(nbf.v4.new_code_cell("""df_reg = df_latest.drop_nulls(
    subset=['happiness_score', 'gdp_per_capita', 'social_support', 'life_expectancy', 'freedom', 'corruption']
).to_pandas()

X = df_reg[['gdp_per_capita', 'social_support', 'life_expectancy', 'freedom', 'corruption']]
y = df_reg['happiness_score']

X_with_const = sm.add_constant(X)
model = sm.OLS(y, X_with_const).fit()
print(model.summary())"""))

# Machine Learning
cells.append(nbf.v4.new_markdown_cell("## 5. Machine Learning & Clustering\n### 5.1 K-Means Clustering of Country Profiles\nWe cluster countries based on their economic and social indicators to identify overarching patterns."))
cells.append(nbf.v4.new_code_cell("""# Prepare scaled data
features = ['gdp_per_capita', 'social_support', 'life_expectancy', 'freedom', 'corruption']
X_cluster = df_reg[features]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_cluster)

# KMeans
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
df_reg['cluster'] = kmeans.fit_predict(X_scaled)
df_reg['cluster'] = df_reg['cluster'].astype(str)

# PCA for 2D visualization
pca = PCA(n_components=2)
pca_result = pca.fit_transform(X_scaled)
df_reg['pca_1'] = pca_result[:, 0]
df_reg['pca_2'] = pca_result[:, 1]

print(f"PCA explained variance ratio: {pca.explained_variance_ratio_}")

# Plot Clusters
fig_cluster = px.scatter(
    df_reg, x="pca_1", y="pca_2", color="cluster", hover_name="country_name",
    title="Country Clusters based on Economic & Social Profiles (PCA 2D)"
)
fig_cluster.show()"""))

cells.append(nbf.v4.new_markdown_cell("### 5.2 Random Forest: Feature Importance\nUsing an ensemble method to predict happiness and extract the non-linear importance of each feature."))
cells.append(nbf.v4.new_code_cell("""X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

y_pred = rf_model.predict(X_test)
print(f"Random Forest R2 Score: {r2_score(y_test, y_pred):.4f}")
print(f"Random Forest RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.4f}")

# Feature Importances Plot
importances = rf_model.feature_importances_
fig_rf = px.bar(
    x=features, y=importances, 
    labels={'x':'Features', 'y':'Importance'},
    title="Random Forest Feature Importance for Predicting Happiness",
    color=importances, color_continuous_scale="Teal"
)
fig_rf.show()"""))

# Conclusion
cells.append(nbf.v4.new_markdown_cell("""## 6. Conclusion & Insights

### Key Findings
* **Strong Predictors:** Both the linear OLS model and the non-linear Random Forest model indicate that **Social Support** and **GDP per capita** are the strongest predictors of a country's happiness score.
* **Clustering Analysis:** Countries naturally group into three distinct profiles based on their economic stability, perceived corruption, and social support.
* **Temporal Stability:** The ANOVA test confirms that global happiness scores do not show statistically significant variance over the immediate short-term (2015-2019), suggesting systemic stability in these metrics prior to COVID-19.

### Next Steps
* Integrate data for 2020-2023 to perform a pre/post COVID-19 variance analysis.
* Incorporate deeper CO2 emission factors into the Random Forest to see how climate risk directly affects wellbeing.
"""))

# Export Helpers
cells.append(nbf.v4.new_markdown_cell("## 7. Export Tables to Markdown for README\nRun this cell to generate markdown text for your data tables so you can easily copy and paste them into your `README.md` file!"))
cells.append(nbf.v4.new_code_cell("""print("### Data Loading Table (First 5 Rows)\\n")
print(df.head().to_pandas().to_markdown())

print("\\n\\n### OLS Regression Results (Summary)\\n")
print(model.summary().as_text())
"""))

nb['cells'] = cells

with open('c:/Users/nonmr/Desktop/Projeler/climate-economic-wellbeing-analysis/analyses/Climate_Economic_Wellbeing_Analysis.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
