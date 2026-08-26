"""
dashboard/app.py — Streamlit Dashboard
Faz 8'de tam olarak implement edilecek; şimdilik başlangıç iskeleti.
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Sayfa konfigürasyonu — ilk Streamlit komutu olmalı
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="İklim & Ekonomik Refah Analizi",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Geçici placeholder içerik
# ---------------------------------------------------------------------------
st.title("🌍 İklim Değişimi & Küresel Ekonomik/Sosyal Refah")
st.subheader("Çapraz Etki Analizi Dashboard")

st.info(
    "🚧 **Geliştirme Aşaması** — Bu dashboard Faz 8'de tam olarak implement edilecek.\n\n"
    "Planlanan özellikler:\n"
    "- Ülke bazlı iklim & refah karşılaştırması\n"
    "- Zaman serisi trend grafikleri (2005-2022)\n"
    "- Küme haritası (dünya haritası üzerinde renk kodlu)\n"
    "- Panel regresyon sonuçları görselleştirmesi"
)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Kapsanan Ülke", "~150", help="Tüm kaynaklarda ortak ülkeler")
with col2:
    st.metric("Analiz Penceresi", "2005-2022", help="World Happiness Report başlangıcı")
with col3:
    st.metric("Veri Kaynağı", "3", help="World Bank, Berkeley Earth, WHR")
