"""
Jupyter Notebook Generator for River Water Quality Analytics System
Generates the 8 structured notebooks required by the project specifications:
01_data_understanding.ipynb
02_data_cleaning.ipynb
03_feature_engineering.ipynb
04_eda_visualization.ipynb
05_temporal_location_analysis.ipynb
06_water_quality_assessment.ipynb
07_model_training_evaluation.ipynb
08_explainability_forecasting.ipynb
"""

import json
import os

NOTEBOOKS_DIR = "notebooks"
os.makedirs(NOTEBOOKS_DIR, exist_ok=True)


def make_notebook(cells):
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.12"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }


def md_cell(text):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in text.strip().split("\n")]
    }


def code_cell(code):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in code.strip().split("\n")]
    }


# ==========================================
# Notebook 1: Data Understanding & Audit
# ==========================================
nb1_cells = [
    md_cell("""# Step 1: Data Understanding & Audit
### River Water Quality Analytics System
**Dataset:** `RiverWaterQualityOverYears.csv`

---
### Objectives:
1. Load the raw dataset and inspect the dimensions, column names, and data types.
2. Identify initial missing values, placeholders (`-`, `BDL`, `nil`, blanks), and encoding anomalies.
3. Quantify duplicate records.
4. Audit temporal range (years), geographic coverage (States), and monitoring stations.
"""),
    code_cell("""import os
import sys
import pandas as pd
import numpy as np

# Ensure project root is in path
sys.path.insert(0, os.path.abspath('..'))

from src.data_loader import load_raw_data

# Load raw dataset with cleaned headers
df_raw = load_raw_data('../data/raw/RiverWaterQualityOverYears.csv')
print(f"Dataset Shape: {df_raw.shape[0]} rows, {df_raw.shape[1]} columns")
df_raw.head()
"""),
    md_cell("""### 1.1 Data Schema and Types
Notice that although most measurement columns represent physical/chemical values, pandas infers `object` (string) dtype due to non-numeric tokens.
"""),
    code_cell("""print("Column Data Types:")
print(df_raw.dtypes)
"""),
    md_cell("""### 1.2 Temporal and Geographic Coverage
Audit the range of monitoring years and Indian states represented.
"""),
    code_cell("""print("Years covered:", sorted(df_raw['Year'].dropna().unique().tolist()))
print(f"Total Unique States recorded: {df_raw['State'].nunique()}")
print("Sample States:", df_raw['State'].dropna().unique()[:15])
"""),
    md_cell("""### 1.3 Identification of Non-Numeric Placeholders
We inspect non-numeric tokens present in measurement columns (`BDL`, `-`, `nil`, newline glitches).
"""),
    code_cell("""meas_cols = [c for c in df_raw.columns if c not in ['Station Code', 'Monitoring Location', 'State', 'Year']]
print(f"Number of Measurement Columns: {len(meas_cols)}")

sample_tokens = {}
for col in meas_cols[:5]:
    tokens = df_raw[col].dropna().astype(str).str.strip().unique()
    non_numeric = [t for t in tokens if not t.replace('.', '', 1).isdigit()][:5]
    sample_tokens[col] = non_numeric

print("Sample non-numeric placeholders detected:")
for col, toks in sample_tokens.items():
    print(f" - {col}: {toks}")
"""),
    md_cell("""### 1.4 Duplicate Audit
Check for exact duplicate rows.
"""),
    code_cell("""dup_count = df_raw.duplicated().sum()
print(f"Exact Duplicate Rows Detected: {dup_count} ({(dup_count / len(df_raw) * 100):.2f}%)")
""")
]

# ==========================================
# Notebook 2: Data Cleaning & Preprocessing
# ==========================================
nb2_cells = [
    md_cell("""# Step 2: Data Cleaning & Preprocessing
### River Water Quality Analytics System

---
### Key Tasks:
1. Convert placeholders (`-`, `BDL`, `nil`, `ND`) and malformed text entries to `NaN`.
2. Parse numerical values including newline-broken numbers (e.g., `'76-\\n 00'` -> `7600`).
3. Deduplicate exact duplicate rows.
4. Standardize State and Monitoring Location strings.
5. Handle physical/chemical outliers safely via capping without dropping large parts of the dataset.
"""),
    code_cell("""import os
import sys
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath('..'))
from src.cleaning import clean_dataset

# Execute modular cleaning pipeline
df_cleaned = clean_dataset(save_path='../data/processed/cleaned_data.csv')
print(f"Cleaned Data Dimensions: {df_cleaned.shape}")
df_cleaned.head(3)
"""),
    md_cell("""### 2.1 Post-Cleaning Non-Null Audits
Verify that all measurement columns are now numeric (`float64`).
"""),
    code_cell("""meas_cols = [c for c in df_cleaned.columns if c not in ['Station Code', 'Monitoring Location', 'State', 'Year']]
print("Cleaned Data Types:")
print(df_cleaned[meas_cols].dtypes.value_counts())
"""),
    md_cell("""### 2.2 Standardized State Audit
Verify that State names no longer have newline characters or typos.
"""),
    code_cell("""unique_states = sorted(df_cleaned['State'].dropna().unique().tolist())
print(f"Cleaned States Count: {len(unique_states)}")
print("States list:")
for s in unique_states:
    print(f" - {s}")
"""),
    md_cell("""### 2.3 Outlier Capping Verification
Check min and max of physical variables (Temperature, pH, Dissolved Oxygen).
"""),
    code_cell("""summary = df_cleaned[['Temperature (C) Min', 'Temperature (C) Max', 'pH Min', 'pH Max', 'Dissolved Oxygen (mg/L) Min', 'Dissolved Oxygen (mg/L) Max']].describe().T
summary[['min', 'mean', '50%', 'max']]
""")
]

# ==========================================
# Notebook 3: Feature Engineering
# ==========================================
nb3_cells = [
    md_cell("""# Step 3: Feature Engineering
### River Water Quality Analytics System

---
### Objectives:
1. Compute **Average** and **Range** features for all key parameters:
   - DO, pH, BOD, Temperature, Conductivity, Nitrate, Coliforms.
   - $\\text{Avg} = \\frac{\\text{Min} + \\text{Max}}{2}$, $\\text{Range} = |\\text{Max} - \\text{Min}|$
2. Calculate log-transforms for microbiological counts ($\\log_{10}(\\text{Coliform} + 1)$).
3. Compute domain ratios: DO Deficit, BOD-to-Nitrate ratio.
4. Extract temporal period bins.
"""),
    code_cell("""import os
import sys
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath('..'))
from src.features import engineer_features

df_features = engineer_features(save_path='../data/processed/features.csv')
print("Total Features Created:", df_features.shape[1])
df_features.head(3)
"""),
    md_cell("""### 3.1 Verification of Engineered Average and Range Features"""),
    code_cell("""avg_cols = [c for c in df_features.columns if '_Avg' in c]
range_cols = [c for c in df_features.columns if '_Range' in c]
print("Average Features:", avg_cols)
print("Range Features:", range_cols)
"""),
    md_cell("""### 3.2 Summary Statistics of Engineered Features"""),
    code_cell("""df_features[['DO_Avg', 'BOD_Avg', 'pH_Avg', 'Conductivity_Avg', 'Nitrate_Avg', 'Log_Total_Coliform']].describe().T
""")
]

# ==========================================
# Notebook 4: Exploratory Data Analysis (EDA)
# ==========================================
nb4_cells = [
    md_cell("""# Step 4: Exploratory Data Analysis (EDA)
### River Water Quality Analytics System

---
### Objectives:
1. Examine statistical distributions and skewness of water quality parameters.
2. Evaluate Pearson correlations across chemical and biological indicators.
3. Identify multi-collinearity and key environmental relationships.
"""),
    code_cell("""import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style='whitegrid')
df = pd.read_csv('../data/processed/features.csv')
df.shape
"""),
    md_cell("""### 4.1 Parameter Distributions"""),
    code_cell("""fig, axes = plt.subplots(2, 3, figsize=(15, 8))
params = ['DO_Avg', 'pH_Avg', 'BOD_Avg', 'Conductivity_Avg', 'Nitrate_Avg', 'Log_Total_Coliform']

for ax, col in zip(axes.flatten(), params):
    sns.histplot(df[col].dropna(), kde=True, ax=ax, bins=30, color='#1f77b4')
    ax.set_title(f'Distribution of {col}', fontweight='bold')
plt.tight_layout()
plt.show()
"""),
    md_cell("""### 4.2 Correlation Matrix Heatmap"""),
    code_cell("""corr_cols = ['DO_Avg', 'pH_Avg', 'BOD_Avg', 'Conductivity_Avg', 'Nitrate_Avg', 'Log_Total_Coliform', 'Temp_Avg']
corr_matrix = df[corr_cols].dropna().corr()

plt.figure(figsize=(9, 7))
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', vmin=-1, vmax=1)
plt.title('Correlation Heatmap of River Water Quality Parameters', fontweight='bold', fontsize=13)
plt.show()
"""),
    md_cell("""### 4.3 Key Findings:
- **DO vs. BOD**: Strongly inverse relationship (aerobic organic degradation consumes dissolved oxygen).
- **Coliform vs. BOD**: Positive correlation reflecting municipal sewage inputs.
""")
]

# ==========================================
# Notebook 5: Temporal & Location Analysis
# ==========================================
nb5_cells = [
    md_cell("""# Step 5: Temporal and Location Analysis
### River Water Quality Analytics System

---
### Objectives:
1. Track year-wise trends (2012–2023) across India's river monitoring network.
2. Compare 2012 baseline with 2023 recent status.
3. Compare states and identify high-risk river monitoring locations.
"""),
    code_cell("""import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style='whitegrid')
df = pd.read_csv('../data/processed/features.csv')
"""),
    md_cell("""### 5.1 Temporal Trajectories (2012–2023)"""),
    code_cell("""yearly = df[df['Year'] > 2000].groupby('Year')[['DO_Avg', 'BOD_Avg', 'pH_Avg', 'Nitrate_Avg']].median().reset_index()

fig, ax1 = plt.subplots(figsize=(10, 5))
ax1.plot(yearly['Year'], yearly['DO_Avg'], marker='o', label='Median DO (mg/L)', color='blue')
ax1.plot(yearly['Year'], yearly['pH_Avg'], marker='s', label='Median pH', color='green', linestyle='--')
ax1.set_ylabel('DO & pH')
ax1.set_xlabel('Year')

ax2 = ax1.twinx()
ax2.plot(yearly['Year'], yearly['BOD_Avg'], marker='^', label='Median BOD (mg/L)', color='red')
ax2.plot(yearly['Year'], yearly['Nitrate_Avg'], marker='d', label='Median Nitrate (mg/L)', color='orange', linestyle=':')
ax2.set_ylabel('BOD & Nitrate (mg/L)')

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
plt.title('Temporal Trajectory of Indian River Water Parameters (2012–2023)', fontweight='bold')
plt.show()
"""),
    md_cell("""### 5.2 State-Wise Pollution Hotspots (Median BOD)"""),
    code_cell("""top_states = df.groupby('State')['BOD_Avg'].median().dropna().sort_values(ascending=False).head(10)
plt.figure(figsize=(10, 5))
sns.barplot(x=top_states.values, y=top_states.index, palette='Reds_r')
plt.axvline(3.0, color='darkgreen', linestyle='--', label='CPCB Bathing Limit (3.0 mg/L)')
plt.title('Top 10 States with Highest Median River BOD', fontweight='bold')
plt.xlabel('Median BOD (mg/L)')
plt.legend()
plt.show()
""")
]

# ==========================================
# Notebook 6: Water Quality Assessment
# ==========================================
nb6_cells = [
    md_cell("""# Step 6: Water Quality Assessment
### River Water Quality Analytics System

---
### Standard Specifications:
1. **CPCB Designated Best Use Criteria**:
   - Class A: Drinking water without conventional treatment (DO >= 6.0, BOD <= 2.0, pH 6.5-8.5, TC <= 50)
   - Class B: Outdoor bathing (DO >= 5.0, BOD <= 3.0, pH 6.5-8.5, TC <= 500)
   - Class C: Drinking water with treatment (DO >= 4.0, BOD <= 3.0, pH 6.0-9.0, TC <= 5000)
   - Class D: Wildlife & Fisheries (DO >= 4.0, pH 6.5-8.5)
   - Class E: Irrigation & Industrial cooling (pH 6.0-8.5, EC <= 2250)
   - Below-E: Severely Polluted
2. **Weighted Arithmetic Water Quality Index (WAWQI)**:
   - Evaluates weighted normalized sub-indices against BIS/CPCB drinking water standards.
"""),
    code_cell("""import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.insert(0, os.path.abspath('..'))
from src.assessment import assess_water_quality

df_assessed = assess_water_quality(save_path='../data/processed/water_quality_assessed.csv')
print("Assessment Complete. Summary:")
print(df_assessed[['CPCB_Designated_Class', 'WQI_Category']].value_counts())
"""),
    md_cell("""### 6.1 Distribution of CPCB River Classes"""),
    code_cell("""plt.figure(figsize=(10, 5))
counts = df_assessed['CPCB_Designated_Class'].value_counts()
sns.barplot(x=counts.values, y=counts.index, palette='viridis')
plt.title('CPCB Designated Best Use Classification Distribution across Indian Rivers', fontweight='bold')
plt.xlabel('Sample Count')
plt.show()
"""),
    md_cell("""### 6.2 Distribution of WAWQI Quality Categories"""),
    code_cell("""plt.figure(figsize=(7, 7))
wqi_cat = df_assessed['WQI_Category'].value_counts()
wqi_cat = wqi_cat[wqi_cat.index != 'Unassessed']
plt.pie(wqi_cat.values, labels=wqi_cat.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette('pastel'))
plt.title('WAWQI Water Quality Grades Distribution', fontweight='bold')
plt.show()
""")
]

# ==========================================
# Notebook 7: Model Training & Evaluation
# ==========================================
nb7_cells = [
    md_cell("""# Step 7: Model Training & Evaluation
### River Water Quality Analytics System

---
### Machine Learning Problem Definition:
- **Target:** `BOD_Avg` (Biochemical Oxygen Demand in mg/L - primary index of organic river pollution).
- **Data Leakage Safeguard:** Min/Max and Range columns of BOD are **strictly removed** from the feature set $X$.
- **Preprocessing:** Pipeline with Median Imputation, Standard Scaling, and One-Hot Encoding for State.
- **Split:** Temporal Split (Train: 2012–2020; Test: 2021–2023).
- **Candidate Models:**
  1. Linear Regression (Baseline)
  2. Ridge Regression
  3. Decision Tree
  4. Random Forest
  5. Gradient Boosting
  6. XGBoost
- **Tuning:** GridSearchCV on top-performing ensemble architectures.
"""),
    code_cell("""import os
import sys
import pandas as pd
import numpy as np

# Load trained model comparison leaderboard
comp_df = pd.read_csv('../models/model_comparison.csv')
print("=== Model Performance Leaderboard ===")
comp_df
"""),
    md_cell("""### 7.1 Best Model Inspection"""),
    code_cell("""import joblib

model_artifact = joblib.load('../models/best_model.joblib')
print(f"Selected Champion Model: {model_artifact['model_name']}")
print("Test Performance Metrics:")
for k, v in model_artifact['metrics'].items():
    print(f" - {k}: {v}")
"""),
    md_cell("""### 7.2 Residual and Diagnostic Verification"""),
    code_cell("""import matplotlib.pyplot as plt
import seaborn as sns

pipeline = model_artifact['pipeline']
X_test = model_artifact['test_data']['X_test']
y_test = model_artifact['test_data']['y_test']

y_pred = pipeline.predict(X_test)
residuals = y_test - y_pred

plt.figure(figsize=(8, 5))
sns.scatterplot(x=y_pred, y=residuals, alpha=0.5, color='teal')
plt.axhline(0, color='red', linestyle='--')
plt.title(f"Residual Plot - {model_artifact['model_name']}", fontweight='bold')
plt.xlabel('Predicted BOD (mg/L)')
plt.ylabel('Residuals')
plt.show()
""")
]

# ==========================================
# Notebook 8: Explainability & Forecasting
# ==========================================
nb8_cells = [
    md_cell("""# Step 8: Explainability & Forecasting
### River Water Quality Analytics System

---
### Objectives:
1. Explain model predictions via Gini/Gain Feature Importance and SHAP (SHapley Additive exPlanations).
2. Quantify the relative influence of Dissolved Oxygen, Coliform, Nitrate, and State on river degradation.
3. Evaluate temporal forecast trends per state with scientific limitations explicitly documented.
"""),
    code_cell("""import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

model_artifact = joblib.load('../models/best_model.joblib')
pipeline = model_artifact['pipeline']
regressor = pipeline.named_steps['regressor']
preprocessor = pipeline.named_steps['preprocessor']

# Extract feature names
num_names = model_artifact['num_cols']
cat_names = list(preprocessor.named_transformers_['cat'].named_steps['onehot'].get_feature_names_out(model_artifact['cat_cols']))
all_features = num_names + cat_names

fi_df = pd.DataFrame({'Feature': all_features, 'Importance': regressor.feature_importances_})
fi_top = fi_df.sort_values(by='Importance', ascending=False).head(12)

plt.figure(figsize=(10, 5))
sns.barplot(data=fi_top, x='Importance', y='Feature', palette='mako')
plt.title(f"Top 12 Features Driving Predicted BOD ({model_artifact['model_name']})", fontweight='bold')
plt.xlabel('Feature Importance')
plt.show()
"""),
    md_cell("""### 8.1 SHAP Value Inspection"""),
    code_cell("""import shap

X_test = model_artifact['test_data']['X_test']
X_trans = preprocessor.transform(X_test)

explainer = shap.TreeExplainer(regressor, data=X_trans[:100])
shap_vals = explainer(X_trans[:200], check_additivity=False)
shap_vals.feature_names = all_features[:X_trans.shape[1]]

plt.figure(figsize=(10, 6))
shap.summary_plot(shap_vals, max_display=10, show=False)
plt.title("SHAP Summary Plot - Impact on River BOD Prediction", fontweight='bold')
plt.tight_layout()
plt.show()
"""),
    md_cell("""### 8.2 Historical Trajectory & Trend Limitations
*Note as specified in PDF Step 15:* Multi-year extrapolation must note that point-source sewage interventions and monsoon seasonal flow variations limit simple linear extrapolation. Long-term forecasting requires hydrodynamic river basin flow modeling.
""")
]

# Write all notebooks to disk
notebooks_map = {
    "01_data_understanding.ipynb": nb1_cells,
    "02_data_cleaning.ipynb": nb2_cells,
    "03_feature_engineering.ipynb": nb3_cells,
    "04_eda_visualization.ipynb": nb4_cells,
    "05_temporal_location_analysis.ipynb": nb5_cells,
    "06_water_quality_assessment.ipynb": nb6_cells,
    "07_model_training_evaluation.ipynb": nb7_cells,
    "08_explainability_forecasting.ipynb": nb8_cells,
}

for filename, cells in notebooks_map.items():
    nb_content = make_notebook(cells)
    filepath = os.path.join(NOTEBOOKS_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(nb_content, f, indent=2)
    print(f"Generated: {filepath}")

print("All 8 notebooks created successfully!")
