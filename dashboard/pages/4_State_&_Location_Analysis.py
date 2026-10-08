"""
Streamlit Page 4: State & Location Analysis
Spatial comparisons, identification of high-risk river stretches and monitoring location lookup.
"""

import os
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="State & Location Analysis", page_icon="🗺️", layout="wide")
st.title("🗺️ State & Location Analysis")
st.markdown("Geographic distribution of river water pollution hotspots and station-level inspection.")


@st.cache_data
def load_data():
    paths = ["data/processed/water_quality_assessed.csv", "../data/processed/water_quality_assessed.csv"]
    for p in paths:
        if os.path.exists(p):
            return pd.read_csv(p)
    return None


df = load_data()

if df is not None:
    tab1, tab2, tab3 = st.tabs(["🏆 State Rankings (BOD Stress)", "🚨 High-Risk River Stretches", "📍 Station Deep Dive"])

    with tab1:
        st.subheader("State-Wise Pollution Burden (Median BOD mg/L)")
        state_agg = df.groupby("State").agg(
            Median_BOD=("BOD_Avg", "median"),
            Median_DO=("DO_Avg", "median"),
            Total_Stations=("Monitoring Location", "nunique"),
            Records=("Year", "count")
        ).reset_index().sort_values(by="Median_BOD", ascending=False)

        fig_state = px.bar(
            state_agg.head(20), x="Median_BOD", y="State", orientation="h",
            color="Median_BOD", color_continuous_scale="Reds",
            title="Top 20 States by River Organic Stress (Median BOD mg/L)"
        )
        fig_state.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_state, use_container_width=True)

        st.dataframe(state_agg, use_container_width=True)

    with tab2:
        st.subheader("Top 20 Most Severely Polluted River Monitoring Locations in India")
        loc_agg = df.groupby(["Monitoring Location", "State"]).agg(
            Mean_BOD=("BOD_Avg", "mean"),
            Min_DO=("DO_Avg", "min"),
            Max_Total_Coliform=("Total_Coliform_Avg", "max"),
            Years_Recorded=("Year", "nunique")
        ).reset_index().sort_values(by="Mean_BOD", ascending=False).head(20)

        fig_loc = px.bar(
            loc_agg, x="Mean_BOD", y="Monitoring Location",
            color="State", orientation="h",
            title="Top 20 River Monitoring Stretches by Mean BOD Concentration (mg/L)"
        )
        fig_loc.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_loc, use_container_width=True)

        st.dataframe(loc_agg, use_container_width=True)

    with tab3:
        st.subheader("Monitoring Station Search & Inspection")
        c1, c2 = st.columns(2)
        with c1:
            sel_state = st.selectbox("Select State:", sorted(df["State"].dropna().unique().tolist()))
        with c2:
            st_locations = sorted(df[df["State"] == sel_state]["Monitoring Location"].dropna().unique().tolist())
            sel_loc = st.selectbox("Select River Monitoring Location:", st_locations)

        station_history = df[(df["State"] == sel_state) & (df["Monitoring Location"] == sel_loc)].sort_values("Year")

        st.write(f"Historical Records for **{sel_loc}** ({len(station_history)} years):")
        cols_to_show = ["Year", "Station Code", "DO_Avg", "BOD_Avg", "pH_Avg", "Conductivity_Avg", "Nitrate_Avg", "CPCB_Designated_Class", "WQI_Category"]
        st.dataframe(station_history[[c for c in cols_to_show if c in station_history.columns]], use_container_width=True)

        if len(station_history) > 1:
            fig_hist = px.line(
                station_history, x="Year", y=["DO_Avg", "BOD_Avg"],
                markers=True, title=f"Historical DO vs. BOD Trend at {sel_loc}"
            )
            st.plotly_chart(fig_hist, use_container_width=True)
else:
    st.error("Data file not found.")
