# River Water Quality Analytics System: Technical Project Report

**Author / Project:** River Water Quality Analytics System  
**Dataset:** `RiverWaterQualityOverYears.csv` (Central Pollution Control Board River Monitoring Network)  
**Standard Benchmarks:** Central Pollution Control Board (CPCB) Designated Best Use Criteria & BIS 10500:2012  

---

## Executive Summary

River ecosystems across India face severe multi-dimensional stress from untreated domestic sewage discharge, municipal solid waste, and industrial effluents. This project implements a comprehensive, end-to-end data science and machine learning analytics platform to audit, clean, engineer features, evaluate spatial-temporal water quality trends (2012–2023), calculate regulatory compliance indices (CPCB Designated Best Use Classes A–E and Weighted Arithmetic WQI), and train zero-data-leakage machine learning models to predict river organic degradation (Biochemical Oxygen Demand, BOD).

The platform integrates an automated Python processing pipeline (`src/`), 8 reproducible Jupyter notebooks (`notebooks/`), diagnostic and explainability visualizations (`visualizations/`), and an interactive 9-page Streamlit web dashboard (`dashboard/`).

---

## 1. Data Understanding & Audit

### 1.1 Dataset Geometry & Schema
The raw dataset consists of **10,006 records** across **22 columns**, capturing water quality metrics across hundreds of monitoring stations from 2012 to 2023.

| Characteristic | Raw State | Processed State | Remarks |
| :--- | :--- | :--- | :--- |
| **Total Rows** | 10,006 | 9,644 | 362 exact duplicate rows removed |
| **Columns** | 22 | 45 | Includes 23 engineered features |
| **Data Types** | 21 Object, 1 Int64 | Cleaned Floats, Strings, Categoricals | Encoded numbers restored to `float64` |
| **Year Span** | 2012–2023 | 2012–2023 | 10 unique monitoring years |
| **State Entities** | 54 unique raw strings | 30 normalized States/UTs | Removed embedded newlines and typos |

### 1.2 Identified Data Quality Anomalies
1. **Placeholder Tokens:** Measurements contained strings such as `'-'`, `'--'`, `'_'`, `'BDL'` (Below Detection Limit), `'nil'`, and `'ND'` (Not Detected).
2. **Text Formatting Glitches:** Numbers broken across newlines (e.g., `'76-\n 00'` instead of `7600`, `'13000\n 00'` instead of `1300000`).
3. **Data Entry Typos:** Missing decimal points in physical measurements (e.g., `Temperature Max = 269°C` instead of `26.9°C`, `pH Max = 1480` instead of `14.8` or `7.4`).

---

## 2. Data Cleaning & Preprocessing

As strictly outlined in the project specifications, cleaning was executed systematically:
1. **Cell-Level Parsing:** Placeholders (`BDL`, `nil`, `-`) converted to `NaN`. Newline breaks and hyphenations safely repaired.
2. **Exact Duplicate Elimination:** 362 duplicate rows were removed, retaining 9,644 unique records.
3. **Categorical Harmonization:** A comprehensive mapping table resolved all variations of state names (e.g., `ANDHRA\n PRADESH`, `WEST\n BENGAL`, `ODIS-HA`, `CPCB, DELHI`).
4. **Domain-Safe Outlier Handling:**
   - Rather than dropping rows and destroying observational history, safe domain physical bounds were established:
   - Surface water temperature capped to $[0^\circ\text{C}, 50^\circ\text{C}]$.
   - pH bounded to the chemical scale $[0.0, 14.0]$.
   - Dissolved Oxygen (DO) capped at physical saturation limit ($25.0\text{ mg/L}$).
   - BOD capped at $500\text{ mg/L}$; Conductivity capped at $50,000\text{ }\mu\text{mho/cm}$.

---

## 3. Feature Engineering

To capture central tendencies and seasonal volatility, paired parameter measurements were expanded into domain features:
- **Average Metrics ($\text{Avg}$):** $\text{Parameter\_Avg} = \frac{\text{Min} + \text{Max}}{2}$
- **Range Metrics ($\text{Range}$):** $\text{Parameter\_Range} = |\text{Max} - \text{Min}|$
- **Microbiological Log-Transforms:** Coliform bacteria span 6 orders of magnitude ($10^1$ to $10^7\text{ MPN/100ml}$); transformed as $\log_{10}(\text{Coliform} + 1)$.
- **DO Deficit:** Proxy indicator measuring deficit below standard saturation ($\max(0, 8.5 - \text{DO\_Avg})$).
- **Nutrient-to-Organic Ratio:** $\frac{\text{BOD\_Avg}}{\text{Nitrate\_Avg} + 0.1}$.

---

## 4. Exploratory & Temporal Analysis

### 4.1 Statistical Distribution & Correlation
- **DO vs. BOD:** Statistically significant negative correlation ($r = -0.32$), demonstrating that microbial catabolism of organic waste rapidly exhausts dissolved oxygen.
- **Coliform vs. BOD:** Highly positive correlation ($r > 0.40$), identifying domestic untreated municipal wastewater as the primary source of biological oxygen demand in Indian rivers.

### 4.2 Decadal Trends (2012 vs. 2023)
- Nationwide median Dissolved Oxygen has maintained stability around $6.8\text{--}7.2\text{ mg/L}$, indicative of river assimilation capacity during monsoon flows.
- BOD showed elevated national medians during 2017–2019 before stabilizing to $2.3\text{--}2.6\text{ mg/L}$ in recent years (2021–2023), reflecting commissioned Sewage Treatment Plant (STP) capacity under the Namami Gange and National River Conservation Plan.

---

## 5. Regulatory Water Quality Assessment

### 5.1 CPCB Designated Best Use Classification
River samples were assessed against the official CPCB statutory criteria:
- **Class A (Drinking w/o conventional treatment):** 1,249 samples (12.9%)
- **Class B (Outdoor Bathing):** 2,128 samples (22.1%)
- **Class C (Drinking after conventional treatment):** 2,240 samples (23.2%)
- **Class D (Wildlife & Fisheries):** 2,459 samples (25.5%)
- **Class E (Irrigation & Industrial Cooling):** 724 samples (7.5%)
- **Below-Class E (Critically Polluted / Hypoxic):** 844 samples (8.8%)

### 5.2 Weighted Arithmetic WQI (WAWQI)
The WAWQI aggregates sub-indices weighted inversely by BIS 10500 permissible standard limits ($S_i$):
- **Grade A (Excellent, 0–25):** 0.3%
- **Grade B (Good, 26–50):** 15.8%
- **Grade C (Poor, 51–75):** 47.3%
- **Grade D (Very Poor, 76–100):** 16.6%
- **Grade E (Unsuitable / Highly Polluted, >100):** 20.0%

---

## 6. Machine Learning Architecture & Model Benchmark

### 6.1 Target Selection & Prevention of Data Leakage
- **Target:** `BOD_Avg` (mg/L).
- **Leakage Prevention:** To prevent trivial target reconstruction, `BOD Min`, `BOD Max`, `BOD Range`, and derived indices (`WQI`, `CPCB Class`) were **strictly excluded** from feature matrix $X$.
- **Split Protocol:** Temporal split—older records (2012–2020, 5,182 samples) formed the training set; recent records (2021–2023, 4,109 samples) formed the test set.

### 6.2 Model Comparison Leaderboard

| Model | Train RMSE | Test RMSE | Train MAE | Test MAE | Train $R^2$ | Test $R^2$ | CV RMSE (5-Fold) | Train-Test Gap |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Random Forest (Tuned)** 🏆 | **4.2969** | **6.4811** | **1.2301** | **2.0903** | **0.8596** | **0.5153** | **7.4871** | **0.3444** |
| Random Forest (Default) | 3.7689 | 6.7371 | 1.2304 | 2.2052 | 0.8920 | 0.4762 | 7.6695 | 0.4158 |
| Gradient Boosting | 2.2373 | 7.0976 | 1.1648 | 2.3044 | 0.9619 | 0.4187 | 7.6223 | 0.5433 |
| XGBoost (Tuned) | 2.7518 | 7.2226 | 1.3061 | 2.3404 | 0.9424 | 0.3980 | 6.8373 | 0.5444 |
| Ridge Regression | 9.6172 | 7.4587 | 3.9071 | 3.5199 | 0.2969 | 0.3580 | 9.7273 | 0.0611 |
| Linear Regression (Baseline) | 9.6144 | 7.4977 | 3.9515 | 3.5945 | 0.2973 | 0.3513 | 9.7819 | 0.0540 |
| XGBoost (Default) | 2.5363 | 7.7104 | 1.2260 | 2.3646 | 0.9511 | 0.3140 | 7.3692 | 0.6371 |
| Decision Tree | 3.8091 | 9.2612 | 1.6671 | 2.5559 | 0.8897 | 0.0102 | 9.8104 | 0.8795 |

### 6.3 Explainability via SHAP & Feature Importances
- **Primary Driver:** `Log_Total_Coliform` and `Log_Fecal_Coliform` accounted for $> 45\%$ of total feature importance, demonstrating that microbiological contamination is the single strongest precursor to organic oxygen demand.
- **Secondary Driver:** `DO_Avg` and `DO_Deficit` contributed strongly negative SHAP impacts; low DO values directly identify high BOD loads.
- **Geography:** State indicator variables capture regional disparity in treatment infrastructure and industrial density.

---

## 7. Conclusions & Strategic Recommendations

1. **Targeted Sewage Interception:** Sewage interception and diversion networks must prioritize municipal drains discharging directly into Class D and Below-E river stretches.
2. **Real-Time Sensor Deployments:** Install optical continuous Dissolved Oxygen and Electrical Conductivity probes at 10 km intervals along vulnerable river reaches.
3. **Environmental Flow (E-Flow) Enforcement:** Mandate minimum discharge thresholds from upstream barrages during lean dry months (March to May) to preserve natural oxygen replenishment.
