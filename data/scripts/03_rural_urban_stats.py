"""
Rural vs Urban Statistical Validation

Purpose: Validate rural-urban activity disparity using:
         - Cohen's d effect size
         - Mann-Whitney U test (non-parametric due to non-normal distributions)
         - Bootstrap 95% CI for median difference (10,000 resamples)
         - Export median values for citation in final report

Output: rural_urban_comparison_stats.json, rural_urban_boxplot.png, 
        rural_urban_medians.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import json
from scipy import stats
import matplotlib.pyplot as plt

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

def cohens_d(group1, group2):
    """Calculate Cohen's d effect size."""
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    return (np.mean(group1) - np.mean(group2)) / pooled_std

def bootstrap_ci(group1, group2, n_boot=10000, ci=95):
    """Bootstrap confidence interval for median difference."""
    logger.info(f"Running bootstrap with {n_boot:,} resamples")
    
    differences = []
    for _ in range(n_boot):
        sample1 = np.random.choice(group1, size=len(group1), replace=True)
        sample2 = np.random.choice(group2, size=len(group2), replace=True)
        differences.append(np.median(sample1) - np.median(sample2))
    
    lower_percentile = (100 - ci) / 2
    upper_percentile = 100 - lower_percentile
    
    ci_lower = np.percentile(differences, lower_percentile)
    ci_upper = np.percentile(differences, upper_percentile)
    
    return ci_lower, ci_upper

def main():
    logger.info("=" * 60)
    logger.info("RURAL VS URBAN STATISTICAL VALIDATION")
    logger.info("=" * 60)
    
    # Load data
    logger.info(f"Loading data from {INPUT_CSV}")
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
    
    # Urban flag
    if 'urban_flag' not in df.columns:
        if 'urban_share' in df.columns:
            urban_share = pd.to_numeric(df['urban_share'], errors='coerce')
            df['urban_flag'] = 'unknown'
            df.loc[urban_share >= 0.5, 'urban_flag'] = 'urban'
            df.loc[urban_share < 0.5, 'urban_flag'] = 'rural'
        else:
            df['urban_flag'] = 'unknown'
    
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
        urban_flag=('urban_flag', 'first'),
        total_activity=('total_activity', 'sum')
    )
    
    # Fix population
    pincode_agg.loc[pincode_agg['population'] <= 0, 'population'] = np.nan
    global_median = pincode_agg['population'].median()
    pincode_agg['population'].fillna(global_median, inplace=True)
    
    # Activity per 100k
    pincode_agg['activity_per_100k'] = pincode_agg['total_activity'] / (pincode_agg['population'] / 100000)
    
    # Split by urban/rural
    rural = pincode_agg[pincode_agg['urban_flag'] == 'rural']['activity_per_100k'].values
    urban = pincode_agg[pincode_agg['urban_flag'] == 'urban']['activity_per_100k'].values
    
    logger.info(f"\nRural pincodes: {len(rural):,}")
    logger.info(f"Urban pincodes: {len(urban):,}")
    
    # Compute statistics
    logger.info("\nComputing effect size (Cohen's d)")
    effect_size = cohens_d(rural, urban)
    
    logger.info("Running Mann-Whitney U test")
    u_stat, p_value = stats.mannwhitneyu(rural, urban, alternative='two-sided')
    
    logger.info("Computing bootstrap 95% CI for median difference")
    ci_lower, ci_upper = bootstrap_ci(rural, urban, n_boot=10000, ci=95)
    
    # Medians for citation
    rural_median = np.median(rural)
    urban_median = np.median(urban)
    median_diff = rural_median - urban_median
    
    # Summary stats
    rural_mean = np.mean(rural)
    urban_mean = np.mean(urban)
    rural_std = np.std(rural, ddof=1)
    urban_std = np.std(urban, ddof=1)
    
    # Save stats to JSON
    stats_output = {
        "rural": {
            "n": int(len(rural)),
            "mean": float(rural_mean),
            "median": float(rural_median),
            "std": float(rural_std),
            "q25": float(np.percentile(rural, 25)),
            "q75": float(np.percentile(rural, 75))
        },
        "urban": {
            "n": int(len(urban)),
            "mean": float(urban_mean),
            "median": float(urban_median),
            "std": float(urban_std),
            "q25": float(np.percentile(urban, 25)),
            "q75": float(np.percentile(urban, 75))
        },
        "effect_size_cohens_d": float(effect_size),
        "mann_whitney_u_statistic": float(u_stat),
        "mann_whitney_p_value": float(p_value),
        "median_difference": float(median_diff),
        "bootstrap_95_ci": {
            "lower": float(ci_lower),
            "upper": float(ci_upper)
        }
    }
    
    stats_path = OUT_DIR / "rural_urban_comparison_stats.json"
    with open(stats_path, 'w') as f:
        json.dump(stats_output, f, indent=2)
    logger.info(f"\nSaved statistics to {stats_path}")
    
    # Save medians CSV for citation
    medians_df = pd.DataFrame([
        {'area_type': 'rural', 'median_activity_per_100k': rural_median, 'n_pincodes': len(rural)},
        {'area_type': 'urban', 'median_activity_per_100k': urban_median, 'n_pincodes': len(urban)}
    ])
    medians_path = OUT_DIR / "rural_urban_medians.csv"
    medians_df.to_csv(medians_path, index=False)
    logger.info(f"Saved medians CSV to {medians_path}")
    
    # Create boxplot
    logger.info("Generating boxplot visualization")
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Cap at 99th percentile for readability
    cap_99 = np.percentile(np.concatenate([rural, urban]), 99)
    rural_capped = rural[rural <= cap_99]
    urban_capped = urban[urban <= cap_99]
    
    ax.boxplot([rural_capped, urban_capped], labels=['Rural', 'Urban'], showfliers=False)
    ax.set_ylabel('Activity per 100,000 population')
    ax.set_title('Rural vs Urban Activity Distribution\n(capped at 99th percentile)')
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plot_path = OUT_DIR / "rural_urban_boxplot.png"
    plt.savefig(plot_path, dpi=200, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved boxplot to {plot_path}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Rural median activity: {rural_median:.2f} per 100k")
    logger.info(f"Urban median activity: {urban_median:.2f} per 100k")
    logger.info(f"Median difference: {median_diff:.2f} per 100k")
    logger.info(f"Cohen's d effect size: {effect_size:.3f}")
    logger.info(f"Mann-Whitney U p-value: {p_value:.4e}")
    logger.info(f"Bootstrap 95% CI: [{ci_lower:.2f}, {ci_upper:.2f}]")
    
    logger.info("\nRural vs urban statistical validation complete")

if __name__ == "__main__":
    main()
