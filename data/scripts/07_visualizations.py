"""
Summary Visualizations

Purpose: Generate individual PNG plots for all analysis checks.
         No combined subplot grids - individual figures only for PDF readability.

Output: Multiple PNG files in outputs/antigravity/
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import matplotlib.pyplot as plt
import json

# Setup
np.random.seed(42)
BASE_DIR = Path(r"C:\Users\Lalit Hire\UIDAI Data Hackathon 2026\data")
INPUT_CSV = BASE_DIR / "UIDAI_with_population.csv"
OUT_DIR = BASE_DIR / "outputs" / "antigravity"
LOG_FILE = OUT_DIR / "antigravity.log"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def plot_imputation_distribution():
    """Plot distribution of imputation sources."""
    logger.info("Generating imputation distribution plot")
    
    try:
        imputed_df = pd.read_csv(OUT_DIR / "imputed_population_report.csv")
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        counts = imputed_df['imputation_source'].value_counts()
        ax.bar(range(len(counts)), counts.values, color='steelblue')
        ax.set_xticks(range(len(counts)))
        ax.set_xticklabels(counts.index, rotation=45, ha='right')
        ax.set_ylabel('Number of Pincodes')
        ax.set_title('Population Imputation Source Distribution')
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(OUT_DIR / "viz_imputation_distribution.png", dpi=200, bbox_inches='tight')
        plt.close()
        logger.info("  Saved: viz_imputation_distribution.png")
    except Exception as e:
        logger.warning(f"  Could not generate imputation plot: {e}")

def plot_sensitivity_comparison():
    """Plot service desert sensitivity comparison."""
    logger.info("Generating sensitivity comparison plot")
    
    try:
        sens_df = pd.read_csv(OUT_DIR / "service_desert_sensitivity.csv")
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        ax.plot(sens_df['threshold_pct'], sens_df['desert_count'], 
                marker='o', linewidth=2, markersize=8, color='darkred')
        ax.set_xlabel('Threshold (% of district baseline)')
        ax.set_ylabel('Number of Service Deserts')
        ax.set_title('Service Desert Count Sensitivity to Threshold\n(Primary: 50%)')
        ax.grid(alpha=0.3)
        
        # Highlight the 50% threshold
        primary_row = sens_df[sens_df['threshold_pct'] == 50]
        if not primary_row.empty:
            ax.axvline(x=50, color='blue', linestyle='--', alpha=0.5, label='Primary threshold (50%)')
            ax.legend()
        
        plt.tight_layout()
        plt.savefig(OUT_DIR / "viz_sensitivity_comparison.png", dpi=200, bbox_inches='tight')
        plt.close()
        logger.info("  Saved: viz_sensitivity_comparison.png")
    except Exception as e:
        logger.warning(f"  Could not generate sensitivity plot: {e}")

def plot_activity_distribution():
    """Plot activity per 100k distribution."""
    logger.info("Generating activity distribution histogram")
    
    try:
        # Load and prepare data
        df = pd.read_csv(INPUT_CSV, low_memory=False)
        df.columns = [c.strip().lower().replace(' ', '_').replace('-', '_') for c in df.columns]
        
        # Get population
        pop_col = None
        for c in ['total_population', 'population']:
            if c in df.columns:
                pop_col = c
                break
        
        if not pop_col:
            male_col = next((c for c in ['male_population'] if c in df.columns), None)
            female_col = next((c for c in ['female_population'] if c in df.columns), None)
            if male_col and female_col:
                df['population'] = pd.to_numeric(df[male_col], errors='coerce') + pd.to_numeric(df[female_col], errors='coerce')
                pop_col = 'population'
        
        df[pop_col] = pd.to_numeric(df[pop_col], errors='coerce')
        
        if 'pincode' in df.columns:
            df['pincode'] = df['pincode'].astype(str).str.zfill(6)
        
        for c in ['bio_raw_row_count', 'demo_raw_row_count', 'enroll_raw_row_count']:
            if c not in df.columns:
                df[c] = 0
            else:
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
        
        df['total_activity'] = df['bio_raw_row_count'] + df['demo_raw_row_count'] + df['enroll_raw_row_count']
        
        pincode_agg = df.groupby('pincode', as_index=False).agg(
            population=(pop_col, 'sum'),
            total_activity=('total_activity', 'sum')
        )
        
        pincode_agg.loc[pincode_agg['population'] <= 0, 'population'] = np.nan
        pincode_agg['population'].fillna(pincode_agg['population'].median(), inplace=True)
        pincode_agg['activity_per_100k'] = pincode_agg['total_activity'] / (pincode_agg['population'] / 100000)
        
        # Plot
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Cap at 99th percentile for readability
        cap_99 = pincode_agg['activity_per_100k'].quantile(0.99)
        data_capped = pincode_agg[pincode_agg['activity_per_100k'] <= cap_99]['activity_per_100k']
        
        ax.hist(data_capped, bins=50, color='steelblue', edgecolor='black', alpha=0.7)
        ax.set_xlabel('Activity per 100,000 population')
        ax.set_ylabel('Number of Pincodes')
        ax.set_title('Distribution of Aadhaar Activity Rates\n(capped at 99th percentile)')
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(OUT_DIR / "viz_activity_distribution.png", dpi=200, bbox_inches='tight')
        plt.close()
        logger.info("  Saved: viz_activity_distribution.png")
    except Exception as e:
        logger.warning(f"  Could not generate activity distribution plot: {e}")

def plot_top_anomalies():
    """Plot top anomalies by policy relevance."""
    logger.info("Generating top anomalies visualization")
    
    try:
        anomaly_df = pd.read_csv(OUT_DIR / "anomaly_list.csv")
        
        # Take top 15 for readability
        top_15 = anomaly_df.head(15).sort_values('policy_relevance_score', ascending=True)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        ax.barh(range(len(top_15)), top_15['policy_relevance_score'], color='darkred')
        ax.set_yticks(range(len(top_15)))
        ax.set_yticklabels([f"{pin} ({dist})" for pin, dist in zip(top_15['pincode'], top_15['district'])],
                          fontsize=9)
        ax.set_xlabel('Policy Relevance Score')
        ax.set_title('Top 15 Most Policy-Relevant Anomalies')
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(OUT_DIR / "viz_top_anomalies.png", dpi=200, bbox_inches='tight')
        plt.close()
        logger.info("  Saved: viz_top_anomalies.png")
    except Exception as e:
        logger.warning(f"  Could not generate anomalies plot: {e}")

def main():
    logger.info("=" * 60)
    logger.info("SUMMARY VISUALIZATIONS")
    logger.info("=" * 60)
    logger.info("Generating individual PNG plots (no combined grids)")
    
    # Generate all plots
    plot_imputation_distribution()
    plot_sensitivity_comparison()
    plot_activity_distribution()
    plot_top_anomalies()
    
    # Note: Other plots already generated by previous scripts:
    # - rural_urban_boxplot.png (from 03_rural_urban_stats.py)
    # - pop_activity_scatter.png (from 04_pop_activity_correlation.py)
    # - regression_diagnostics.png (from 04_pop_activity_correlation.py)
    # - district_desert_counts.png (from 06_district_verification.py)
    
    logger.info("\n" + "=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)
    logger.info("Individual visualizations generated:")
    
    expected_plots = [
        "viz_imputation_distribution.png",
        "viz_sensitivity_comparison.png",
        "viz_activity_distribution.png",
        "viz_top_anomalies.png",
        "rural_urban_boxplot.png",
        "pop_activity_scatter.png",
        "regression_diagnostics.png",
        "district_desert_counts.png"
    ]
    
    for plot_name in expected_plots:
        plot_path = OUT_DIR / plot_name
        if plot_path.exists():
            logger.info(f"  ✓ {plot_name}")
        else:
            logger.info(f"  ✗ {plot_name} (not found)")
    
    logger.info("\nSummary visualizations complete")

if __name__ == "__main__":
    main()
