import duckdb
import polars as pl
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from statsmodels.tsa.holtwinters import ExponentialSmoothing

DB_PATH = "data/climate_wellbeing.duckdb"
conn = duckdb.connect(str(DB_PATH), read_only=True)
df = conn.execute("SELECT * FROM main_marts.fct_climate_economy").pl()

latest_year = df['year'].max()
df_latest = df.filter(pl.col('year') == latest_year)

# 1. Map
fig_map = px.choropleth(
    df_latest.to_pandas(),
    locations="iso_code",
    color="happiness_score",
    hover_name="country_name",
    color_continuous_scale="RdYlGn",
    title=f"Global Happiness Scores ({latest_year})"
)
fig_map.write_image("docs/map.png", width=1000, height=500)

# 2. Scatter
fig_scatter = px.scatter(
    df_latest.to_pandas(), 
    x="gdp_per_capita", 
    y="happiness_score",
    hover_name="country_name",
    color="happiness_score",
    color_continuous_scale="Viridis",
    log_x=True,
    title=f"Wealth (GDP per Capita) vs Wellbeing ({latest_year})"
)
fig_scatter.write_image("docs/scatter.png", width=1000, height=500)

# 3. Random Forest Feature Importance
df_reg = df_latest.drop_nulls(
    subset=['happiness_score', 'gdp_per_capita', 'social_support', 'life_expectancy', 'freedom', 'corruption']
).to_pandas()
X = df_reg[['gdp_per_capita', 'social_support', 'life_expectancy', 'freedom', 'corruption']]
y = df_reg['happiness_score']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

fig_rf = px.bar(
    x=X.columns, y=rf_model.feature_importances_, 
    labels={'x':'Features', 'y':'Importance'},
    title="Random Forest Feature Importance for Predicting Happiness",
    color=rf_model.feature_importances_, color_continuous_scale="Teal"
)
fig_rf.write_image("docs/rf_importance.png", width=1000, height=500)

# 4. Time Series Forecast
global_trends = df.to_pandas().groupby('year').agg({
    'happiness_score': 'mean'
}).reset_index().sort_values('year')

ts_data = global_trends['happiness_score'].values
years = global_trends['year'].values

model_ts = ExponentialSmoothing(ts_data, trend='add', seasonal=None, initialization_method="estimated")
fit_model = model_ts.fit()

forecast = fit_model.forecast(6)
forecast_years = np.arange(2025, 2031)

fig_forecast = go.Figure()
fig_forecast.add_trace(go.Scatter(x=years, y=ts_data, mode='lines+markers', name='Historical Global Happiness', line=dict(color='blue', width=3)))
fig_forecast.add_trace(go.Scatter(x=forecast_years, y=forecast, mode='lines+markers', name='Forecast (2025-2030)', line=dict(color='red', width=3, dash='dash')))

fig_forecast.update_layout(title='Global Happiness Score Forecast (2025-2030)', xaxis_title='Year', yaxis_title='Average Happiness Score', template='plotly_white')
fig_forecast.write_image("docs/forecast.png", width=1000, height=500)

# 5. CO2 Impact Boxplot
df_climate = df_latest.drop_nulls(subset=['co2_per_capita', 'happiness_score']).to_pandas()
median_co2 = df_climate['co2_per_capita'].median()
df_climate['emission_group'] = np.where(df_climate['co2_per_capita'] > median_co2, 'High Emitters', 'Low Emitters')

fig_co2 = px.box(
    df_climate, x="emission_group", y="happiness_score", color="emission_group",
    title="Wellbeing Variance: High vs Low CO2 Emitters",
    labels={"emission_group": "Emission Group", "happiness_score": "Happiness Score"},
    color_discrete_map={"High Emitters": "crimson", "Low Emitters": "seagreen"}
)
fig_co2.write_image("docs/co2_impact.png", width=1000, height=500)
