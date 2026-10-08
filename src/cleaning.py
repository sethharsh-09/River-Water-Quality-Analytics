"""
Data Cleaning and Preprocessing Module for River Water Quality Analytics System
Handles:
- String artifact conversion ('-', 'BDL', 'nil', blanks to NaN)
- Robust numeric parsing including newline broken values
- Exact duplicate removal
- Outlier handling (safe bounding and capping without deleting rows)
- Standardizing State and Location text
"""

import os
import re
import numpy as np
import pandas as pd
from src.data_loader import load_raw_data

# Comprehensive State Name Normalization Mapping
STATE_MAPPING = {
    "ANDHRA\n PRADESH": "ANDHRA PRADESH",
    "ANDHRA PRADESH": "ANDHRA PRADESH",
    "Andhra Pradesh": "ANDHRA PRADESH",
    "ARUNACHAL\n PRADESH": "ARUNACHAL PRADESH",
    "ARUNACHAL PRADESH": "ARUNACHAL PRADESH",
    "ASSAM": "ASSAM",
    "BIHAR": "BIHAR",
    "CHATTISGARH": "CHHATTISGARH",
    "CHHATTISGARH": "CHHATTISGARH",
    "CPCB, DELHI": "DELHI",
    "DELHI": "DELHI",
    "GUJARAT": "GUJARAT",
    "HARYANA": "HARYANA",
    "HIMACHAL\n PRADESH": "HIMACHAL PRADESH",
    "HIMACHAL PRADESH": "HIMACHAL PRADESH",
    "INTER-STATE": "INTER-STATE",
    "JAMMU &\n KASHMIR": "JAMMU & KASHMIR",
    "JAMMU & KASHMIR": "JAMMU & KASHMIR",
    "JHARKHA\n ND": "JHARKHAND",
    "JHARKHA ND": "JHARKHAND",
    "JHARKHAND": "JHARKHAND",
    "Jharkhand": "JHARKHAND",
    "KARNATAKA": "KARNATAKA",
    "RD_BANGALORE": "KARNATAKA",
    "KERALA": "KERALA",
    "MADHYA\n PRADESH": "MADHYA PRADESH",
    "MADHYA PRADESH": "MADHYA PRADESH",
    "MAHARASHTRA": "MAHARASHTRA",
    "MANIPUR": "MANIPUR",
    "MEGHALAYA": "MEGHALAYA",
    "MIZORAM": "MIZORAM",
    "NAGALAND": "NAGALAND",
    "ODIS-HA": "ODISHA",
    "ODISHA": "ODISHA",
    "ORISSA": "ODISHA",
    "Odisha": "ODISHA",
    "PUDUCHERRY": "PUDUCHERRY",
    "PUNJAB": "PUNJAB",
    "RAJASTHA N": "RAJASTHAN",
    "RAJASTHAN": "RAJASTHAN",
    "SIKKIM": "SIKKIM",
    "TAMIL\n NADU": "TAMIL NADU",
    "TAMIL NADU": "TAMIL NADU",
    "TAMILNADU": "TAMIL NADU",
    "TELANGANA": "TELANGANA",
    "TRIPURA": "TRIPURA",
    "UTTAR\n PRADESH": "UTTAR PRADESH",
    "UTTAR PRADESH": "UTTAR PRADESH",
    "UTTARAKH\n AND": "UTTARAKHAND",
    "UTTARAKH AND": "UTTARAKHAND",
    "UTTARAKHAND": "UTTARAKHAND",
    "WEST\n BENGAL": "WEST BENGAL",
    "WEST BENGAL": "WEST BENGAL",
    "-": np.nan,
}


def parse_numeric_cell(val):
    """
    Robust cell-level parsing:
    - Replaces missing indicator tokens ('-', 'BDL', 'nil', etc.) with NaN.
    - Strips whitespace and embedded newlines ('76-\\n 00' -> 7600).
    - Repairs typo prefixes/suffixes ('.1.4' -> 1.4, '0..' -> 0.0).
    - Converts valid scientific notation and decimal strings to float.
    """
    if pd.isna(val):
        return np.nan
    s = str(val).strip()

    # Known placeholder tokens for missing / below detection limit / unmeasured
    missing_tokens = {
        "-", "--", "---", "_", ".", "nil", "Nil", "NIL",
        "bdl", "BDL", "Bdl", "nd", "ND", "Nd", "", "nan", "NaN", "null", "NULL", "NA", "N/A"
    }
    if s in missing_tokens:
        return np.nan

    # Clean embedded newlines, carriage returns, spaces
    s = s.replace("\n", "").replace("\r", "").replace(" ", "")

    # Handle line-break hyphenations like '76-00' -> '7600' or '1-586' -> '1586'
    if re.match(r"^\d+-\d+$", s):
        s = s.replace("-", "")

    # Fix typo patterns
    if s.startswith("."):
        parts = s.split(".")
        if len(parts) >= 2:
            s = parts[1] + ("." + parts[2] if len(parts) > 2 else "")
    if s.endswith(".."):
        s = s[:-1]

    try:
        val_float = float(s)
        return val_float
    except ValueError:
        return np.nan


def clean_state(val):
    """Standardizes State names, removing newlines and mapping synonyms."""
    if pd.isna(val):
        return np.nan
    s = str(val).strip()
    if s in STATE_MAPPING:
        return STATE_MAPPING[s]
    # Clean newlines and double spaces as general fallback
    s_clean = re.sub(r"\s+", " ", s.replace("\n", " ")).strip().upper()
    return STATE_MAPPING.get(s_clean, s_clean if s_clean != "-" else np.nan)


def clean_location(val):
    """Cleans location text, stripping newlines and excessive whitespace."""
    if pd.isna(val):
        return "UNKNOWN"
    s = str(val).strip()
    s = re.sub(r"\s+", " ", s.replace("\n", " ")).strip()
    return s if s not in ["-", ""] else "UNKNOWN"


def cap_physical_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Safely caps physical and chemical outliers according to domain principles
    without dropping rows, as explicitly instructed in the project plan.
    """
    df = df.copy()

    # Temperature (°C): River surface water typically 0°C to 50°C.
    # Correct obvious 10x multiplier typos (e.g. 269 -> 26.9)
    for col in ["Temperature (C) Min", "Temperature (C) Max"]:
        if col in df.columns:
            # If temp > 100, likely entered without decimal point (e.g. 269 -> 26.9)
            df[col] = df[col].apply(lambda x: x / 10.0 if (pd.notna(x) and x > 100.0) else x)
            df[col] = df[col].clip(lower=0.0, upper=50.0)

    # pH: Universal chemical scale [0.0, 14.0]
    for col in ["pH Min", "pH Max"]:
        if col in df.columns:
            # If pH > 100, e.g. 1480 or 750, likely missing decimal point
            df[col] = df[col].apply(lambda x: x / 100.0 if (pd.notna(x) and x > 100.0) else (
                x / 10.0 if (pd.notna(x) and x > 14.0) else x
            ))
            df[col] = df[col].clip(lower=0.0, upper=14.0)

    # Dissolved Oxygen (mg/L): Saturation upper bound ~25.0 mg/L; non-negative
    for col in ["Dissolved Oxygen (mg/L) Min", "Dissolved Oxygen (mg/L) Max"]:
        if col in df.columns:
            df[col] = df[col].clip(lower=0.0, upper=25.0)

    # BOD (mg/L): Non-negative; cap extreme erroneous spikes at 500 mg/L
    for col in ["BOD (mg/L) Min", "BOD (mg/L) Max"]:
        if col in df.columns:
            df[col] = df[col].clip(lower=0.0, upper=500.0)

    # Conductivity (umho/cm): Non-negative; cap extreme outliers at 50,000 umho/cm
    for col in ["Conductivity (umho/cm) Min", "Conductivity (umho/cm) Max"]:
        if col in df.columns:
            df[col] = df[col].clip(lower=0.0, upper=50000.0)

    # Nitrate N (mg/L): Non-negative; cap extreme spikes at 250 mg/L
    for col in ["Nitrate N (mg/L) Min", "Nitrate N (mg/L) Max"]:
        if col in df.columns:
            df[col] = df[col].clip(lower=0.0, upper=250.0)

    # Coliforms (MPN/100ml): Non-negative
    coliform_cols = [
        "Fecal Coliform (MPN/100ml) Min", "Fecal Coliform (MPN/100ml) Max",
        "Total Coliform (MPN/100ml) Min", "Total Coliform (MPN/100ml) Max",
        "Fecal Streptococci (MPN/100ml) Min", "Fecal Streptococci (MPN/100ml) Max"
    ]
    for col in coliform_cols:
        if col in df.columns:
            df[col] = df[col].clip(lower=0.0)

    return df


def clean_dataset(df_raw: pd.DataFrame = None, save_path: str = "data/processed/cleaned_data.csv") -> pd.DataFrame:
    """
    Executes full data cleaning pipeline:
    1. Loads raw dataset if not provided.
    2. Drops exact duplicates.
    3. Standardizes State and Monitoring Location strings.
    4. Converts measurement columns to numeric with cell-level parser.
    5. Safely handles outliers via physical bounding and capping.
    6. Saves cleaned dataset to disk.
    """
    if df_raw is None:
        df_raw = load_raw_data()

    initial_count = len(df_raw)
    df = df_raw.copy()

    # Step A: Drop exact duplicates
    df = df.drop_duplicates().reset_index(drop=True)
    dedup_count = len(df)
    duplicates_removed = initial_count - dedup_count

    # Step B: Standardize Categorical Columns
    if "State" in df.columns:
        df["State"] = df["State"].apply(clean_state)
    if "Monitoring Location" in df.columns:
        df["Monitoring Location"] = df["Monitoring Location"].apply(clean_location)
    if "Station Code" in df.columns:
        df["Station Code"] = df["Station Code"].astype(str).str.strip()

    # Step C: Parse Numeric Measurement Columns
    meta_cols = {"Station Code", "Monitoring Location", "State", "Year"}
    meas_cols = [c for c in df.columns if c not in meta_cols]

    for col in meas_cols:
        df[col] = df[col].apply(parse_numeric_cell)

    # Step D: Cap physical/chemical outliers safely
    df = cap_physical_outliers(df)

    # Ensure Year is integer
    if "Year" in df.columns:
        df["Year"] = pd.to_numeric(df["Year"], errors="coerce").fillna(0).astype(int)

    # Save to disk
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        df.to_csv(save_path, index=False)
        print(f"Cleaned data successfully saved to: {save_path}")

    print(f"Cleaning Complete: Initial {initial_count} rows -> {dedup_count} rows ({duplicates_removed} duplicates removed).")
    return df


if __name__ == "__main__":
    df_cleaned = clean_dataset()
    print("Cleaned Dataset Head:")
    print(df_cleaned.head(3))
    print("\nNon-null counts:")
    print(df_cleaned.notna().sum())
