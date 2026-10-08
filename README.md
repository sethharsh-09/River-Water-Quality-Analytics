# River Water Quality Analytics System 🌊

An end-to-end environmental data science, regulatory compliance assessment, and explainable machine learning analytics system built on historical river monitoring data across India (2012–2023).

---

## 📌 Project Overview
River ecosystems across India face severe stress from domestic sewage discharge, municipal runoff, and industrial effluents. This platform provides an end-to-end framework to:
1. **Audit & Clean Raw Environmental Data:** Safely resolve missing placeholders (`-`, `BDL`, `nil`), broken newline text, duplicate entries, and physical measurement outliers without deleting data records.
2. **Feature Engineering:** Calculate paired parameter averages, ranges, microbiological log-transformations, and nutrient stress ratios.
3. **Temporal & Spatial Analytics:** Track decadal trajectories (2012–2023) across states and identify high-risk river stretches.
4. **Official Regulatory Assessment:** Classify river health strictly according to **Central Pollution Control Board (CPCB) Designated Best Use Criteria (Classes A to E)** and the **Weighted Arithmetic Water Quality Index (WAWQI)**.
5. **Zero-Data-Leakage Machine Learning:** Benchmark multiple regressors (Linear Regression, Ridge, Decision Trees, Random Forest, Gradient Boosting, XGBoost) to predict river **Biochemical Oxygen Demand (BOD)** while strictly eliminating circular target leakage.
6. **Explainable AI (XAI):** Interpret model decisions using Gini/Gain feature importance and global **SHAP (SHapley Additive exPlanations)** analysis.
7. **Interactive Streamlit Web Dashboard:** A 9-page interactive dashboard for data exploration, spatial analysis, real-time prediction, and decision support.

---

## 📁 Project Folder Structure

```text
River-Water-Quality-Analytics/
│
├── data/
│   ├── raw/
│   │   └── RiverWaterQualityOverYears.csv      # Original untouched CPCB raw dataset (10,006 rows)
│   └── processed/
│       ├── cleaned_data.csv                    # Cleaned dataset (9,644 rows, duplicates removed)
│       ├── features.csv                        # Feature-engineered dataset (45 columns)
│       └── water_quality_assessed.csv          # Assessed dataset with CPCB classes & WAWQI
│
├── notebooks/
│   ├── 01_data_understanding.ipynb             # Step 1: Data understanding, schema & audit
│   ├── 02_data_cleaning.ipynb                  # Step 2: Cleaning, parsing & safe outlier capping
│   ├── 03_feature_engineering.ipynb            # Step 3: Average, range & log transforms
│   ├── 04_eda_visualization.ipynb              # Step 4: Distributions, correlations & stats
│   ├── 05_temporal_location_analysis.ipynb     # Step 5: 2012–2023 trends & spatial comparison
│   ├── 06_water_quality_assessment.ipynb       # Step 6: CPCB Designated Best Use & WAWQI
│   ├── 07_model_training_evaluation.ipynb      # Step 7: Zero-leakage ML pipeline & 5-fold CV
│   └── 08_explainability_forecasting.ipynb     # Step 8: SHAP explainability & trend analysis
│
├── src/
│   ├── data_loader.py                          # Robust CSV loading and header cleaning
│   ├── cleaning.py                             # Cell parsing, deduplication, state standardization
│   ├── features.py                             # Average, range, ratio & log feature derivation
│   ├── assessment.py                           # Official CPCB classification & WAWQI engine
│   ├── train.py                                # ML pipeline, temporal split, tuning & serialization
│   ├── evaluate.py                             # Diagnostic metrics, residual plots & SHAP analysis
│   ├── predict.py                              # Real-time inference & environmental advisory
│   └── generate_visualizations.py              # Publication-grade chart generation
│
├── models/
│   ├── best_model.joblib                       # Serialized champion pipeline (Random Forest Tuned)
│   └── model_comparison.csv                    # Evaluation leaderboard across all candidate models
│
├── dashboard/
│   ├── app.py                                  # Main Streamlit web application portal
│   └── pages/
│       ├── 1_📊_Overview_&_Audit.py            # Dataset audit, missingness & schema
│       ├── 2_📈_Water_Quality_Analytics.py     # Interactive parameter distributions & box plots
│       ├── 3_🗓️_Yearly_Trends.py               # 2012–2023 decadal trajectory comparator
│       ├── 4_🗺️_State_&_Location_Analysis.py   # State pollution rankings & station deep dive
│       ├── 5_🧪_WQI_&_CPCB_Assessment.py       # Regulatory CPCB classes & WAWQI grades
│       ├── 6_🤖_Water_Quality_Prediction.py    # Real-time ML predictor with health advisory
│       ├── 7_🏆_Model_Performance.py           # Model leaderboard & residual diagnostics
│       ├── 8_🔍_Feature_Importance_&_SHAP.py   # XAI feature rankings & SHAP beeswarm
│       └── 9_💡_Insights_&_Recommendations.py  # Empirical findings & policy recommendations
│
├── visualizations/                             # Saved high-resolution PNG charts
│   ├── actual_vs_predicted.png
│   ├── cpcb_water_classes_distribution.png
│   ├── eda_correlation_heatmap.png
│   ├── eda_distributions.png
│   ├── feature_importance.png
│   ├── high_risk_monitoring_locations.png
│   ├── model_comparison.png
│   ├── residuals_distribution.png
│   ├── residuals_plot.png
│   ├── shap_summary.png
│   ├── state_water_quality_ranking.png
│   ├── temporal_comparison_2012_vs_2023.png
│   ├── temporal_trends_parameters.png
│   └── wqi_grades_distribution.png
│
├── reports/
│   ├── final_report.md                         # Comprehensive technical report
│   ├── project_presentation.md                 # Slide-by-slide viva / presentation guide
│   └── workflow_flowchart.md                   # End-to-end system flowchart & diagram
│
├── requirements.txt                            # Pinned Python package dependencies
└── README.md                                   # Project documentation and execution guide
```

---

## ⚙️ Installation & Setup

### 1. Clone or Open the Repository
```bash
cd "c:\Users\harsh\OneDrive\Desktop\river water analytics system"
```

### 2. Install Required Dependencies
```bash
pip install -r requirements.txt
```

---

## 🚀 Running the Full Pipeline

You can run individual modules or execute the complete end-to-end pipeline:

### Step 1: Clean Raw Dataset
```bash
python src/cleaning.py
```
*Generates:* `data/processed/cleaned_data.csv`

### Step 2: Feature Engineering
```bash
python src/features.py
```
*Generates:* `data/processed/features.csv`

### Step 3: Scientific Regulatory Assessment
```bash
python src/assessment.py
```
*Generates:* `data/processed/water_quality_assessed.csv`

### Step 4: Train Machine Learning Pipeline & Hyperparameter Tuning
```bash
python src/train.py
```
*Generates:* `models/best_model.joblib` and `models/model_comparison.csv`

### Step 5: Evaluate & Generate Publication Charts
```bash
python src/evaluate.py
python src/generate_visualizations.py
```
*Generates:* All 14 high-resolution diagnostic and analytical charts in `visualizations/`

---

## 🖥️ Launching the Streamlit Web Dashboard

Launch the interactive 9-page decision support application:
```bash
streamlit run dashboard/app.py
```

Open your browser to `http://localhost:8501`.

---

## 🏆 Machine Learning Leaderboard

Evaluated on a **temporal test split (2021–2023)** to simulate real-world prospective deployment:

| Model | Test RMSE (mg/L) | Test MAE (mg/L) | Test $R^2$ | 5-Fold CV RMSE | Generalization Gap | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Random Forest (Tuned)** | **6.4811** | **2.0903** | **0.5153** | **7.4871** | **0.3444** | 🏆 **Champion** |
| Random Forest (Default) | 6.7371 | 2.2052 | 0.4762 | 7.6695 | 0.4158 | Candidate |
| Gradient Boosting | 7.0976 | 2.3044 | 0.4187 | 7.6223 | 0.5433 | Candidate |
| XGBoost (Tuned) | 7.2226 | 2.3404 | 0.3980 | 6.8373 | 0.5444 | Candidate |
| Ridge Regression | 7.4587 | 3.5199 | 0.3580 | 9.7273 | 0.0611 | Baseline |
| Linear Regression | 7.4977 | 3.5945 | 0.3513 | 9.7819 | 0.0540 | Baseline |
| XGBoost (Default) | 7.7104 | 2.3646 | 0.3140 | 7.3692 | 0.6371 | Candidate |
| Decision Tree | 9.2612 | 2.5559 | 0.0102 | 9.8104 | 0.8795 | Overfit |

---

## 🧪 Official Regulatory Standards

### Central Pollution Control Board (CPCB) Designated Best Use
- **Class A:** Drinking water source without conventional treatment (DO $\ge 6$, BOD $\le 2$, pH $6.5\text{--}8.5$, Coliform $\le 50$)
- **Class B:** Outdoor bathing (DO $\ge 5$, BOD $\le 3$, pH $6.5\text{--}8.5$, Coliform $\le 500$)
- **Class C:** Drinking water after conventional treatment (DO $\ge 4$, BOD $\le 3$, pH $6.0\text{--}9.0$, Coliform $\le 5000$)
- **Class D:** Wildlife propagation and fisheries (DO $\ge 4$, pH $6.5\text{--}8.5$)
- **Class E:** Irrigation and industrial cooling (pH $6.0\text{--}8.5$, Conductivity $\le 2250$)
- **Below-Class E:** Critically polluted / Hypoxic

---

## 📖 Citation & References
1. Central Pollution Control Board (CPCB), Ministry of Environment, Forest and Climate Change, Govt. of India: *Water Quality Criteria for Designated Best Use*.
2. Bureau of Indian Standards: *Indian Standard Drinking Water Specification (IS 10500:2012)*.
3. Brown, R.M., McClelland, N.I., Deininger, R.A. and Tozer, R.G. (1970). *A Water Quality Index - Do We Dare?* Water & Sewage Works.
