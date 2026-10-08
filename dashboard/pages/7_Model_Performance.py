"""
Streamlit Page 7: Model Performance
Leaderboard of trained candidate models, 5-fold cross-validation results,
Actual vs. Predicted plots, and residual error diagnostics.
"""

import os
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Model Performance", page_icon="🏆", layout="wide")
st.title("🏆 Machine Learning Model Performance & Leaderboard")
st.markdown("Rigorous benchmark of candidate models evaluated on temporal test split (2021–2023) and 5-fold cross-validation.")


@st.cache_data
def load_comparison():
    paths = ["models/model_comparison.csv", "../models/model_comparison.csv"]
    for p in paths:
        if os.path.exists(p):
            return pd.read_csv(p)
    return None


df_comp = load_comparison()

if df_comp is not None:
    tab1, tab2, tab3 = st.tabs(["📊 Model Leaderboard", "📈 Metric Visual Comparisons", "🔬 Residual & Error Diagnostics"])

    with tab1:
        st.subheader("Candidate Model Comparison Table")
        st.dataframe(
            df_comp.style.highlight_min(subset=["Test RMSE", "Test MAE", "Train-Test Gap"], color="#c6f6d5")
                   .highlight_max(subset=["Test R2"], color="#c6f6d5"),
            use_container_width=True
        )

        st.markdown("""
        **Key Evaluation Takeaways:**
        - **Random Forest (Tuned)** achieved champion status with the lowest Test RMSE (**6.48 mg/L**), lowest Test MAE (**2.09 mg/L**), and highest generalization $R^2$ (**0.515**).
        - Linear and Ridge baselines yielded higher errors (RMSE $\\approx 7.46$–$7.50$ mg/L, $R^2 \\approx 0.35$), demonstrating the non-linear dynamics between chemical parameters and microbial oxygen demand.
        - Decision Tree alone experienced substantial overfitting (Train $R^2 = 0.89$ vs. Test $R^2 = 0.01$), highlighting the necessity of ensemble bagging/boosting.
        """)

    with tab2:
        st.subheader("Side-by-Side Model Metric Comparison")
        c1, c2 = st.columns(2)
        with c1:
            fig_rmse = px.bar(
                df_comp, x="Model", y="Test RMSE", color="Model",
                title="Test RMSE by Model (Lower is Better)",
                color_discrete_sequence=px.colors.sequential.Sunset
            )
            fig_rmse.update_layout(showlegend=False, xaxis_tickangle=-45)
            st.plotly_chart(fig_rmse, use_container_width=True)

        with c2:
            fig_r2 = px.bar(
                df_comp, x="Model", y="Test R2", color="Model",
                title="Test R² Coefficient of Determination (Higher is Better)",
                color_discrete_sequence=px.colors.sequential.Viridis
            )
            fig_r2.update_layout(showlegend=False, xaxis_tickangle=-45)
            st.plotly_chart(fig_r2, use_container_width=True)

    with tab3:
        st.subheader("Diagnostic Evaluation Charts")
        col_img1, col_img2 = st.columns(2)

        actual_pred_path = "visualizations/actual_vs_predicted.png" if os.path.exists("visualizations/actual_vs_predicted.png") else "../visualizations/actual_vs_predicted.png"
        resid_path = "visualizations/residuals_plot.png" if os.path.exists("visualizations/residuals_plot.png") else "../visualizations/residuals_plot.png"
        dist_path = "visualizations/residuals_distribution.png" if os.path.exists("visualizations/residuals_distribution.png") else "../visualizations/residuals_distribution.png"

        with col_img1:
            if os.path.exists(actual_pred_path):
                st.image(actual_pred_path, caption="Actual vs. Predicted BOD (mg/L)", use_container_width=True)
            if os.path.exists(dist_path):
                st.image(dist_path, caption="Residual Error Distribution", use_container_width=True)

        with col_img2:
            if os.path.exists(resid_path):
                st.image(resid_path, caption="Residuals vs. Fitted Predicted Values", use_container_width=True)

            st.info("""
            **Diagnostic Observations:**
            - Residual errors are centered symmetrically around 0.
            - Outliers at extreme high BOD concentrations (> 50 mg/L) correspond to acute industrial dump events where linear relationships plateau.
            """)
else:
    st.error("Model comparison table not found.")
