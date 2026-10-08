"""
Streamlit Page 1: Overview & Audit
Audits raw vs. cleaned dataset dimensions, missingness, duplicates, and column schema.
"""

import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Overview & Audit", page_icon="📊", layout="wide")
st.title("📊 Data Understanding & Audit")
st.markdown("Detailed audit of raw dataset artifacts, cleaning transformations, missing values, and categorical schemas.")


@st.cache_data
def load_datasets():
    cleaned_path = "data/processed/cleaned_data.csv" if os.path.exists("data/processed/cleaned_data.csv") else "../data/processed/cleaned_data.csv"
    assessed_path = "data/processed/water_quality_assessed.csv" if os.path.exists("data/processed/water_quality_assessed.csv") else "../data/processed/water_quality_assessed.csv"

    df_clean = pd.read_csv(cleaned_path) if os.path.exists(cleaned_path) else None
    df_assessed = pd.read_csv(assessed_path) if os.path.exists(assessed_path) else None
    return df_clean, df_assessed


df_clean, df_assessed = load_datasets()

if df_clean is not None:
    tab1, tab2, tab3 = st.tabs(["📁 Dataset Summary & Schema", "🧹 Cleaning & Outlier Audit", "🔍 Data Preview"])

    with tab1:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Cleaned Rows", f"{len(df_clean):,}")
        c2.metric("Total Features", f"{df_clean.shape[1]}")
        c3.metric("Duplicates Removed", "362 rows")
        c4.metric("Temporal Span", f"{df_clean['Year'].min()} – {df_clean['Year'].max()}")

        st.subheader("Data Columns and Missingness Profile")
        missing_df = pd.DataFrame({
            "Column Name": df_clean.columns,
            "Data Type": df_clean.dtypes.astype(str),
            "Non-Null Count": df_clean.notna().sum(),
            "Missing Count": df_clean.isna().sum(),
            "Missing %": (df_clean.isna().mean() * 100).round(2)
        }).reset_index(drop=True)
        st.dataframe(missing_df, use_container_width=True)

    with tab2:
        st.subheader("Audit of Handled Artifacts & Domain Capping")
        st.markdown("""
        | Measurement Column | Raw Issues Encountered | Cleaning / Normalization Applied | Safe Capping Standard |
        | :--- | :--- | :--- | :--- |
        | **Temperature (C)** | Corrupted units, typos up to 269°C | ASCII unit normalization, 10x divisor for typo | Capped [0°C, 50°C] |
        | **pH** | Malformed entries up to 1480 | Fixed missing decimal points | Bounded [0.0, 14.0] |
        | **Dissolved Oxygen** | Tokens: `BDL`, `nil`, `-` | Converted placeholders to `NaN` | Saturated cap at 25.0 mg/L |
        | **BOD (mg/L)** | Tokens: `BDL`, `nil`, `-` | Converted placeholders to `NaN` | Capped at 500 mg/L |
        | **State** | Embedded newlines (`\\n`), spelling variations | Comprehensive 54-to-30 state mapping | Normalized standard uppercase |
        """)

    with tab3:
        st.subheader("Interactive Dataset Explorer")
        filter_state = st.multiselect("Filter by State:", options=sorted(df_clean["State"].dropna().unique().tolist()))
        filter_year = st.slider("Filter by Year:", int(df_clean["Year"].min()), int(df_clean["Year"].max()), (int(df_clean["Year"].min()), int(df_clean["Year"].max())))

        df_view = df_clean.copy()
        if filter_state:
            df_view = df_view[df_view["State"].isin(filter_state)]
        df_view = df_view[(df_view["Year"] >= filter_year[0]) & (df_view["Year"] <= filter_year[1])]

        st.write(f"Showing **{len(df_view):,}** matching records:")
        st.dataframe(df_view.head(100), use_container_width=True)
else:
    st.error("Cleaned data file not found.")
