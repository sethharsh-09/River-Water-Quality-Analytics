"""
Water Quality Assessment Module for River Water Quality Analytics System
Implements official water quality assessments based strictly on verified standards:
1. CPCB (Central Pollution Control Board, India) Designated Best Use Criteria (Classes A through E & Below-E).
2. Weighted Arithmetic Water Quality Index (WAWQI) Method using BIS/CPCB benchmark standards.

References:
- Central Pollution Control Board (CPCB), MoEF&CC, Govt. of India: Water Quality Criteria for Designated Best Use.
- Bureau of Indian Standards (BIS 10500:2012): Drinking Water Specification.
- Brown et al. (1970) / Horton (1965): Weighted Arithmetic Water Quality Index method.
"""

import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# CPCB Water Quality Benchmark Limits
CPCB_BENCHMARKS = {
    "DO_ideal": 14.6,       # Dissolved oxygen saturation at 0°C (mg/L)
    "DO_standard": 5.0,    # Minimum permissible DO for aquatic/bathing health (mg/L)
    "BOD_ideal": 0.0,      # Ideal BOD in pristine river (mg/L)
    "BOD_standard": 3.0,   # Permissible river BOD upper limit (mg/L)
    "pH_ideal": 7.0,       # Neutral pH
    "pH_standard": 8.5,    # Upper permissible pH limit
    "EC_ideal": 0.0,       # Conductivity ideal (umho/cm)
    "EC_standard": 1000.0, # Permissible conductivity limit (umho/cm)
    "Nitrate_ideal": 0.0,  # Nitrate ideal (mg/L)
    "Nitrate_standard": 45.0, # Permissible nitrate limit (mg/L)
    "TC_ideal": 0.0,       # Total coliform ideal (MPN/100ml)
    "TC_standard": 5000.0  # Permissible coliform limit for conventional treatment (MPN/100ml)
}


def classify_cpcb_designated_best_use(row) -> str:
    """
    Classifies a river water sample according to the official CPCB Designated Best Use Criteria:
    - Class A: Drinking Water Source without conventional treatment but after disinfection.
      (DO >= 6.0 mg/L, BOD <= 2.0 mg/L, pH 6.5-8.5, Total Coliform <= 50 MPN/100ml)
    - Class B: Outdoor bathing (Organized).
      (DO >= 5.0 mg/L, BOD <= 3.0 mg/L, pH 6.5-8.5, Total Coliform <= 500 MPN/100ml)
    - Class C: Drinking water source after conventional treatment and disinfection.
      (DO >= 4.0 mg/L, BOD <= 3.0 mg/L, pH 6.0-9.0, Total Coliform <= 5000 MPN/100ml)
    - Class D: Propagation of Wild life and Fisheries.
      (DO >= 4.0 mg/L, pH 6.5-8.5)
    - Class E: Irrigation, Industrial cooling, Controlled waste disposal.
      (pH 6.0-8.5, Conductivity <= 2250 umho/cm)
    - Below-E / Polluted: Exceeds permissible limits (e.g. DO < 4.0 or BOD > 3.0 or EC > 2250).
    """
    do = row.get("DO_Avg", np.nan)
    bod = row.get("BOD_Avg", np.nan)
    ph = row.get("pH_Avg", np.nan)
    tc = row.get("Total_Coliform_Avg", np.nan)
    ec = row.get("Conductivity_Avg", np.nan)

    # Class A
    is_class_a = (
        (pd.isna(do) or do >= 6.0) and
        (pd.isna(bod) or bod <= 2.0) and
        (pd.isna(ph) or (6.5 <= ph <= 8.5)) and
        (pd.isna(tc) or tc <= 50.0)
    )
    if is_class_a and not (pd.isna(do) and pd.isna(bod)):
        return "Class A (Drinking w/o Treatment)"

    # Class B
    is_class_b = (
        (pd.isna(do) or do >= 5.0) and
        (pd.isna(bod) or bod <= 3.0) and
        (pd.isna(ph) or (6.5 <= ph <= 8.5)) and
        (pd.isna(tc) or tc <= 500.0)
    )
    if is_class_b and not (pd.isna(do) and pd.isna(bod)):
        return "Class B (Outdoor Bathing)"

    # Class C
    is_class_c = (
        (pd.isna(do) or do >= 4.0) and
        (pd.isna(bod) or bod <= 3.0) and
        (pd.isna(ph) or (6.0 <= ph <= 9.0)) and
        (pd.isna(tc) or tc <= 5000.0)
    )
    if is_class_c and not (pd.isna(do) and pd.isna(bod)):
        return "Class C (Drinking after Treatment)"

    # Class D
    is_class_d = (
        (pd.isna(do) or do >= 4.0) and
        (pd.isna(ph) or (6.5 <= ph <= 8.5))
    )
    if is_class_d and (pd.isna(bod) or bod <= 5.0):
        return "Class D (Wildlife & Fisheries)"

    # Class E
    is_class_e = (
        (pd.isna(ph) or (6.0 <= ph <= 8.5)) and
        (pd.isna(ec) or ec <= 2250.0)
    )
    if is_class_e and (pd.isna(bod) or bod <= 10.0):
        return "Class E (Irrigation & Industrial)"

    return "Below-E (Severely Polluted)"


def calculate_wawqi(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes Weighted Arithmetic Water Quality Index (WAWQI).
    Weights W_i are inversely proportional to permissible standard limits S_i.
    Quality ratings q_i = 100 * |V_i - V_ideal| / |S_i - V_ideal|
    WQI = sum(q_i * w_i) / sum(w_i) for all available parameters.
    """
    df = df.copy()

    params = {
        "DO_Avg": {"ideal": CPCB_BENCHMARKS["DO_ideal"], "standard": CPCB_BENCHMARKS["DO_standard"]},
        "BOD_Avg": {"ideal": CPCB_BENCHMARKS["BOD_ideal"], "standard": CPCB_BENCHMARKS["BOD_standard"]},
        "pH_Avg": {"ideal": CPCB_BENCHMARKS["pH_ideal"], "standard": CPCB_BENCHMARKS["pH_standard"]},
        "Conductivity_Avg": {"ideal": CPCB_BENCHMARKS["EC_ideal"], "standard": CPCB_BENCHMARKS["EC_standard"]},
        "Nitrate_Avg": {"ideal": CPCB_BENCHMARKS["Nitrate_ideal"], "standard": CPCB_BENCHMARKS["Nitrate_standard"]},
        "Total_Coliform_Avg": {"ideal": CPCB_BENCHMARKS["TC_ideal"], "standard": CPCB_BENCHMARKS["TC_standard"]}
    }

    # Unit weights k / S_i
    reciprocal_sum = sum(1.0 / p["standard"] for p in params.values())
    k = 1.0 / reciprocal_sum
    unit_weights = {col: k / p["standard"] for col, p in params.items()}

    # Calculate sub-indices
    qi_dict = {}
    for col, p in params.items():
        if col in df.columns:
            ideal = p["ideal"]
            standard = p["standard"]
            val = df[col]
            # Sub-index q_i
            # For DO: q_i = 100 * (DO - 14.6) / (5.0 - 14.6)
            qi = 100.0 * (val - ideal).abs() / abs(standard - ideal)
            qi_dict[col] = qi

    # Weighted sum
    wqi_numerator = pd.Series(0.0, index=df.index)
    wqi_denominator = pd.Series(0.0, index=df.index)

    for col in params:
        if col in qi_dict:
            qi = qi_dict[col]
            w = unit_weights[col]
            valid_mask = qi.notna()
            wqi_numerator += (qi * w).fillna(0.0)
            wqi_denominator += valid_mask * w

    # Avoid divide by zero
    wqi = wqi_numerator / wqi_denominator.replace(0.0, np.nan)
    # Bound reasonable display
    df["WQI"] = wqi.round(2)

    # Assign Quality Tier based on standard WAWQI scale
    def assign_wqi_grade(score):
        if pd.isna(score):
            return "Unassessed"
        elif score <= 25.0:
            return "Excellent (Grade A)"
        elif score <= 50.0:
            return "Good (Grade B)"
        elif score <= 75.0:
            return "Poor (Grade C)"
        elif score <= 100.0:
            return "Very Poor (Grade D)"
        else:
            return "Unsuitable / Highly Polluted (Grade E)"

    df["WQI_Category"] = df["WQI"].apply(assign_wqi_grade)
    df["CPCB_Designated_Class"] = df.apply(classify_cpcb_designated_best_use, axis=1)

    return df


def assess_water_quality(df: pd.DataFrame = None, save_path: str = "data/processed/water_quality_assessed.csv") -> pd.DataFrame:
    """Runs end-to-end water quality assessment and persists assessed dataframe."""
    if df is None:
        features_path = "data/processed/features.csv"
        if os.path.exists(features_path):
            df = pd.read_csv(features_path)
        else:
            from src.features import engineer_features
            df = engineer_features()

    df_assessed = calculate_wawqi(df)

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        df_assessed.to_csv(save_path, index=False)
        print(f"Assessed water quality saved to: {save_path}")

    return df_assessed


if __name__ == "__main__":
    df_assessed = assess_water_quality()
    print("Assessment Summary:")
    print("WQI Stats:\n", df_assessed["WQI"].describe())
    print("\nWQI Category Distribution:\n", df_assessed["WQI_Category"].value_counts())
    print("\nCPCB Designated Class Distribution:\n", df_assessed["CPCB_Designated_Class"].value_counts())
