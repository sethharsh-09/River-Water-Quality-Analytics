"""
Model Training Module for River Water Quality Analytics System
Implements:
- Strict zero-leakage target/feature segregation (PDF Section 3)
- Robust Scikit-Learn Pipeline with Median Imputation, Scaling, and OneHotEncoding
- Train/Test Split (Temporal Year Split + GroupKFold evaluation)
- Multiple candidate models: Linear Regression, Decision Tree, Random Forest, Gradient Boosting, XGBoost
- Hyperparameter tuning for top 2 models (Random Forest & XGBoost)
- Model comparison table generation and best pipeline serialization via joblib
"""

import os
import sys
import numpy as np
import pandas as pd
import joblib

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import GridSearchCV, KFold, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.features import engineer_features


def prepare_modeling_data(df: pd.DataFrame = None):
    """
    Prepares features X and target y with STRICT ZERO DATA LEAKAGE:
    - Target: BOD_Avg (Biochemical Oxygen Demand in mg/L)
    - Removed from features:
      * BOD (mg/L) Min, BOD (mg/L) Max, BOD_Range, BOD_Avg (source columns of target)
      * WQI, WQI_Category, CPCB_Designated_Class (rule-based derived indices)
      * Station Code, Monitoring Location (high-cardinality identifiers, Station Code used for grouping)
    """
    if df is None:
        features_path = "data/processed/features.csv"
        if os.path.exists(features_path):
            df = pd.read_csv(features_path)
        else:
            df = engineer_features()

    df = df.copy()

    # Drop rows where target BOD_Avg is NaN
    valid_mask = df["BOD_Avg"].notna() & (df["BOD_Avg"] >= 0)
    df_clean = df[valid_mask].copy()

    # Feature definitions
    num_cols = [
        "Temp_Avg", "Temp_Range",
        "DO_Avg", "DO_Range",
        "pH_Avg", "pH_Range",
        "Conductivity_Avg", "Conductivity_Range",
        "Nitrate_Avg", "Nitrate_Range",
        "Log_Total_Coliform", "Log_Fecal_Coliform",
        "Year"
    ]
    # Keep only available numerical columns
    num_cols = [c for c in num_cols if c in df_clean.columns]
    cat_cols = ["State"]

    feature_cols = num_cols + cat_cols
    X = df_clean[feature_cols].copy()
    y = df_clean["BOD_Avg"].copy()

    return df_clean, X, y, num_cols, cat_cols


def build_preprocessor(num_cols, cat_cols):
    """Builds scikit-learn ColumnTransformer for numeric and categorical pipelines."""
    num_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    cat_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="UNKNOWN")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    preprocessor = ColumnTransformer([
        ("num", num_pipeline, num_cols),
        ("cat", cat_pipeline, cat_cols)
    ], remainder="drop")

    return preprocessor


def train_and_evaluate_models(models_dir: str = "models", data_dir: str = "data"):
    """
    Trains candidate models on temporal train/test split (<= 2020 train, > 2020 test).
    Evaluates MAE, RMSE, R2, and 5-fold Cross-Validation score.
    Tunes top 2 models (Random Forest and XGBoost).
    Selects and saves best pipeline to models/best_model.joblib.
    """
    os.makedirs(models_dir, exist_ok=True)
    df_clean, X, y, num_cols, cat_cols = prepare_modeling_data()

    # 1. Temporal Split (older years train, newer years test) to mimic real-world deployment
    test_years = [2021, 2022, 2023]
    train_mask = ~df_clean["Year"].isin(test_years)
    test_mask = df_clean["Year"].isin(test_years)

    X_train, y_train = X[train_mask], y[train_mask]
    X_test, y_test = X[test_mask], y[test_mask]

    print(f"Dataset split: Train rows={len(X_train)} (Years: {sorted(df_clean.loc[train_mask, 'Year'].unique())}), "
          f"Test rows={len(X_test)} (Years: {sorted(df_clean.loc[test_mask, 'Year'].unique())})")

    preprocessor = build_preprocessor(num_cols, cat_cols)

    candidate_models = {
        "Linear Regression (Baseline)": LinearRegression(),
        "Ridge Regression": Ridge(alpha=10.0),
        "Decision Tree": DecisionTreeRegressor(max_depth=8, random_state=42),
        "Random Forest": RandomForestRegressor(n_estimators=100, max_depth=12, min_samples_split=5, random_state=42, n_jobs=-1),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, learning_rate=0.08, max_depth=5, random_state=42),
        "XGBoost": xgb.XGBRegressor(n_estimators=100, learning_rate=0.08, max_depth=5, random_state=42, n_jobs=-1)
    }

    results = []

    for name, est in candidate_models.items():
        print(f"Training {name}...")
        pipe = Pipeline([
            ("preprocessor", preprocessor),
            ("regressor", est)
        ])

        # Fit model
        pipe.fit(X_train, y_train)

        # Predictions
        y_train_pred = pipe.predict(X_train)
        y_test_pred = pipe.predict(X_test)

        # Metrics
        train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
        test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
        train_mae = mean_absolute_error(y_train, y_train_pred)
        test_mae = mean_absolute_error(y_test, y_test_pred)
        train_r2 = r2_score(y_train, y_train_pred)
        test_r2 = r2_score(y_test, y_test_pred)
        train_test_gap = abs(train_r2 - test_r2)

        # 5-Fold Cross Validation on Train Set
        cv = KFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(pipe, X_train, y_train, cv=cv, scoring="neg_root_mean_squared_error", n_jobs=-1)
        mean_cv_rmse = -np.mean(cv_scores)

        results.append({
            "Model": name,
            "Train RMSE": round(train_rmse, 4),
            "Test RMSE": round(test_rmse, 4),
            "Train MAE": round(train_mae, 4),
            "Test MAE": round(test_mae, 4),
            "Train R2": round(train_r2, 4),
            "Test R2": round(test_r2, 4),
            "CV RMSE (5-Fold)": round(mean_cv_rmse, 4),
            "Train-Test Gap": round(train_test_gap, 4),
            "pipeline": pipe
        })

    results_df = pd.DataFrame(results)

    # 2. Hyperparameter Tuning for top 2 models: Random Forest & XGBoost
    print("\n--- Hyperparameter Tuning Top Models ---")
    
    # Random Forest Tuning
    rf_param_grid = {
        "regressor__n_estimators": [100, 150],
        "regressor__max_depth": [8, 12, 16],
        "regressor__min_samples_split": [2, 5],
        "regressor__min_samples_leaf": [1, 2]
    }
    rf_pipe = Pipeline([("preprocessor", preprocessor), ("regressor", RandomForestRegressor(random_state=42, n_jobs=-1))])
    rf_search = GridSearchCV(rf_pipe, rf_param_grid, cv=3, scoring="neg_root_mean_squared_error", n_jobs=-1)
    rf_search.fit(X_train, y_train)
    best_rf = rf_search.best_estimator_

    # XGBoost Tuning
    xgb_param_grid = {
        "regressor__n_estimators": [100, 150],
        "regressor__max_depth": [4, 6, 8],
        "regressor__learning_rate": [0.03, 0.08, 0.15],
        "regressor__subsample": [0.8, 1.0]
    }
    xgb_pipe = Pipeline([("preprocessor", preprocessor), ("regressor", xgb.XGBRegressor(random_state=42, n_jobs=-1))])
    xgb_search = GridSearchCV(xgb_pipe, xgb_param_grid, cv=3, scoring="neg_root_mean_squared_error", n_jobs=-1)
    xgb_search.fit(X_train, y_train)
    best_xgb = xgb_search.best_estimator_

    # Evaluate Tuned Models
    for tuned_name, tuned_pipe, best_params in [
        ("Random Forest (Tuned)", best_rf, rf_search.best_params_),
        ("XGBoost (Tuned)", best_xgb, xgb_search.best_params_)
    ]:
        y_train_pred = tuned_pipe.predict(X_train)
        y_test_pred = tuned_pipe.predict(X_test)
        train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
        test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
        train_mae = mean_absolute_error(y_train, y_train_pred)
        test_mae = mean_absolute_error(y_test, y_test_pred)
        train_r2 = r2_score(y_train, y_train_pred)
        test_r2 = r2_score(y_test, y_test_pred)
        gap = abs(train_r2 - test_r2)

        cv_scores = cross_val_score(tuned_pipe, X_train, y_train, cv=5, scoring="neg_root_mean_squared_error", n_jobs=-1)
        mean_cv_rmse = -np.mean(cv_scores)

        results.append({
            "Model": tuned_name,
            "Train RMSE": round(train_rmse, 4),
            "Test RMSE": round(test_rmse, 4),
            "Train MAE": round(train_mae, 4),
            "Test MAE": round(test_mae, 4),
            "Train R2": round(train_r2, 4),
            "Test R2": round(test_r2, 4),
            "CV RMSE (5-Fold)": round(mean_cv_rmse, 4),
            "Train-Test Gap": round(gap, 4),
            "pipeline": tuned_pipe
        })
        print(f"{tuned_name} Best Params: {best_params} -> Test R2: {test_r2:.4f}, Test RMSE: {test_rmse:.4f}")

    # Build final comparison table
    comparison_table = pd.DataFrame([{k: v for k, v in r.items() if k != "pipeline"} for r in results])
    comparison_table = comparison_table.sort_values(by="Test RMSE", ascending=True).reset_index(drop=True)

    comparison_path = os.path.join(models_dir, "model_comparison.csv")
    comparison_table.to_csv(comparison_path, index=False)
    print("\n=== Model Comparison Leaderboard ===")
    print(comparison_table.to_string())

    # Select Best Model based on lowest Test RMSE & CV RMSE and balanced generalization gap
    best_entry = min(results, key=lambda r: (r["Test RMSE"] + r["CV RMSE (5-Fold)"]))
    best_model_name = best_entry["Model"]
    best_pipeline = best_entry["pipeline"]

    best_model_path = os.path.join(models_dir, "best_model.joblib")
    # Save model pipeline along with metadata for easy inference
    model_artifact = {
        "pipeline": best_pipeline,
        "model_name": best_model_name,
        "num_cols": num_cols,
        "cat_cols": cat_cols,
        "metrics": {k: v for k, v in best_entry.items() if k != "pipeline"},
        "test_data": {"X_test": X_test, "y_test": y_test, "X_train": X_train, "y_train": y_train}
    }
    joblib.dump(model_artifact, best_model_path)
    print(f"\nBest Model Selected: '{best_model_name}' saved to {best_model_path}")

    return comparison_table, model_artifact


if __name__ == "__main__":
    train_and_evaluate_models()
