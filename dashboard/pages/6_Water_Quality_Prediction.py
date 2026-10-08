"""
Streamlit Page 6: Water Quality Prediction
Interactive Machine Learning prediction tool: User inputs water-quality parameters;
Trained champion pipeline predicts BOD concentration and assigns CPCB class & advisory.
"""

import os
import sys
import numpy as np
import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.predict import predict_sample

st.set_page_config(page_title="Water Quality Prediction", page_icon="🤖", layout="wide")
st.title("🤖 Real-Time Water Quality & BOD Predictor")
st.markdown("Enter river physical, chemical, and microbiological readings to obtain machine learning predicted BOD, CPCB Designated Best Use classification, and environmental advisory.")

# Load state options
STATE_OPTIONS = [
    "ANDHRA PRADESH", "ASSAM", "BIHAR", "CHHATTISGARH", "DELHI", "GUJARAT",
    "HARYANA", "HIMACHAL PRADESH", "JAMMU & KASHMIR", "JHARKHAND", "KARNATAKA",
    "KERALA", "MADHYA PRADESH", "MAHARASHTRA", "MEGHALAYA", "ODISHA", "PUNJAB",
    "RAJASTHAN", "TAMIL NADU", "TELANGANA", "UTTAR PRADESH", "UTTARAKHAND", "WEST BENGAL"
]

with st.form("prediction_form"):
    st.subheader("1. Sampling Context & Location")
    c1, c2 = st.columns(2)
    with c1:
        sel_state = st.selectbox("State / Territory:", STATE_OPTIONS, index=STATE_OPTIONS.index("UTTAR PRADESH") if "UTTAR PRADESH" in STATE_OPTIONS else 0)
    with c2:
        sel_year = st.number_input("Monitoring Year:", min_value=2012, max_value=2030, value=2024, step=1)

    st.subheader("2. Physical & Chemical Indicators")
    col1, col2, col3 = st.columns(3)
    with col1:
        temp_avg = st.slider("Temperature (°C) Average:", min_value=5.0, max_value=45.0, value=24.5, step=0.5)
        temp_range = st.slider("Temperature Range (°C):", min_value=0.0, max_value=20.0, value=6.0, step=0.5)

    with col2:
        do_avg = st.slider("Dissolved Oxygen (DO mg/L):", min_value=0.0, max_value=14.0, value=6.2, step=0.1)
        do_range = st.slider("DO Range (mg/L):", min_value=0.0, max_value=8.0, value=2.0, step=0.1)

    with col3:
        ph_avg = st.slider("pH Average:", min_value=4.0, max_value=10.0, value=7.5, step=0.1)
        ph_range = st.slider("pH Range:", min_value=0.0, max_value=4.0, value=0.6, step=0.1)

    st.subheader("3. Nutrients & Microbiological Loading")
    c_ec, c_nit, c_col = st.columns(3)
    with c_ec:
        cond_avg = st.number_input("Conductivity (µmho/cm) Average:", min_value=10.0, max_value=15000.0, value=450.0, step=25.0)
        cond_range = st.number_input("Conductivity Range (µmho/cm):", min_value=0.0, max_value=5000.0, value=120.0, step=10.0)

    with c_nit:
        nitrate_avg = st.number_input("Nitrate-N (mg/L) Average:", min_value=0.0, max_value=100.0, value=1.5, step=0.1)
        nitrate_range = st.number_input("Nitrate-N Range (mg/L):", min_value=0.0, max_value=30.0, value=0.5, step=0.1)

    with c_col:
        tc_avg = st.number_input("Total Coliform (MPN/100ml):", min_value=0.0, max_value=10000000.0, value=850.0, step=50.0)
        fc_avg = st.number_input("Fecal Coliform (MPN/100ml):", min_value=0.0, max_value=5000000.0, value=250.0, step=25.0)

    submitted = st.form_submit_button("⚡ Run Water Quality & BOD Prediction", use_container_width=True)

if submitted:
    sample_payload = {
        "Temp_Avg": temp_avg,
        "Temp_Range": temp_range,
        "DO_Avg": do_avg,
        "DO_Range": do_range,
        "pH_Avg": ph_avg,
        "pH_Range": ph_range,
        "Conductivity_Avg": cond_avg,
        "Conductivity_Range": cond_range,
        "Nitrate_Avg": nitrate_avg,
        "Nitrate_Range": nitrate_range,
        "Total_Coliform_Avg": tc_avg,
        "Fecal_Coliform_Avg": fc_avg,
        "State": sel_state,
        "Year": sel_year
    }

    try:
        result = predict_sample(sample_payload)

        st.success("✅ Prediction Successfully Generated!")

        st.subheader("Prediction Results & Environmental Diagnosis")
        r1, r2, r3, r4 = st.columns(4)

        with r1:
            st.metric("Predicted BOD (mg/L)", f"{result['Predicted_BOD_mg_L']} mg/L")
        with r2:
            st.metric("Risk Level", result["Pollution_Risk_Level"])
        with r3:
            st.metric("CPCB Best Use Class", result["CPCB_Designated_Class"].split("(")[0].strip())
        with r4:
            st.metric("WAWQI Score", f"{result['WQI_Score']:.1f}")

        # Advisory Callout
        risk = result["Pollution_Risk_Level"]
        if risk == "Low":
            st.success(f"**Classification:** {result['CPCB_Designated_Class']} — {result['Environmental_Advisory']}")
        elif risk == "Moderate":
            st.info(f"**Classification:** {result['CPCB_Designated_Class']} — {result['Environmental_Advisory']}")
        elif risk == "High":
            st.warning(f"**Classification:** {result['CPCB_Designated_Class']} — {result['Environmental_Advisory']}")
        else:
            st.error(f"**Classification:** {result['CPCB_Designated_Class']} — {result['Environmental_Advisory']}")

        st.markdown(f"**WAWQI Grade:** `{result['WQI_Category']}`")

    except Exception as e:
        st.error(f"Prediction failed: {e}")
