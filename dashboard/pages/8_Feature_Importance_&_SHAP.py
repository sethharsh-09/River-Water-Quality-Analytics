"""
Streamlit Page 8: Feature Importance & Explainability (SHAP)
Explains champion model drivers using Gini/Gain feature importance and SHAP analysis.
"""

import os
import streamlit as st

st.set_page_config(page_title="Feature Importance & SHAP", page_icon="🔍", layout="wide")
st.title("🔍 Model Explainability & SHAP Analysis")
st.markdown("Interpretable AI diagnostics revealing the physical and biological drivers governing river water quality degradation.")

tab1, tab2, tab3 = st.tabs(["🌳 Feature Importance (Ensemble)", "🐝 SHAP Summary Beeswarm", "💡 Domain Scientific Interpretation"])

fi_path = "visualizations/feature_importance.png" if os.path.exists("visualizations/feature_importance.png") else "../visualizations/feature_importance.png"
shap_path = "visualizations/shap_summary.png" if os.path.exists("visualizations/shap_summary.png") else "../visualizations/shap_summary.png"

with tab1:
    st.subheader("Top Features Driving Biochemical Oxygen Demand (BOD)")
    if os.path.exists(fi_path):
        st.image(fi_path, caption="Random Forest Feature Importance Rankings", use_container_width=True)
    else:
        st.warning("Feature importance plot not found. Run src/evaluate.py first.")

with tab2:
    st.subheader("SHAP (SHapley Additive exPlanations) Global Summary")
    st.markdown("""
    SHAP values quantify how each parameter shifts model output away from the base expected value.
    - **Red dots** indicate higher parameter values; **Blue dots** indicate lower values.
    - Dots to the right indicate positive influence (increasing predicted BOD); dots to the left decrease predicted BOD.
    """)
    if os.path.exists(shap_path):
        st.image(shap_path, caption="SHAP Summary Plot on Test Set Samples", use_container_width=True)
    else:
        st.warning("SHAP plot not found.")

with tab3:
    st.subheader("Environmental & Biochemical Explanations")
    st.markdown("""
    1. **Total Coliform & Fecal Coliform Counts**:
       - *Finding:* Dominant positive driver of elevated BOD.
       - *Mechanism:* Coliform bacteria originate from untreated domestic wastewater and sewage discharge. High coliform density correlates directly with organic carbon abundance, requiring intensive oxygen consumption by bacteria.
    2. **Dissolved Oxygen Deficit (Inverse DO)**:
       - *Finding:* Strongly negative SHAP contribution.
       - *Mechanism:* In heavily polluted streams, aerobic decomposition rapidly consumes oxygen. Low DO levels (< 4 mg/L) serve as the primary biochemical footprint of high BOD.
    3. **Nitrate-N (Nitrate_Avg)**:
       - *Finding:* Moderate positive contribution.
       - *Mechanism:* Elevated nitrates indicate agricultural fertilizer runoff and nitrified municipal effluents, fueling eutrophication.
    4. **Geographic State Encoding**:
       - *Finding:* State-level categorical indicators capture regional sewage treatment capacity and industrial density variations.
    """)
