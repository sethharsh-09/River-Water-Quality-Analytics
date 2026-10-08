"""
Streamlit Main Application: River Water Quality Analytics System
Central Pollution Control Board (CPCB) Standards Compliant Data Science Platform
"""

import os
import sys
import pandas as pd
import streamlit as st

# Setup page config
st.set_page_config(
    page_title="River Water Quality Analytics System",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.3rem;
        font-weight: 800;
        color: #1a365d;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4a5568;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #f7fafc;
        border-radius: 10px;
        padding: 1.2rem;
        border-left: 5px solid #3182ce;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .kpi-val {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2b6cb0;
    }
    .kpi-lbl {
        font-size: 0.85rem;
        color: #718096;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_assessed_data():
    paths = [
        "data/processed/water_quality_assessed.csv",
        "../data/processed/water_quality_assessed.csv"
    ]
    for p in paths:
        if os.path.exists(p):
            return pd.read_csv(p)
    return None


df = load_assessed_data()

st.markdown('<div class="main-header">🌊 National River Water Quality Analytics System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">End-to-End Environmental Data Science & Machine Learning Pipeline • Verified CPCB & BIS Standards</div>', unsafe_allow_html=True)

st.sidebar.image("https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=400&q=80", use_container_width=True)
st.sidebar.title("Navigation")
st.sidebar.info("""
Select an analytical module from the sidebar pages:
- **1. Overview & Audit**
- **2. Water Quality Analytics**
- **3. Yearly Trends (2012-2023)**
- **4. State & Location Analysis**
- **5. WQI & CPCB Assessment**
- **6. Water Quality Prediction**
- **7. Model Performance**
- **8. Feature Importance & SHAP**
- **9. Insights & Recommendations**
""")

if df is not None:
    # KPI Summary Row
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="kpi-lbl">Total Samples</div>
            <div class="kpi-val">{:,}</div>
        </div>
        """.format(len(df)), unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card" style="border-left-color: #38a169;">
            <div class="kpi-lbl">States & UTs</div>
            <div class="kpi-val">{}</div>
        </div>
        """.format(df["State"].nunique()), unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card" style="border-left-color: #dd6b20;">
            <div class="kpi-lbl">Years Monitored</div>
            <div class="kpi-val">{}-{}</div>
        </div>
        """.format(df["Year"].min(), df["Year"].max()), unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="metric-card" style="border-left-color: #319795;">
            <div class="kpi-lbl">Median DO</div>
            <div class="kpi-val">{:.1f} mg/L</div>
        </div>
        """.format(df["DO_Avg"].median()), unsafe_allow_html=True)

    with col5:
        st.markdown("""
        <div class="metric-card" style="border-left-color: #e53e3e;">
            <div class="kpi-lbl">Median BOD</div>
            <div class="kpi-val">{:.1f} mg/L</div>
        </div>
        """.format(df["BOD_Avg"].median()), unsafe_allow_html=True)

    st.write("")
    st.write("")

    # Highlights & Quick Filter
    col_left, col_right = st.columns([1.5, 1])

    with col_left:
        st.subheader("📌 System Architecture & Pipeline Workflow")
        st.markdown("""
        This platform delivers a scientifically verified pipeline built in accordance with Central Pollution Control Board (CPCB) protocols:
        1. **Data Understanding & Cleaning**: Parsing of irregular characters, newline fixes, duplicate elimination, and safe physical outlier capping.
        2. **Feature Engineering**: Average and range derivation, log transforms, and nutrient-stress indices.
        3. **Exploratory & Temporal Analytics**: 2012–2023 trajectory evaluation identifying improving and deteriorating river stretches.
        4. **Scientific Assessment**: Official CPCB Designated Best Use classification (Classes A to E) and Weighted Arithmetic WQI (WAWQI).
        5. **Machine Learning & Zero-Leakage Pipeline**: Champion Tuned Random Forest regressor with cross-validation and SHAP explainability.
        """)

    with col_right:
        st.subheader("🔍 Quick State River Quality Lookup")
        states = sorted(df["State"].dropna().unique().tolist())
        selected_state = st.selectbox("Select State:", states, index=states.index("UTTAR PRADESH") if "UTTAR PRADESH" in states else 0)

        state_df = df[df["State"] == selected_state]
        st.write(f"**Records for {selected_state}:** {len(state_df):,}")
        st.write(f"• Median DO: **{state_df['DO_Avg'].median():.2f} mg/L**")
        st.write(f"• Median BOD: **{state_df['BOD_Avg'].median():.2f} mg/L**")
        st.write(f"• Dominant CPCB Class: **{state_df['CPCB_Designated_Class'].mode()[0] if not state_df['CPCB_Designated_Class'].empty else 'N/A'}**")

        st.info("💡 Use the sidebar to explore in-depth visualizations, predictions, and reports!")

    st.divider()
    st.caption("Developed for River Water Quality Analytics • Central Pollution Control Board (CPCB) Standard Aligned")
else:
    st.error("Assessed dataset not found. Please run the data pipeline first.")
