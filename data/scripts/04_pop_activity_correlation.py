"""
Population-Activity Correlation Analysis

Purpose: Analyze relationship between population and activity using:
         - Pearson & Spearman correlations
         - Scatter plot with LOWESS smoothing
         - Huber robust regression with diagnostics
         - EMPHASIS: Heteroskedasticity and non-normative interpretation
         - Correlation does NOT imply service adequacy or equity

Output: pop_activity_stats.json, pop_activity_scatter.png, regression_diagnostics.png
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import json
from scipy import stats
import matplotlib.pyplot as plt
from statsmodels.nonparametric.smoothers_lowess import lowess
from statsmodels.robust.robust_linear_model import RLM
import statsmodels.api as sm

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

def main():
    logger.info("=" * 60)
    logger.info("POPULATION-ACTIVITY CORRELATION ANALYSIS")
    logger.info("=" * 60)
    logger.info("WARNING: Correlation does NOT imply service adequacy or equity")
    logger.info("Emphasis on heteroskedasticity and descriptive interpretation only")
    
    # Load data
    logger.info(f"\nLoading data from {INPUT_CSV}")
    df = pd.read_csv(INPUT_CSV, low_memory=False)
    logger.info(f"Loaded {len(df):,} rows")
    
    # Standardize columns
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
    
    # Ensure pincode
    if 'pincode' in df.columns:
        df['pincode'] = df['pincode'].astype(str).str.zfill(6)
    
    # Activity counts
    for c in ['bio_raw_row_count', 'demo_raw_row_count', 'enroll_raw_row_count']:
        if c not in df.columns:
            df[c] = 0
        else:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
    
    df['total_activity'] = df['bio_raw_row_count'] + df['demo_raw_row_count'] + df['enroll_raw_row_count']
    
    # Aggregate to pincode
    logger.info("Aggregating to pincode level")
    pincode_agg = df.groupby('pincode', as_index=False).agg(
        district=('district', 'first'),
        state=('state', 'first'),
        population=(pop_col, 'sum'),
        total_activity=('total_activity', 'sum')
    )
    
    # Fix population
    pincode_agg.loc[pincode_agg['population'] <= 0, 'population'] = np.nan
    global_median = pincode_agg['population'].median()
    pincode_agg['population'].fillna(global_median, inplace=True)
    
    # Activity per 100k
    pincode_agg['activity_per_100k'] = pincode_agg['total_activity'] / (pincode_agg['population'] / 100000)
    
    # Remove any infinite or NaN values
    analysis_df = pincode_agg[
        np.isfinite(pincode_agg['population']) & 
        np.isfinite(pincode_agg['activity_per_100k']) &
        (pincode_agg['population'] > 0)
    ].copy()
    
    logger.info(f"Analysis dataset: {len(analysis_df):,} pincodes")
    
    # Compute correlations
    logger.info("\nComputing correlation coefficients")
    pearson_r, pearson_p = stats.pearsonr(analysis_df['population'], analysis_df['activity_per_100k'])
    spearman_r, spearman_p = stats.spearmanr(analysis_df['population'], analysis_df['activity_per_100k'])
    
    logger.info(f"Pearson r: {pearson_r:.4f} (p={pearson_p:.4e})")
    logger.info(f"Spearman ρ: {spearman_r:.4f} (p={spearman_p:.4e})")
    
    # Huber robust regression
    logger.info("\nFitting Huber robust regression")
    X = sm.add_constant(analysis_df['population'])
    y = analysis_df['activity_per_100k']
    
    huber_model = RLM(y, X, M=sm.robust.norms.HuberT()).fit()
    
    # Get fitted values and residuals
    fitted = huber_model.fittedvalues
    residuals = huber_model.resid
    
    # Heteroskedasticity test (Breusch-Pagan)
    from statsmodels.stats.diagnostic import het_breuschpagan
    bp_test = het_breuschpagan(residuals, X)
    bp_statistic, bp_pvalue = bp_test[0], bp_test[1]
    
    logger.info(f"Breusch-Pagan heteroskedasticity test:")
    logger.info(f"  Statistic: {bp_statistic:.4f}")
    logger.info(f"  P-value: {bp_pvalue:.4e}")
    if bp_pvalue < 0.05:
        logger.info("  Result: SIGNIFICANT heteroskedasticity detected (p < 0.05)")
    else:
        logger.info("  Result: No significant heteroskedasticity")
    
    # Save statistics
    stats_output = {
        "note": "Correlation does NOT imply service adequacy or equity. Descriptive only.",
        "n_pincodes": int(len(analysis_df)),
        "pearson_correlation": {
            "r": float(pearson_r),
            "p_value": float(pearson_p)
        },
        "spearman_correlation": {
            "rho": float(spearman_r),
            "p_value": float(spearman_p)
        },
        "huber_robust_regression": {
            "intercept": float(huber_model.params[0]),
            "slope": float(huber_model.params[1]),
            "scale": float(huber_model.scale)
        },
        "heteroskedasticity_test": {
            "breusch_pagan_statistic": float(bp_statistic),
            "breusch_pagan_p_value": float(bp_pvalue),
            "interpretation": "Significant heteroskedasticity detected" if bp_pvalue < 0.05 else "No significant heteroskedasticity"
        }
    }
    
    stats_path = OUT_DIR / "pop_activity_stats.json"
    with open(stats_path, 'w') as f:
        json.dump(stats_output, f, indent=2)
    logger.info(f"\nSaved statistics to {stats_path}")
    
    # Scatter plot with LOWESS
    logger.info("\nGenerating scatter plot with LOWESS smoothing")
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Sample for visualization if too many points
    if len(analysis_df) > 5000:
        plot_df = analysis_df.sample(n=5000, random_state=42)
    else:
        plot_df = analysis_df
    
    ax.scatter(plot_df['population'], plot_df['activity_per_100k'], 
               alpha=0.3, s=10, color='steelblue', label='Pincodes')
    
    # LOWESS smoothing
    lowess_result = lowess(analysis_df['activity_per_100k'], analysis_df['population'], frac=0.1)
    ax.plot(lowess_result[:, 0], lowess_result[:, 1], 
            color='red', linewidth=2, label='LOWESS smooth')
    
    ax.set_xlabel('Population (log scale)')
    ax.set_ylabel('Activity per 100,000 population')
    ax.set_title('Population vs Activity Relationship\n(Correlation ≠ Service Adequacy)')
    ax.set_xscale('log')
    ax.legend()
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    scatter_path = OUT_DIR / "pop_activity_scatter.png"
    plt.savefig(scatter_path, dpi=200, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved scatter plot to {scatter_path}")
    
    # Regression diagnostics
    logger.info("Generating regression diagnostics")
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # 1. Residuals vs Fitted
    axes[0, 0].scatter(fitted, residuals, alpha=0.3, s=10)
    axes[0, 0].axhline(y=0, color='red', linestyle='--', linewidth=1)
    axes[0, 0].set_xlabel('Fitted values')
    axes[0, 0].set_ylabel('Residuals')
    axes[0, 0].set_title('Residuals vs Fitted\n(Check for heteroskedasticity)')
    axes[0, 0].grid(alpha=0.3)
    
    # 2. Q-Q plot
    stats.probplot(residuals, dist="norm", plot=axes[0, 1])
    axes[0, 1].set_title('Normal Q-Q Plot\n(Check for normality)')
    axes[0, 1].grid(alpha=0.3)
    
    # 3. Scale-Location
    standardized_resid = residuals / np.std(residuals)
    axes[1, 0].scatter(fitted, np.sqrt(np.abs(standardized_resid)), alpha=0.3, s=10)
    axes[1, 0].set_xlabel('Fitted values')
    axes[1, 0].set_ylabel('√|Standardized residuals|')
    axes[1, 0].set_title('Scale-Location Plot\n(Heteroskedasticity diagnostic)')
    axes[1, 0].grid(alpha=0.3)
    
    # 4. Residual histogram
    axes[1, 1].hist(residuals, bins=50, edgecolor='black', alpha=0.7)
    axes[1, 1].set_xlabel('Residuals')
    axes[1, 1].set_ylabel('Frequency')
    axes[1, 1].set_title('Residual Distribution')
    axes[1, 1].grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    diag_path = OUT_DIR / "regression_diagnostics.png"
    plt.savefig(diag_path, dpi=200, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved regression diagnostics to {diag_path}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Pearson correlation: {pearson_r:.4f}")
    logger.info(f"Spearman correlation: {spearman_r:.4f}")
    logger.info(f"Heteroskedasticity: {'PRESENT' if bp_pvalue < 0.05 else 'Not detected'}")
    logger.info("\nIMPORTANT: These correlations describe data patterns only.")
    logger.info("They do NOT imply service adequacy, equity, or normative conclusions.")
    logger.info("Heteroskedasticity indicates variance in service delivery across")
    logger.info("population scales, suggesting uneven infrastructure distribution.")
    
    logger.info("\nPopulation-activity correlation analysis complete")

if __name__ == "__main__":
    main()
