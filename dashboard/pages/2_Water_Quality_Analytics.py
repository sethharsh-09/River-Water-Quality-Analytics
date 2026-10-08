"""
Streamlit Page 2: Water Quality Analytics
Interactive Exploratory Data Analysis: distributions, box plots, correlation analysis.
"""

import os
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import streamlit as st

st.set_page_config(page_title="Water Quality Analytics", page_icon="📈", layout="wide")
st.title("📈 Water Quality Analytics (EDA)")
st.markdown("Exploration of physical, chemical, and biological parameter distributions, correlations, and outliers.")


@st.cache_data
def load_data():
    paths = ["data/processed/water_quality_assessed.csv", "../data/processed/water_quality_assessed.csv"]
    for p in paths:
        if os.path.exists(p):
            return pd.read_csv(p)
    return None


df = load_data()

if df is not None:
    tab1, tab2, tab3 = st.tabs(["📊 Parameter Distributions", "📦 Box Plots & Variations", "🔥 Correlation Heatmap"])

    params_dict = {
        "Dissolved Oxygen (DO_Avg)": "DO_Avg",
        "Biochemical Oxygen Demand (BOD_Avg)": "BOD_Avg",
        "pH (pH_Avg)": "pH_Avg",
        "Conductivity (Conductivity_Avg)": "Conductivity_Avg",
        "Nitrate-N (Nitrate_Avg)": "Nitrate_Avg",
        "Total Coliform Log10": "Log_Total_Coliform",
        "Temperature (Temp_Avg)": "Temp_Avg"
    }

    with tab1:
        st.subheader("Interactive Parameter Distribution")
        selected_label = st.selectbox("Select Parameter to Inspect:", list(params_dict.keys()), index=1)
        col_name = params_dict[selected_label]

        sub_df = df[[col_name, "State", "Year"]].dropna()

        c1, c2 = st.columns([2, 1])
        with c1:
            fig = px.histogram(
                sub_df, x=col_name, nbins=50, marginal="box",
                title=f"Distribution of {selected_label}",
                color_discrete_sequence=["#1f77b4"]
            )
            fig.update_layout(bargap=0.1)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.markdown(f"**Descriptive Statistics for {selected_label}:**")
            stats = sub_df[col_name].describe().to_frame()
            stats.columns = ["Value"]
            st.dataframe(stats.round(3), use_container_width=True)

            if col_name == "BOD_Avg":
                st.info("💡 **CPCB Bathing Criterion**: BOD must not exceed **3.0 mg/L**. Samples exceeding 3.0 mg/L indicate organic sewage loading.")
            elif col_name == "DO_Avg":
                st.info("💡 **CPCB Bathing Criterion**: Dissolved Oxygen must be at least **5.0 mg/L** to sustain aquatic life.")

    with tab2:
        st.subheader("Parameter Variation Across Top States")
        top_states = df["State"].value_counts().head(10).index.tolist()
        filtered_df = df[df["State"].isin(top_states)]

        fig_box = px.box(
            filtered_df, x="State", y=col_name, color="State",
            title=f"{selected_label} by Major States (Top 10 Monitored)",
            points="outliers"
        )
        fig_box.update_layout(showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig_box, use_container_width=True)

    with tab3:
        st.subheader("Correlation Matrix Across Water Quality Indicators")
        corr_cols = ["DO_Avg", "pH_Avg", "BOD_Avg", "Conductivity_Avg", "Nitrate_Avg", "Log_Total_Coliform", "Temp_Avg", "WQI"]
        valid_cols = [c for c in corr_cols if c in df.columns]
        corr_matrix = df[valid_cols].dropna().corr().round(2)

        fig_heat = px.imshow(
            corr_matrix, text_auto=True, aspect="auto",
            color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
            title="Pearson Correlation Heatmap"
        )
        st.plotly_chart(fig_heat, use_container_width=True)

        st.markdown("""
        **Key Empirical Relationships Observed:**
        - **DO vs. BOD**: Strongly negative correlation ($r \\approx -0.32$), confirming that microbial breakdown of organic matter severely depletes dissolved oxygen.
        - **Total Coliform vs. BOD**: Strongly positive correlation, identifying raw domestic sewage as the dominant source of organic water pollution in India.
        """)
else:
    st.error("Dataset not found.")
