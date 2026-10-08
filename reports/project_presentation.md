# River Water Quality Analytics System: Project Presentation Deck

**Topic:** End-to-End River Water Quality Analytics, Regulatory Assessment & Machine Learning System  
**Audience:** Technical Reviewers, Viva Committee, Environmental Data Stakeholders  
**Dataset:** CPCB River Water Quality Over Years (2012–2023)  

---

## Slide 1: Title & Project Overview
- **Title:** River Water Quality Analytics System
- **Subtitle:** An End-to-End Data Science, Regulatory Assessment & Explainable AI Architecture
- **Key Modules:**
  1. Automated Data Cleaning & Anomaly Correction
  2. Feature Engineering & Microbiological Log-Transformations
  3. CPCB Designated Best Use & Weighted Arithmetic WQI Assessment
  4. Zero-Data-Leakage Machine Learning Benchmark (BOD Prediction)
  5. Interactive Streamlit Decision Support Dashboard

---

## Slide 2: Problem Statement & Motivation
- **The Environmental Crisis:** Over 80% of India's surface waters receive untreated municipal sewage and non-point runoff.
- **The Data Challenge:** Raw environmental datasets contain sensor drops, irregular missing placeholders (`BDL`, `nil`, `-`), newline text fractures, and data entry typos.
- **Objective:** Build an automated, reproducible analytics engine adhering strictly to statutory standards (CPCB and BIS 10500) to evaluate water quality and predict organic river pollution.

---

## Slide 3: Data Ingestion & Systematic Cleaning
- **Raw Volume:** 10,006 rows, 22 columns across 2012–2023.
- **Key Cleaning Transformations:**
  - Standardized units to clean ASCII representations (`(°C)` -> `(C)`, `(µmho/cm)` -> `(umho/cm)`).
  - Cell parser replaced string tokens (`BDL`, `nil`, `-`) with `NaN`.
  - Repaired newline-split numbers (e.g. `'76-\n 00'` -> `7600`).
  - Consolidated 54 irregular state names into 30 standardized entities.
  - Eliminated 362 duplicate observations (yielding 9,644 clean samples).
  - Safe physical outlier capping: pH $[0, 14]$, Temperature $[0, 50]^\circ\text{C}$, DO $[0, 25]\text{ mg/L}$.

---

## Slide 4: Feature Engineering & Domain Indicators
- **Paired Aggregations:** Derived `Average` and `Range` for all physical, chemical, and biological measurements.
- **Microbiological Dynamics:** Total Coliform and Fecal Coliform vary exponentially ($10^1$ to $10^7$); transformed via $\log_{10}(\text{Count} + 1)$.
- **Biochemical Proxies:** Dissolved Oxygen Deficit ($\max(0, 8.5 - \text{DO})$) and Organic-to-Nitrate loading ratio.
- **Feature Set:** Expanded from 22 raw columns to **45 high-information features**.

---

## Slide 5: Exploratory Data Analysis & Empirical Insights
- **Inverse DO-BOD Coupling ($r = -0.32$):** Confirms that bacterial metabolism of organic matter drives acute aquatic hypoxia.
- **Coliform-BOD Direct Correlation ($r > 0.40$):** Identifies raw untreated domestic sewage—rather than agricultural runoff—as the dominant driver of organic degradation.
- **Spatial Distribution:** Upstream Himalayan stretches (Himachal Pradesh, Uttarakhand) maintain pristine Class A/B water; densely populated Gangetic and peninsular plains (Uttar Pradesh, Maharashtra, Gujarat) carry extreme organic loads.

---

## Slide 6: Regulatory Assessment (CPCB & WAWQI)
- **CPCB Designated Best Use Compliance:**
  - Class A (Drinking without treatment): **12.9%**
  - Class B (Outdoor bathing): **22.1%**
  - Class C (Drinking after conventional treatment): **23.2%**
  - Class D (Wildlife & Fisheries): **25.5%**
  - Class E (Irrigation/Industrial): **7.5%**
  - **Below-Class E (Severely Polluted / Critical):** **8.8%**
- **Weighted Arithmetic WQI (WAWQI):** Inversely weighted by BIS 10500 drinking limits. Demonstrates that over 80% of river points require intensive treatment before domestic use.

---

## Slide 7: Machine Learning Architecture & Leakage Prevention
- **Target Selection:** Biochemical Oxygen Demand (`BOD_Avg` in mg/L) — the universal benchmark for river organic pollution.
- **Strict Leakage Prevention Protocol:**
  - To prevent synthetic 100% accuracy, `BOD Min`, `BOD Max`, and `BOD Range` were **strictly excluded** from feature inputs.
  - Preprocessor encapsulated inside Scikit-Learn `Pipeline` (Median Imputer + StandardScaler + OneHotEncoder).
- **Split Strategy:** Temporal split (Train: 2012–2020, 5,182 samples; Test: 2021–2023, 4,109 samples) combined with 5-Fold Cross-Validation.

---

## Slide 8: Model Evaluation & Leaderboard
- **Champion Model:** **Random Forest (Tuned)**
  - **Test RMSE:** **6.4811 mg/L** (Lowest error)
  - **Test MAE:** **2.0903 mg/L**
  - **Test $R^2$:** **0.5153** (Highest generalization)
  - **5-Fold CV RMSE:** **7.4871 mg/L**
- **Benchmark Comparisons:**
  - Linear/Ridge Baselines ($R^2 \approx 0.35$) failed to capture non-linear biochemical dynamics.
  - Unregularized Decision Tree suffered catastrophic overfitting (Train $R^2 = 0.89$ vs. Test $R^2 = 0.01$).
  - Ensemble bagging and boosting proved essential for robust tabular performance.

---

## Slide 9: Explainable AI (SHAP & Diagnostics)
- **Global SHAP Findings:**
  1. `Log_Total_Coliform` and `Log_Fecal_Coliform` are the primary positive drivers of elevated BOD.
  2. `DO_Avg` contributes negative SHAP values—confirming that hypoxic conditions are the key signature of organic overload.
  3. Residual diagnostics confirm zero-centered, homoscedastic error distribution across typical concentrations ($0\text{--}30\text{ mg/L}$).

---

## Slide 10: Interactive Streamlit Decision Support Dashboard
- **Executive Portal:** National summary metrics, historical trends, and quick state lookup.
- **Analytical Modules:**
  - Interactive parameter histograms and box plots.
  - 2012 vs. 2023 temporal trajectory comparator.
  - Spatial hotspot explorer and station deep dive.
  - Official CPCB Designated Best Use & WAWQI analytics.
  - Real-time BOD and water quality predictor with environmental health advisories.
  - Model diagnostics and SHAP explainability visualizations.

---

## Slide 11: Policy Recommendations & Conclusion
1. **Targeted Sewage Interception:** Prioritize interceptor drains in Below-Class E urban river corridors.
2. **Real-Time Sensor Deployments:** Optical continuous DO and conductivity probes at critical industrial outfalls.
3. **Mandatory Environmental Flows (E-Flows):** Safeguard minimum dry-season river discharge from upstream barrages.
4. **Reproducible Data Pipeline:** Clean, modular Python architecture supporting regulatory decision-making and continuous environmental monitoring.
