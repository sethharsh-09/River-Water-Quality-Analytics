"""
Streamlit Page 5: WQI & CPCB Assessment
Official Central Pollution Control Board (CPCB) Designated Best Use Criteria
and Weighted Arithmetic Water Quality Index (WAWQI) evaluation.
"""

import os
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="WQI & CPCB Assessment", page_icon="🧪", layout="wide")
st.title("🧪 Official Water Quality Assessment")
st.markdown("Ground-truth regulatory assessment adhering strictly to Central Pollution Control Board (CPCB) and BIS:10500 standards.")


@st.cache_data
def load_data():
    paths = ["data/processed/water_quality_assessed.csv", "../data/processed/water_quality_assessed.csv"]
    for p in paths:
        if os.path.exists(p):
            return pd.read_csv(p)
    return None


df = load_data()

if df is not None:
    tab1, tab2, tab3 = st.tabs(["🏛️ CPCB Designated Best Use Classes", "📊 Weighted Arithmetic WQI (WAWQI)", "📋 Regulatory Standards Reference"])

    with tab1:
        st.subheader("CPCB Designated Best Use Classification Distribution")
        cpcb_counts = df["CPCB_Designated_Class"].value_counts().reset_index()
        cpcb_counts.columns = ["CPCB Class", "Record Count"]

        c1, c2 = st.columns([1.5, 1])
        with c1:
            fig_cpcb = px.bar(
                cpcb_counts, x="Record Count", y="CPCB Class", orientation="h",
                color="CPCB Class", color_discrete_sequence=px.colors.qualitative.Prism,
                title="Distribution of Monitored River Samples across CPCB Classes"
            )
            fig_cpcb.update_layout(showlegend=False, yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_cpcb, use_container_width=True)

        with c2:
            st.write("**Classification Breakdown:**")
            cpcb_counts["Share (%)"] = (cpcb_counts["Record Count"] / len(df) * 100).round(1)
            st.dataframe(cpcb_counts, use_container_width=True)

            st.warning("""
            🚨 **Below-E Critical Stretches:** Represent river sections failing all primary criteria (severe dissolved oxygen depletion < 4 mg/L or excessive BOD > 3 mg/L).
            """)

    with tab2:
        st.subheader("Weighted Arithmetic WQI (WAWQI) Distribution")
        wqi_counts = df["WQI_Category"].value_counts().reset_index()
        wqi_counts.columns = ["Category", "Count"]

        c1, c2 = st.columns([1.2, 1.2])
        with c1:
            fig_pie = px.pie(
                wqi_counts, names="Category", values="Count",
                hole=0.4, title="River Water Quality Grades Proportion",
                color_discrete_sequence=px.colors.sequential.Teal
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with c2:
            st.subheader("WQI Score Distribution by State")
            sel_state = st.selectbox("Select State for WQI Profile:", sorted(df["State"].dropna().unique().tolist()))
            st_wqi = df[df["State"] == sel_state]["WQI"].dropna()
            fig_hist = px.histogram(
                st_wqi, x="WQI", nbins=40,
                title=f"WQI Score Histogram in {sel_state}",
                color_discrete_sequence=["#319795"]
            )
            st.plotly_chart(fig_hist, use_container_width=True)

    with tab3:
        st.subheader("Official Regulatory Benchmark Criteria")
        st.markdown("""
        ### CPCB Designated Best Use Thresholds:
        | Class | Designated Best Use | pH | DO (mg/L) | BOD (mg/L) | Total Coliform (MPN/100ml) |
        | :--- | :--- | :--- | :--- | :--- | :--- |
        | **Class A** | Drinking water without conventional treatment | 6.5 – 8.5 | ≥ 6.0 | ≤ 2.0 | ≤ 50 |
        | **Class B** | Outdoor bathing (organized) | 6.5 – 8.5 | ≥ 5.0 | ≤ 3.0 | ≤ 500 |
        | **Class C** | Drinking water after conventional treatment | 6.0 – 9.0 | ≥ 4.0 | ≤ 3.0 | ≤ 5,000 |
        | **Class D** | Wildlife propagation and Fisheries | 6.5 – 8.5 | ≥ 4.0 | — | — |
        | **Class E** | Irrigation, industrial cooling | 6.0 – 8.5 | — | — | Conductivity ≤ 2,250 µmho/cm |
        | **Below-E** | Critically Polluted / Unsuitable | < 6.0 or > 9.0 | < 4.0 | > 3.0 | > 5,000 |

        *Source: Central Pollution Control Board (CPCB), Ministry of Environment, Forest and Climate Change, Govt. of India.*
        """)
else:
    st.error("Data file not found.")
