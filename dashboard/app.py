import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pathlib import Path

# --- 1. CONFIG & UI SETUP ---
st.set_page_config(
    page_title="Climate & Wellbeing Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Premium Glassmorphism & Modern CSS
st.markdown(
    """
<style>
    /* Global Background */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #58a6ff !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Metrics / Metric Cards */
    [data-testid="stMetricValue"] {
        color: #58a6ff;
        font-size: 2rem !important;
        font-weight: 700;
    }
    [data-testid="stMetric"] {
        background: rgba(33, 38, 45, 0.6);
        border: 1px solid rgba(240, 246, 252, 0.1);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        transition: transform 0.2s ease-in-out;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        border-color: #58a6ff;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 8px 8px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(88, 166, 255, 0.1);
        border-bottom: 2px solid #58a6ff !important;
    }
</style>
""",
    unsafe_allow_html=True,
)


# --- 2. DATA LOADING ---
@st.cache_data
def load_data():
    project_root = Path(__file__).parent.parent
    db_path = project_root / "data" / "climate_wellbeing.duckdb"

    if not db_path.exists():
        st.error(f"Database not found at {db_path}!")
        return pd.DataFrame()

    conn = duckdb.connect(str(db_path), read_only=True)
    df = conn.execute("SELECT * FROM main_marts.fct_climate_economy").df()
    conn.close()
    return df


df = load_data()

if df.empty:
    st.warning("No data found. Please run the dbt pipeline first.")
    st.stop()

# --- 3. SIDEBAR FILTERS ---
st.sidebar.title("🌍 Controls")
st.sidebar.markdown("Filter the global data using the options below.")

years = sorted(df["year"].dropna().unique().tolist())
selected_year = st.sidebar.slider(
    "Select Year", min_value=min(years), max_value=max(years), value=max(years)
)

countries = sorted(df["country_name"].unique().tolist())
selected_countries = st.sidebar.multiselect("Filter by Countries (Optional)", options=countries)

filtered_df = df[df["year"] == selected_year]
if selected_countries:
    filtered_df = filtered_df[filtered_df["country_name"].isin(selected_countries)]

# --- 4. MAIN LAYOUT ---
st.title("Global Climate & Wellbeing Analytics")
st.markdown(
    "Interactive dashboard exploring the intersection of macroeconomic growth, carbon emissions, and human happiness."
)

# Metric Cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    avg_happy = filtered_df["happiness_score"].mean()
    st.metric("Avg Global Happiness", f"{avg_happy:.2f}" if pd.notnull(avg_happy) else "N/A")
with col2:
    avg_gdp = filtered_df["gdp_per_capita"].mean()
    st.metric("Avg GDP per Capita", f"${avg_gdp:,.0f}" if pd.notnull(avg_gdp) else "N/A")
with col3:
    avg_co2 = filtered_df["co2_per_capita"].mean()
    st.metric("Avg CO2 (Tonnes)", f"{avg_co2:.2f}" if pd.notnull(avg_co2) else "N/A")
with col4:
    st.metric("Countries Analysed", len(filtered_df["country_name"].unique()))

st.markdown("<br>", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(
    ["🌍 Overview & Maps", "😷 COVID-19 Resilience", "🏭 Climate Impact (CO2)"]
)

# TAB 1: OVERVIEW
with tab1:
    st.markdown("### Happiness Score Map")
    if not filtered_df.empty and "iso_code" in filtered_df.columns:
        fig_map = px.choropleth(
            filtered_df,
            locations="iso_code",
            color="happiness_score",
            hover_name="country_name",
            color_continuous_scale="Tealgrn",
            title=f"Global Wellbeing Distribution ({selected_year})",
        )
        fig_map.update_layout(
            geo=dict(bgcolor="rgba(0,0,0,0)", showframe=False, showcoastlines=True),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_map, use_container_width=True)

    st.markdown("### Wealth vs Wellbeing")
    if not filtered_df.empty:
        fig_scatter = px.scatter(
            filtered_df,
            x="gdp_per_capita",
            y="happiness_score",
            size="population",
            color="happiness_score",
            hover_name="country_name",
            log_x=True,
            color_continuous_scale="Plotly3",
            title=f"GDP per Capita vs Happiness Score ({selected_year})",
        )
        fig_scatter.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_scatter, use_container_width=True)

# TAB 2: COVID-19
with tab2:
    st.markdown("### Pre vs Post COVID-19 Happiness Trends")
    st.markdown(
        "Observing how global wellbeing reacted to the systemic shock of the COVID-19 pandemic."
    )

    trend_df = df.groupby("year")["happiness_score"].mean().reset_index()
    fig_covid = px.line(
        trend_df,
        x="year",
        y="happiness_score",
        markers=True,
        title="Global Average Happiness (2015-2024)",
        color_discrete_sequence=["#ff7f0e"],
    )
    # Highlight COVID era
    fig_covid.add_vrect(
        x0=2020,
        x1=max(years),
        fillcolor="red",
        opacity=0.1,
        layer="below",
        line_width=0,
        annotation_text="Post-COVID Era",
    )
    fig_covid.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_covid, use_container_width=True)

# TAB 3: CLIMATE IMPACT
with tab3:
    st.markdown("### The CO2 Paradox")
    st.markdown("Does high carbon output correlate with higher happiness due to industrial wealth?")

    df_climate = filtered_df.dropna(subset=["co2_per_capita", "happiness_score"]).copy()
    if not df_climate.empty:
        median_co2 = df_climate["co2_per_capita"].median()
        df_climate["Emission Group"] = df_climate["co2_per_capita"].apply(
            lambda x: "High Emitters" if x > median_co2 else "Low Emitters"
        )

        fig_box = px.box(
            df_climate,
            x="Emission Group",
            y="happiness_score",
            color="Emission Group",
            title=f"Wellbeing Variance: High vs Low CO2 Emitters ({selected_year})",
            color_discrete_map={"High Emitters": "#d62728", "Low Emitters": "#2ca02c"},
        )
        fig_box.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_box, use_container_width=True)
    else:
        st.info("Not enough data to calculate CO2 impact for this selection.")
