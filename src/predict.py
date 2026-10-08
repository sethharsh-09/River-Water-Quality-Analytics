"""
Inference and Prediction Module for River Water Quality Analytics System
Provides:
- Easy-to-use prediction interface for single sample or batch inputs
- Integration with official CPCB standards and WAWQI scoring
- Environmental risk assessment and advisory output
"""

import os
import sys
import numpy as np
import pandas as pd
import joblib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.assessment import classify_cpcb_designated_best_use, calculate_wawqi


MODEL_ARTIFACT_PATH = "models/best_model.joblib"


def load_trained_pipeline(model_path: str = MODEL_ARTIFACT_PATH):
    """Loads the serialized model pipeline artifact."""
    if not os.path.exists(model_path):
        alt = os.path.join(os.path.dirname(__file__), "..", model_path)
        if os.path.exists(alt):
            model_path = alt
        else:
            raise FileNotFoundError(f"Model file not found at {model_path}. Please train model first via src.train.")

    artifact = joblib.load(model_path)
    return artifact


def predict_sample(sample_dict: dict, model_path: str = MODEL_ARTIFACT_PATH) -> dict:
    """
    Predicts BOD_Avg and computes CPCB water quality class for a single input record.

    Example sample_dict:
    {
        "Temp_Avg": 22.0, "Temp_Range": 6.0,
        "DO_Avg": 6.5, "DO_Range": 2.0,
        "pH_Avg": 7.6, "pH_Range": 0.8,
        "Conductivity_Avg": 350.0, "Conductivity_Range": 80.0,
        "Nitrate_Avg": 1.2, "Nitrate_Range": 0.5,
        "Total_Coliform_Avg": 450.0,
        "Fecal_Coliform_Avg": 120.0,
        "State": "UTTAR PRADESH",
        "Year": 2024
    }
    """
    artifact = load_trained_pipeline(model_path)
    pipeline = artifact["pipeline"]

    # Calculate derived log-transforms if not present
    df_in = pd.DataFrame([sample_dict])

    if "Log_Total_Coliform" not in df_in.columns and "Total_Coliform_Avg" in df_in.columns:
        df_in["Log_Total_Coliform"] = np.log10(df_in["Total_Coliform_Avg"].clip(lower=0) + 1.0)
    elif "Log_Total_Coliform" not in df_in.columns:
        df_in["Log_Total_Coliform"] = 0.0

    if "Log_Fecal_Coliform" not in df_in.columns and "Fecal_Coliform_Avg" in df_in.columns:
        df_in["Log_Fecal_Coliform"] = np.log10(df_in["Fecal_Coliform_Avg"].clip(lower=0) + 1.0)
    elif "Log_Fecal_Coliform" not in df_in.columns:
        df_in["Log_Fecal_Coliform"] = 0.0

    # ML Model Prediction for BOD (mg/L)
    predicted_bod = float(pipeline.predict(df_in)[0])
    predicted_bod = max(0.0, round(predicted_bod, 2))

    # Evaluate CPCB class using predicted BOD and provided DO/pH/Coliform
    eval_row = df_in.iloc[0].to_dict()
    eval_row["BOD_Avg"] = predicted_bod

    cpcb_class = classify_cpcb_designated_best_use(eval_row)

    # Calculate WAWQI
    df_eval = pd.DataFrame([eval_row])
    df_wawqi = calculate_wawqi(df_eval)
    wqi_score = float(df_wawqi["WQI"].iloc[0])
    wqi_category = str(df_wawqi["WQI_Category"].iloc[0])

    # Environmental Health Advisory
    if predicted_bod <= 2.0:
        advisory = "Pristine to Low Organic Pollution. Water meets drinking/bathing criteria under proper disinfection."
        risk_level = "Low"
    elif predicted_bod <= 5.0:
        advisory = "Moderate Organic Stress. Typical of domestic non-point runoff; requires conventional filtration."
        risk_level = "Moderate"
    elif predicted_bod <= 10.0:
        advisory = "High Organic Pollution. Exceeds bathing standards; indicative of untreated sewage discharge."
        risk_level = "High"
    else:
        advisory = "Severe Organic Overload. Hypoxic conditions likely; harmful to aquatic organisms and unfit for direct use."
        risk_level = "Critical"

    return {
        "Predicted_BOD_mg_L": predicted_bod,
        "CPCB_Designated_Class": cpcb_class,
        "WQI_Score": wqi_score,
        "WQI_Category": wqi_category,
        "Pollution_Risk_Level": risk_level,
        "Environmental_Advisory": advisory
    }


def predict_batch(df_batch: pd.DataFrame, model_path: str = MODEL_ARTIFACT_PATH) -> pd.DataFrame:
    """Predicts BOD and assesses water quality for a batch dataframe."""
    artifact = load_trained_pipeline(model_path)
    pipeline = artifact["pipeline"]

    df = df_batch.copy()
    if "Log_Total_Coliform" not in df.columns and "Total_Coliform_Avg" in df.columns:
        df["Log_Total_Coliform"] = np.log10(df["Total_Coliform_Avg"].clip(lower=0) + 1.0)
    if "Log_Fecal_Coliform" not in df.columns and "Fecal_Coliform_Avg" in df.columns:
        df["Log_Fecal_Coliform"] = np.log10(df["Fecal_Coliform_Avg"].clip(lower=0) + 1.0)

    preds = pipeline.predict(df)
    df["Predicted_BOD_mg_L"] = np.clip(preds, 0.0, None).round(2)

    # Compute CPCB & WQI
    df["CPCB_Designated_Class"] = df.apply(
        lambda r: classify_cpcb_designated_best_use({**r.to_dict(), "BOD_Avg": r["Predicted_BOD_mg_L"]}), axis=1
    )
    df_assessed = calculate_wawqi(df.rename(columns={"Predicted_BOD_mg_L": "BOD_Avg_Temp"}))
    df["WQI_Score"] = df_assessed["WQI"]
    df["WQI_Category"] = df_assessed["WQI_Category"]

    return df
