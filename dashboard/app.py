import streamlit as st

st.set_page_config(
    page_title="Climate Change & Economic Wellbeing Analysis",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Climate Change & Global Economic / Social Wellbeing")
st.subheader("Cross-Impact Analysis Dashboard")

st.info(
    "**Under Development** — This dashboard will be fully implemented in Phase 8.\n\n"
    "Planned features:\n"
    "- Country-level climate & wellbeing comparison\n"
    "- Time series trend charts (2005-2022)\n"
    "- Cluster map (choropleth on world map)\n"
    "- Panel regression results visualization"
)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Countries Covered", "~140", help="Countries present in all sources")
with col2:
    st.metric("Analysis Window", "2005-2022", help="Bounded by WHR availability")
with col3:
    st.metric("Data Sources", "4", help="World Bank, OWID CO2, Berkeley Earth, WHR")
