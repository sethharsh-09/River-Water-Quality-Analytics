# 🌊 River Water Quality Analytics — Complete Technical Guide & Documentation

This document contains the dedicated **Technical Documentation, Methodologies, Model Results, and User Guide** for the River Water Quality Analytics System.

---

## 1. Project Overview & Architecture
The **River Water Quality Analytics System** is an end-to-end environmental data science platform built on 10 years (2012–2023) of nationwide water monitoring observations published by the Central Pollution Control Board (CPCB), Ministry of Environment, Forest and Climate Change (MoEF&CC), Government of India.

The project integrates:
1. **Automated Cleaning & Ingestion:** Safe cell-level token parsing, deduplication, state standardization, and domain physical bounding.
2. **Domain Feature Engineering:** Construction of central tendency (Average) and fluctuation (Range) metrics, logarithmic microbial transformations, and nutrient-organic loading ratios.
3. **Statutory Water Quality Assessment:** Direct computation of official CPCB Designated Best Use Classes (Classes A through E & Below-E) and the Weighted Arithmetic Water Quality Index (WAWQI) aligned with Bureau of Indian Standards (BIS 10500:2012).
4. **Zero-Leakage Machine Learning:** Rigorous benchmarking of 6 regression architectures to forecast river Biochemical Oxygen Demand (BOD) using a prospective temporal split.
5. **Explainable AI (XAI):** SHAP (SHapley Additive exPlanations) and tree feature importance diagnostics identifying the biochemical precursors to aquatic hypoxia.
6. **Decision Support Dashboard:** 9-module interactive Streamlit application for spatial exploration and real-time prediction.

---

## 2. Dataset Description & Audit

### 2.1 Raw vs. Processed Dimensions
- **Raw File:** `data/raw/RiverWaterQualityOverYears.csv` (10,006 rows, 22 columns)
- **Processed File:** `data/processed/cleaned_data.csv` (9,644 rows, 22 columns)
- **Feature Set:** `data/processed/features.csv` (9,644 rows, 45 engineered features)
- **Assessed Set:** `data/processed/water_quality_assessed.csv` (9,644 rows, 48 features)
- **Duplicates Removed:** 362 exact duplicate rows.

### 2.2 Handled Data Anomalies
| Data Element | Raw Artifact | Handled Method | Safe Bounding Standard |
| :--- | :--- | :--- | :--- |
| **Missing Placeholders** | `'-'`, `'--'`, `'_'`, `'BDL'`, `'nil'`, `'ND'` | Converted to `NaN` using regex cell parser | Handled downstream via Median Imputation |
| **Number Formatting** | Embedded newlines (e.g. `'76-\n 00'`, `'13000\n 00'`) | Defragmented into valid continuous floats | Repaired to `7600.0`, `1300000.0` |
| **State Casing/Typos** | 54 inconsistent strings (`'ANDHRA\n PRADESH'`, `'ODIS-HA'`) | Standardized dictionary mapping | Normalized to 30 valid States/UTs |
| **pH Outliers** | Typo values up to 1480 | Fixed missing decimal separators | Bounded strictly to $[0.0, 14.0]$ |
| **Temperature** | Outliers up to 269°C | Corrected 10x multiplier typos | Bounded to surface water $[0.0, 50.0]^\circ\text{C}$ |
| **Dissolved Oxygen** | Sensor drops | Placeholder replacement | Capped at physical saturation limit ($25.0\text{ mg/L}$) |

---

## 3. Feature Engineering Details
The feature matrix was expanded from 22 raw columns to **45 high-information features**:
1. **Average Features ($\text{Avg}$):** $\text{Parameter\_Avg} = \frac{\text{Min} + \text{Max}}{2}$
   - Derived for: DO, BOD, pH, Temperature, Electrical Conductivity, Nitrate-N, Fecal Coliform, Total Coliform, and Fecal Streptococci.
2. **Range Features ($\text{Range}$):** $\text{Parameter\_Range} = |\text{Max} - \text{Min}|$
   - Measures seasonal hydrological and contamination volatility.
3. **Microbial Log Transforms:** Microbial populations span $10^1$ to $10^7\text{ MPN/100ml}$. Transformed via:
   $$\text{Log\_Total\_Coliform} = \log_{10}(\text{Total\_Coliform\_Avg} + 1)$$
   $$\text{Log\_Fecal\_Coliform} = \log_{10}(\text{Fecal\_Coliform\_Avg} + 1)$$
4. **Dissolved Oxygen Deficit:** Deficit below atmospheric saturation:
   $$\text{DO\_Deficit} = \max(0.0, 8.5 - \text{DO\_Avg})$$
5. **Organic-to-Nutrient Ratio:** $\frac{\text{BOD\_Avg}}{\text{Nitrate\_Avg} + 0.1}$

---

## 4. Regulatory Water Quality Classification (CPCB & WAWQI)

### 4.1 CPCB Designated Best Use Thresholds
- **Class A (Drinking Water Source w/o Conventional Treatment):**
  - $\text{DO} \ge 6.0\text{ mg/L}$, $\text{BOD} \le 2.0\text{ mg/L}$, $\text{pH } 6.5\text{--}8.5$, $\text{Total Coliform} \le 50\text{ MPN/100ml}$.
  - *Dataset Share:* **1,249 samples (12.9%)**
- **Class B (Outdoor Bathing):**
  - $\text{DO} \ge 5.0\text{ mg/L}$, $\text{BOD} \le 3.0\text{ mg/L}$, $\text{pH } 6.5\text{--}8.5$, $\text{Total Coliform} \le 500\text{ MPN/100ml}$.
  - *Dataset Share:* **2,128 samples (22.1%)**
- **Class C (Drinking Water Source after Conventional Treatment):**
  - $\text{DO} \ge 4.0\text{ mg/L}$, $\text{BOD} \le 3.0\text{ mg/L}$, $\text{pH } 6.0\text{--}9.0$, $\text{Total Coliform} \le 5,000\text{ MPN/100ml}$.
  - *Dataset Share:* **2,240 samples (23.2%)**
- **Class D (Propagation of Wildlife & Fisheries):**
  - $\text{DO} \ge 4.0\text{ mg/L}$, $\text{pH } 6.5\text{--}8.5$.
  - *Dataset Share:* **2,459 samples (25.5%)**
- **Class E (Irrigation, Industrial Cooling, Controlled Waste Disposal):**
  - $\text{pH } 6.0\text{--}8.5$, $\text{Electrical Conductivity} \le 2,250\text{ }\mu\text{mho/cm}$.
  - *Dataset Share:* **724 samples (7.5%)**
- **Below-Class E (Critically Polluted / Severe Hypoxia):**
  - Fails all criteria ($\text{DO} < 4.0\text{ mg/L}$ or $\text{BOD} > 3.0\text{ mg/L}$).
  - *Dataset Share:* **844 samples (8.8%)**

---

## 5. Machine Learning Modeling & Results

### 5.1 Zero-Leakage Experimental Setup
- **Target Variable:** `BOD_Avg` (Biochemical Oxygen Demand in mg/L).
- **Leakage Prevention:** `BOD Min`, `BOD Max`, `BOD Range`, `WQI`, and `CPCB Class` were strictly excluded from input features $X$.
- **Temporal Split:** Training set ($\le 2020$: 5,182 samples); Testing set ($2021\text{--}2023$: 4,109 samples).
- **Preprocessing Pipeline:** `SimpleImputer(strategy='median')` + `StandardScaler()` for numerical features; `OneHotEncoder(handle_unknown='ignore')` for State.

### 5.2 Model Comparison Leaderboard
| Model Architecture | Test RMSE (mg/L) | Test MAE (mg/L) | Test $R^2$ | 5-Fold CV RMSE | Train-Test Gap | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Random Forest (Tuned)** 🏆 | **6.4811** | **2.0903** | **0.5153** | **7.4871** | **0.3444** | 🏆 **Champion Model** |
| Random Forest (Default) | 6.7371 | 2.2052 | 0.4762 | 7.6695 | 0.4158 | Strong Generalization |
| Gradient Boosting | 7.0976 | 2.3044 | 0.4187 | 7.6223 | 0.5433 | Competitive |
| XGBoost (Tuned) | 7.2226 | 2.3404 | 0.3980 | 6.8373 | 0.5444 | Low Variance |
| Ridge Regression | 7.4587 | 3.5199 | 0.3580 | 9.7273 | 0.0611 | Baseline Linear |
| Linear Regression | 7.4977 | 3.5945 | 0.3513 | 9.7819 | 0.0540 | Baseline Linear |
| XGBoost (Default) | 7.7104 | 2.3646 | 0.3140 | 7.3692 | 0.6371 | Baseline Ensemble |
| Decision Tree | 9.2612 | 2.5559 | 0.0102 | 9.8104 | 0.8795 | Overfitted |

### 5.3 Explainable AI (SHAP) Insights
- **Untreated Sewage Dominance:** `Log_Total_Coliform` accounts for $> 45\%$ of total feature importance. Municipal sewage discharge is the primary source of biological oxygen demand.
- **Hypoxia Coupling:** Dissolved Oxygen exhibits a strong negative SHAP correlation ($r = -0.32$), reflecting active bacterial respiration during organic decomposition.

---

## 6. How to Run the Project Modules

### 1. Launch the Streamlit Dashboard
```powershell
streamlit run dashboard/app.py
```
Access in your browser at: `http://localhost:8501`

### 2. Run Inference from Terminal
```powershell
python src/predict.py
```

### 3. Execute the Full Data Pipeline
```powershell
python src/cleaning.py
python src/features.py
python src/assessment.py
python src/train.py
python src/evaluate.py
python src/generate_visualizations.py
```

### 4. Open Jupyter Notebooks
All 8 step-by-step notebooks are located in [`notebooks/`](file:///c:/Users/harsh/OneDrive/Desktop/river%20water%20analytics%20system/notebooks).
