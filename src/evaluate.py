"""
Evaluation and Visualization Module for River Water Quality Analytics System
Generates:
- Comprehensive metric tables (MAE, MSE, RMSE, R2, Train vs Test error)
- Visualizations:
  * Model Comparison Bar Chart
  * Actual vs. Predicted Scatter Plot
  * Residuals vs. Fitted Plot
  * Residual Distribution KDE & Histogram
  * Tree Feature Importance Plot
  * SHAP Explainability Summary Plot
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def plot_model_comparison(comparison_csv: str = "models/model_comparison.csv", save_path: str = "visualizations/model_comparison.png"):
    """Plots comparative evaluation metrics across all trained models."""
    if not os.path.exists(comparison_csv):
        print(f"Warning: {comparison_csv} not found.")
        return

    df_comp = pd.read_csv(comparison_csv)
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    sns.set_theme(style="whitegrid")

    palette = sns.color_palette("viridis", len(df_comp))

    # 1. Test RMSE
    sns.barplot(data=df_comp, x="Test RMSE", y="Model", ax=axes[0], palette=palette, hue="Model", legend=False)
    axes[0].set_title("Test RMSE (Lower is Better)", fontsize=13, fontweight="bold")
    axes[0].set_xlabel("Root Mean Squared Error (mg/L)")

    # 2. Test MAE
    sns.barplot(data=df_comp, x="Test MAE", y="Model", ax=axes[1], palette=palette, hue="Model", legend=False)
    axes[1].set_title("Test MAE (Lower is Better)", fontsize=13, fontweight="bold")
    axes[1].set_xlabel("Mean Absolute Error (mg/L)")
    axes[1].set_ylabel("")

    # 3. Test R2
    sns.barplot(data=df_comp, x="Test R2", y="Model", ax=axes[2], palette=palette, hue="Model", legend=False)
    axes[2].set_title("Test R² Score (Higher is Better)", fontsize=13, fontweight="bold")
    axes[2].set_xlabel("R² Coefficient of Determination")
    axes[2].set_ylabel("")

    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Model comparison chart saved to: {save_path}")


def evaluate_best_model(model_path: str = "models/best_model.joblib", viz_dir: str = "visualizations"):
    """Evaluates best model pipeline and generates diagnostics and explainability charts."""
    if not os.path.exists(model_path):
        print(f"Model file not found at {model_path}.")
        return

    os.makedirs(viz_dir, exist_ok=True)
    artifact = joblib.load(model_path)
    pipeline = artifact["pipeline"]
    model_name = artifact["model_name"]
    test_data = artifact["test_data"]

    X_test = test_data["X_test"]
    y_test = test_data["y_test"]

    y_pred = pipeline.predict(X_test)
    y_pred = np.clip(y_pred, 0, None)
    residuals = y_test - y_pred

    # 1. Actual vs Predicted Plot
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x=y_test, y=y_pred, alpha=0.5, color="#1f77b4", edgecolor="none")
    max_val = max(y_test.quantile(0.99), np.quantile(y_pred, 0.99))
    plt.plot([0, max_val], [0, max_val], color="crimson", linestyle="--", linewidth=2, label="Perfect Fit (y = x)")
    plt.xlim(0, max_val * 1.05)
    plt.ylim(0, max_val * 1.05)
    plt.xlabel("Actual BOD (mg/L)", fontsize=12, fontweight="bold")
    plt.ylabel("Predicted BOD (mg/L)", fontsize=12, fontweight="bold")
    plt.title(f"Actual vs Predicted BOD — {model_name}", fontsize=14, fontweight="bold")
    plt.legend(frameon=True)
    plt.tight_layout()
    plt.savefig(os.path.join(viz_dir, "actual_vs_predicted.png"), dpi=300)
    plt.close()

    # 2. Residuals vs Predicted Plot
    plt.figure(figsize=(8, 5))
    sns.scatterplot(x=y_pred, y=residuals, alpha=0.5, color="#2ca02c", edgecolor="none")
    plt.axhline(0, color="crimson", linestyle="--", linewidth=1.5)
    plt.xlabel("Predicted BOD (mg/L)", fontsize=12, fontweight="bold")
    plt.ylabel("Residuals (Actual - Predicted)", fontsize=12, fontweight="bold")
    plt.title(f"Residual Plot — {model_name}", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(viz_dir, "residuals_plot.png"), dpi=300)
    plt.close()

    # 3. Residual Distribution
    plt.figure(figsize=(8, 5))
    sns.histplot(residuals, kde=True, bins=40, color="#9467bd", edgecolor="black")
    plt.axvline(0, color="crimson", linestyle="--", linewidth=1.5)
    plt.xlabel("Residual Error (mg/L)", fontsize=12, fontweight="bold")
    plt.ylabel("Frequency", fontsize=12, fontweight="bold")
    plt.title("Residual Distribution (Error Normality Check)", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(viz_dir, "residuals_distribution.png"), dpi=300)
    plt.close()

    # 4. Feature Importance
    regressor = pipeline.named_steps.get("regressor")
    preprocessor = pipeline.named_steps.get("preprocessor")

    if hasattr(regressor, "feature_importances_"):
        # Extract feature names
        num_names = artifact["num_cols"]
        cat_names = []
        try:
            ohe = preprocessor.named_transformers_["cat"].named_steps["onehot"]
            cat_names = list(ohe.get_feature_names_out(artifact["cat_cols"]))
        except Exception:
            pass
        all_features = num_names + cat_names
        importances = regressor.feature_importances_

        if len(all_features) == len(importances):
            fi_df = pd.DataFrame({"Feature": all_features, "Importance": importances})
            fi_df = fi_df.sort_values(by="Importance", ascending=False).head(15)

            plt.figure(figsize=(10, 6))
            sns.barplot(data=fi_df, x="Importance", y="Feature", palette="mako", hue="Feature", legend=False)
            plt.title(f"Top 15 Feature Importances — {model_name}", fontsize=14, fontweight="bold")
            plt.xlabel("Gini / Gain Importance", fontsize=12, fontweight="bold")
            plt.tight_layout()
            plt.savefig(os.path.join(viz_dir, "feature_importance.png"), dpi=300)
            plt.close()

    # 5. SHAP Explainability (PDF Step 14)
    try:
        import shap
        print("Computing SHAP values for model explainability...")
        X_trans = preprocessor.transform(X_test)
        # Use background sample of 100 for TreeExplainer
        explainer = shap.TreeExplainer(regressor, data=X_trans[:100])
        shap_values = explainer(X_trans[:200], check_additivity=False)

        plt.figure(figsize=(10, 6))
        # Map feature names
        if hasattr(shap_values, "feature_names") and (shap_values.feature_names is None or len(shap_values.feature_names) == 0):
            shap_values.feature_names = all_features[:X_trans.shape[1]]
        shap.summary_plot(shap_values, max_display=12, show=False)
        plt.title("SHAP Summary Plot (Feature Impact on Predicted BOD)", fontsize=13, fontweight="bold")
        plt.tight_layout()
        plt.savefig(os.path.join(viz_dir, "shap_summary.png"), dpi=300, bbox_inches="tight")
        plt.close()
        print("SHAP explainability plot saved successfully.")
    except Exception as e:
        print(f"SHAP generation notice: {e}")

    print("All evaluation charts generated successfully in:", viz_dir)


if __name__ == "__main__":
    plot_model_comparison()
    evaluate_best_model()
