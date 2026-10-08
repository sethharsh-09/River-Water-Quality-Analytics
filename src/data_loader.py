"""
Data Loader Module for River Water Quality Analytics System
Handles robust loading of raw CSV dataset and standardizes column names.
"""

import os
import re
import pandas as pd


def clean_column_name(col_name: str) -> str:
    """
    Cleans raw column names by:
    - Stripping leading/trailing whitespace
    - Removing non-ASCII corrupted characters
    - Normalizing internal spaces
    - Using clean ASCII representation for units: Temperature (C), Conductivity (umho/cm)
    """
    col = str(col_name).strip()
    # Remove non-ascii characters (like corrupted symbols)
    col = re.sub(r"[^\x00-\x7F]+", "", col)
    # Collapse multiple whitespace characters into single space
    col = re.sub(r"\s+", " ", col).strip()

    # Normalize unit naming cleanly
    col = col.replace("Temperature () Min", "Temperature (C) Min")
    col = col.replace("Temperature () Max", "Temperature (C) Max")
    col = col.replace("Temperature (C) Min", "Temperature (C) Min")
    col = col.replace("Temperature (C) Max", "Temperature (C) Max")
    col = col.replace("Conductivity () Min", "Conductivity (umho/cm) Min")
    col = col.replace("Conductivity () Max", "Conductivity (umho/cm) Max")
    col = col.replace("Conductivity (mho/cm) Min", "Conductivity (umho/cm) Min")
    col = col.replace("Conductivity (mho/cm) Max", "Conductivity (umho/cm) Max")

    return col.strip()


def load_raw_data(filepath: str = "data/raw/RiverWaterQualityOverYears.csv") -> pd.DataFrame:
    """
    Loads raw CSV data with automatic encoding fallback and cleaned column names.

    Args:
        filepath: Path to the raw CSV file.

    Returns:
        pd.DataFrame with cleaned column headers and preserved raw row values.
    """
    if not os.path.exists(filepath):
        alt_paths = [
            os.path.join(os.path.dirname(__file__), "..", filepath),
            r"C:\Users\harsh\Downloads\RiverWaterQualityOverYears (1).csv",
            "RiverWaterQualityOverYears.csv"
        ]
        found = False
        for p in alt_paths:
            if os.path.exists(p):
                filepath = p
                found = True
                break
        if not found:
            raise FileNotFoundError(f"Raw dataset could not be located at '{filepath}' or alternate paths.")

    # Try standard encodings
    encodings_to_try = ["utf-8", "latin1", "cp1252", "iso-8859-1"]
    df = None
    for enc in encodings_to_try:
        try:
            df = pd.read_csv(filepath, encoding=enc, low_memory=False)
            break
        except Exception:
            continue

    if df is None:
        raise ValueError(f"Failed to read CSV at {filepath} with tested encodings.")

    # Standardize column headers
    cleaned_columns = {col: clean_column_name(col) for col in df.columns}
    df = df.rename(columns=cleaned_columns)

    return df


if __name__ == "__main__":
    df_raw = load_raw_data()
    print(f"Loaded raw data successfully. Shape: {df_raw.shape}")
    print("Cleaned Columns:")
    for i, col in enumerate(df_raw.columns, 1):
        print(f"  {i}. '{col}'")
