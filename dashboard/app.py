from pathlib import Path

import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st

# Config
st.set_page_config(
    page_title="Climate Change & Economic Wellbeing",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for a beautiful UI
st.markdown(
    """
<style>
    .main {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    h1, h2, h3 {
        color: #00B4D8;
    }
    .stMetric {
        background-color: #1E2127;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #00B4D8;
    }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def load_data():
    project_root = Path(__file__).parent.parent
    db_path = project_root / "data" / "climate_wellbeing.duckdb"

    if not db_path.exists():
        st.error(f"Database not found at {db_path}!")
        return pd.DataFrame()

    conn = duckdb.connect(str(db_path))
    try:
        df = conn.execute("SELECT * FROM main_marts.fct_climate_economy").df()
    except Exception as e:
        st.error(f"Failed to load data from main_marts.fct_climate_economy: {e}")
        return pd.DataFrame()
    finally:
        conn.close()
    return df


st.title("🌍 Climate Change & Global Wellbeing")
st.subheader("Cross-Impact Analysis Dashboard (Phase 7)")

df = load_data()

if df.empty:
    st.warning("No data available to display. Please ensure Phase 3 (dbt run) was successful.")
    st.stop()

# Sidebar filters
st.sidebar.header("Filters")
available_years = sorted(df["year"].dropna().unique().tolist())
selected_year = st.sidebar.select_slider(
    "Select Year", options=available_years, value=max(available_years) if available_years else None
)

regions = st.sidebar.multiselect(
    "Select Countries (Optional)", options=sorted(df["country_name"].unique().tolist())
)

# Filter Data
filtered_df = df[df["year"] == selected_year]
if regions:
    filtered_df = filtered_df[filtered_df["country_name"].isin(regions)]

# Top metrics
st.markdown("### Key Global Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_happiness = filtered_df["happiness_score"].mean()
    st.metric(
        f"Avg Happiness ({selected_year})",
        f"{avg_happiness:.2f}" if pd.notnull(avg_happiness) else "N/A",
    )
with col2:
    avg_gdp = filtered_df["gdp_per_capita"].mean()
    st.metric("Avg GDP Per Capita", f"${avg_gdp:,.0f}" if pd.notnull(avg_gdp) else "N/A")
with col3:
    avg_co2 = filtered_df["co2_per_capita"].mean()
    st.metric("Avg CO2 Per Capita", f"{avg_co2:.2f} t" if pd.notnull(avg_co2) else "N/A")
with col4:
    countries_count = filtered_df["country_name"].nunique()
    st.metric("Countries Analyzed", f"{countries_count}")

st.divider()

# Charts
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown("### Happiness Score Map")
    if not filtered_df.empty and "iso_code" in filtered_df.columns:
        fig_map = px.choropleth(
            filtered_df,
            locations="iso_code",
            color="happiness_score",
            hover_name="country_name",
            color_continuous_scale="Viridis",
            title=f"World Happiness Map ({selected_year})",
        )
        fig_map.update_layout(
            geo={"showframe": False, "showcoastlines": False, "projection_type": "equirectangular"}
        )
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("Map data unavailable.")

with col_chart2:
    st.markdown("### GDP vs Happiness")
    if not filtered_df.empty:
        fig_scatter = px.scatter(
            filtered_df,
            x="gdp_per_capita",
            y="happiness_score",
            hover_name="country_name",
            size="population" if "population" in filtered_df.columns else None,
            color="happiness_score",
            color_continuous_scale="Viridis",
            log_x=True,
            title=f"Wealth vs Wellbeing ({selected_year})",
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("Scatter data unavailable.")

st.divider()
st.markdown("### Time Series Trend (All Years)")

if not df.empty:
    trend_df = (
        df.groupby("year")[["happiness_score", "gdp_per_capita", "co2_per_capita"]]
        .mean()
        .reset_index()
    )
    fig_trend = px.line(
        trend_df,
        x="year",
        y="happiness_score",
        markers=True,
        title="Global Average Happiness Trend",
        color_discrete_sequence=["#00B4D8"],
    )
    st.plotly_chart(fig_trend, use_container_width=True)
