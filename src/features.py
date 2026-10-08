"""
Feature Engineering Module for River Water Quality Analytics System
Handles:
- Average and Range calculation from Min/Max parameters (DO, pH, BOD, Temp, Conductivity, Nitrate, Coliforms)
- Mathematical and domain features (Log transforms for microbiological counts, Nutrient ratios)
- Metadata features (State, Location, Station Code, Year, Decade/Period bins)
"""

import os
import sys
import numpy as np
import pandas as pd

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.cleaning import clean_dataset


def compute_avg_and_range(df: pd.DataFrame, min_col: str, max_col: str, prefix: str):
    """
    Computes:
    - {prefix}_Avg: Average of Min and Max. If one is missing, uses the other.
    - {prefix}_Range: Max - Min. If either is missing, NaN (or 0 if both equal).
    """
    if min_col not in df.columns or max_col not in df.columns:
        return df

    # Vectorized computation
    c_min = df[min_col]
    c_max = df[max_col]

    # Average: when both present -> (min + max) / 2; when one present -> that value
    avg_series = (c_min + c_max) / 2.0
    avg_series = avg_series.fillna(c_min).fillna(c_max)

    # Range: max - min (clip to >= 0 in case of sensor order inversion)
    range_series = (c_max - c_min).abs()

    df[f"{prefix}_Avg"] = avg_series
    df[f"{prefix}_Range"] = range_series
    return df


def engineer_features(df: pd.DataFrame = None, save_path: str = "data/processed/features.csv") -> pd.DataFrame:
    """
    Extracts comprehensive engineered features as required by the project specification.
    """
    if df is None:
        cleaned_path = "data/processed/cleaned_data.csv"
        if os.path.exists(cleaned_path):
            df = pd.read_csv(cleaned_path)
        else:
            df = clean_dataset()

    df = df.copy()

    # 1. Parameter Average and Range Features
    param_pairs = [
        ("Temperature (C) Min", "Temperature (C) Max", "Temp"),
        ("Dissolved Oxygen (mg/L) Min", "Dissolved Oxygen (mg/L) Max", "DO"),
        ("pH Min", "pH Max", "pH"),
        ("Conductivity (umho/cm) Min", "Conductivity (umho/cm) Max", "Conductivity"),
        ("BOD (mg/L) Min", "BOD (mg/L) Max", "BOD"),
        ("Nitrate N (mg/L) Min", "Nitrate N (mg/L) Max", "Nitrate"),
        ("Fecal Coliform (MPN/100ml) Min", "Fecal Coliform (MPN/100ml) Max", "Fecal_Coliform"),
        ("Total Coliform (MPN/100ml) Min", "Total Coliform (MPN/100ml) Max", "Total_Coliform"),
        ("Fecal Streptococci (MPN/100ml) Min", "Fecal Streptococci (MPN/100ml) Max", "Fecal_Streptococci"),
    ]

    for min_c, max_c, prefix in param_pairs:
        df = compute_avg_and_range(df, min_c, max_c, prefix)

    # 2. Log-transformed Coliform features (microbial counts vary over orders of magnitude)
    if "Total_Coliform_Avg" in df.columns:
        df["Log_Total_Coliform"] = np.log10(df["Total_Coliform_Avg"].clip(lower=0) + 1.0)
    if "Fecal_Coliform_Avg" in df.columns:
        df["Log_Fecal_Coliform"] = np.log10(df["Fecal_Coliform_Avg"].clip(lower=0) + 1.0)

    # 3. DO Saturation Deficit proxy: standard saturation DO is ~8.5 mg/L at 25°C
    if "DO_Avg" in df.columns:
        df["DO_Deficit"] = (8.5 - df["DO_Avg"]).clip(lower=0.0)

    # 4. Organic to Nutrient ratio
    if "BOD_Avg" in df.columns and "Nitrate_Avg" in df.columns:
        df["BOD_to_Nitrate_Ratio"] = df["BOD_Avg"] / (df["Nitrate_Avg"] + 0.1)

    # 5. Temporal Features
    if "Year" in df.columns:
        df["Period_Bin"] = pd.cut(
            df["Year"],
            bins=[2011, 2015, 2019, 2024],
            labels=["2012-2015", "2016-2019", "2020-2023"],
            right=True
        )

    # Save to disk
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        df.to_csv(save_path, index=False)
        print(f"Features saved successfully to: {save_path}")

    return df


if __name__ == "__main__":
    df_feat = engineer_features()
    print("Engineered Features Shape:", df_feat.shape)
    new_cols = [c for c in df_feat.columns if "_Avg" in c or "_Range" in c or "Log_" in c]
    print("New Engineered Columns:", new_cols)
    print("\nSample Engineered Head:")
    print(df_feat[new_cols[:8]].head(3))
