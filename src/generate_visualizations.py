"""
Comprehensive Visualization Generator for River Water Quality Analytics System
Generates all publication-quality charts for EDA, Temporal Analysis, State Comparisons,
and CPCB Water Quality Assessments, saved directly to the 'visualizations/' directory.
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.assessment import assess_water_quality


def generate_all_eda_visualizations(viz_dir: str = "visualizations"):
    """Generates all exploratory and domain visualization charts."""
    os.makedirs(viz_dir, exist_ok=True)
    sns.set_theme(style="whitegrid", font_scale=1.0)
    plt.rcParams["font.sans-serif"] = "DejaVu Sans"

    # Load assessed dataset
    df = assess_water_quality()

    # 1. Parameter Distributions
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    params = [
        ("DO_Avg", "Dissolved Oxygen (mg/L)", "#2b5c8f", (0, 15)),
        ("pH_Avg", "pH", "#27ae60", (4, 11)),
        ("BOD_Avg", "Biochemical Oxygen Demand (mg/L)", "#e74c3c", (0, 30)),
        ("Conductivity_Avg", "Conductivity (µmho/cm)", "#8e44ad", (0, 3000)),
        ("Nitrate_Avg", "Nitrate-N (mg/L)", "#d35400", (0, 20)),
        ("Log_Total_Coliform", "Log10 Total Coliform (MPN/100ml)", "#16a085", (0, 7))
    ]

    for ax, (col, label, color, xlim) in zip(axes.flatten(), params):
        if col in df.columns:
            data = df[col].dropna()
            sns.histplot(data, kde=True, ax=ax, color=color, bins=35)
            ax.set_title(f"Distribution of {label}", fontsize=12, fontweight="bold")
            ax.set_xlabel(label, fontsize=11)
            ax.set_ylabel("Count", fontsize=11)
            ax.set_xlim(xlim)

    plt.tight_layout()
    plt.savefig(os.path.join(viz_dir, "eda_distributions.png"), dpi=300)
    plt.close()
    print("Saved: eda_distributions.png")

    # 2. Correlation Heatmap
    corr_cols = [
        "DO_Avg", "pH_Avg", "BOD_Avg", "Conductivity_Avg", "Nitrate_Avg",
        "Log_Total_Coliform", "Temp_Avg", "WQI"
    ]
    corr_df = df[[c for c in corr_cols if c in df.columns]].dropna().corr()

    plt.figure(figsize=(10, 8))
    sns.heatmap(
        corr_df, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1,
        linewidths=0.5, cbar_kws={"label": "Pearson Correlation"}
    )
    plt.title("Water Quality Parameters Correlation Heatmap", fontsize=14, fontweight="bold", pad=12)
    plt.tight_layout()
    plt.savefig(os.path.join(viz_dir, "eda_correlation_heatmap.png"), dpi=300)
    plt.close()
    print("Saved: eda_correlation_heatmap.png")

    # 3. Temporal Trends (2012 - 2023)
    yearly = df.groupby("Year")[["DO_Avg", "BOD_Avg", "pH_Avg", "Nitrate_Avg"]].median().reset_index()
    # Filter years with valid data
    yearly = yearly[yearly["Year"] > 2000].sort_values("Year")

    fig, ax1 = plt.subplots(figsize=(12, 6))
    color = "tab:blue"
    ax1.set_xlabel("Year", fontsize=12, fontweight="bold")
    ax1.set_ylabel("DO & pH (Median)", color=color, fontsize=12, fontweight="bold")
    l1 = ax1.plot(yearly["Year"], yearly["DO_Avg"], color="#1f77b4", marker="o", linewidth=2.5, label="DO (mg/L)")
    l2 = ax1.plot(yearly["Year"], yearly["pH_Avg"], color="#2ca02c", marker="s", linewidth=2.5, linestyle="--", label="pH")
    ax1.tick_params(axis="y", labelcolor=color)

    ax2 = ax1.twinx()
    color = "tab:red"
    ax2.set_ylabel("BOD & Nitrate (mg/L, Median)", color=color, fontsize=12, fontweight="bold")
    l3 = ax2.plot(yearly["Year"], yearly["BOD_Avg"], color="#d62728", marker="^", linewidth=2.5, label="BOD (mg/L)")
    l4 = ax2.plot(yearly["Year"], yearly["Nitrate_Avg"], color="#ff7f0e", marker="d", linewidth=2.5, linestyle=":", label="Nitrate (mg/L)")
    ax2.tick_params(axis="y", labelcolor=color)

    lines = l1 + l2 + l3 + l4
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="upper right", frameon=True)
    plt.title("Year-Wise Water Quality Trends in Indian Rivers (2012–2023)", fontsize=14, fontweight="bold", pad=12)
    plt.tight_layout()
    plt.savefig(os.path.join(viz_dir, "temporal_trends_parameters.png"), dpi=300)
    plt.close()
    print("Saved: temporal_trends_parameters.png")

    # 4. 2012 vs 2023 Comparison
    comp_years = df[df["Year"].isin([2012, 2023])]
    if not comp_years.empty:
        comp_agg = comp_years.groupby("Year")[["DO_Avg", "BOD_Avg", "pH_Avg", "Nitrate_Avg"]].mean().T.reset_index()
        comp_agg.columns = ["Parameter", "Year_2012", "Year_2023"]
        comp_agg["Change_%"] = ((comp_agg["Year_2023"] - comp_agg["Year_2012"]) / comp_agg["Year_2012"] * 100).round(1)

        plt.figure(figsize=(9, 5))
        x = np.arange(len(comp_agg))
        width = 0.35
        plt.bar(x - width/2, comp_agg["Year_2012"], width, label="2012", color="#4a90e2")
        plt.bar(x + width/2, comp_agg["Year_2023"], width, label="2023", color="#50e3c2")
        plt.xticks(x, comp_agg["Parameter"], fontsize=11, fontweight="bold")
        plt.ylabel("Mean Value", fontsize=11, fontweight="bold")
        plt.title("River Water Quality Comparison: 2012 vs 2023", fontsize=13, fontweight="bold")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(viz_dir, "temporal_comparison_2012_vs_2023.png"), dpi=300)
        plt.close()
        print("Saved: temporal_comparison_2012_vs_2023.png")

    # 5. State-Wise Water Quality Ranking (Average BOD)
    state_bod = df.groupby("State")["BOD_Avg"].median().dropna().sort_values(ascending=False).head(15).reset_index()
    plt.figure(figsize=(12, 6))
    sns.barplot(data=state_bod, x="BOD_Avg", y="State", palette="Reds_r", hue="State", legend=False)
    plt.axvline(3.0, color="green", linestyle="--", linewidth=1.5, label="CPCB Bathing Standard (3.0 mg/L)")
    plt.title("Top 15 States with Highest Median River BOD (mg/L)", fontsize=13, fontweight="bold")
    plt.xlabel("Median BOD (mg/L)", fontsize=11, fontweight="bold")
    plt.ylabel("State", fontsize=11, fontweight="bold")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(viz_dir, "state_water_quality_ranking.png"), dpi=300)
    plt.close()
    print("Saved: state_water_quality_ranking.png")

    # 6. High-Risk River Monitoring Locations
    loc_bod = df.groupby(["Monitoring Location", "State"])["BOD_Avg"].mean().dropna().reset_index()
    loc_top = loc_bod.sort_values("BOD_Avg", ascending=False).head(15)
    loc_top["Location_Label"] = loc_top["Monitoring Location"].str[:35] + " (" + loc_top["State"].str[:8] + ")"

    plt.figure(figsize=(12, 7))
    sns.barplot(data=loc_top, x="BOD_Avg", y="Location_Label", palette="rocket", hue="Location_Label", legend=False)
    plt.title("Top 15 Most Severely Polluted River Monitoring Locations in India (Mean BOD)", fontsize=13, fontweight="bold")
    plt.xlabel("Mean BOD (mg/L)", fontsize=11, fontweight="bold")
    plt.ylabel("River Monitoring Location", fontsize=11, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(viz_dir, "high_risk_monitoring_locations.png"), dpi=300)
    plt.close()
    print("Saved: high_risk_monitoring_locations.png")

    # 7. CPCB Water Quality Classes Distribution
    plt.figure(figsize=(9, 5))
    class_order = [
        "Class A (Drinking w/o Treatment)",
        "Class B (Outdoor Bathing)",
        "Class C (Drinking after Treatment)",
        "Class D (Wildlife & Fisheries)",
        "Class E (Irrigation & Industrial)",
        "Below-E (Severely Polluted)"
    ]
    counts = df["CPCB_Designated_Class"].value_counts().reindex(class_order).dropna()
    colors = ["#2ecc71", "#27ae60", "#f39c12", "#e67e22", "#d35400", "#c0392b"]

    sns.barplot(x=counts.values, y=counts.index, palette=colors, hue=counts.index, legend=False)
    plt.title("CPCB Designated Best Use Classification Distribution", fontsize=13, fontweight="bold")
    plt.xlabel("Number of Monitoring Records", fontsize=11, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(viz_dir, "cpcb_water_classes_distribution.png"), dpi=300)
    plt.close()
    print("Saved: cpcb_water_classes_distribution.png")

    # 8. WAWQI Grades Distribution Donut Chart
    plt.figure(figsize=(8, 8))
    wqi_counts = df["WQI_Category"].value_counts()
    # Filter out unassessed
    wqi_counts = wqi_counts[wqi_counts.index != "Unassessed"]
    wqi_colors = ["#f39c12", "#c0392b", "#e74c3c", "#2ecc71", "#27ae60"]
    plt.pie(
        wqi_counts.values, labels=wqi_counts.index, autopct="%1.1f%%",
        startangle=140, colors=wqi_colors[:len(wqi_counts)],
        wedgeprops=dict(width=0.4, edgecolor="white", linewidth=2)
    )
    plt.title("Distribution of River Water Quality Index (WAWQI) Categories", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(viz_dir, "wqi_grades_distribution.png"), dpi=300)
    plt.close()
    print("Saved: wqi_grades_distribution.png")


if __name__ == "__main__":
    generate_all_eda_visualizations()
