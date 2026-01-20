"""
Outlier and Anomaly Detection

Purpose: Detect extreme activity_per_100k values using robust statistical methods:
         - IQR method (1.5× interquartile range)
         - MAD method (3× median absolute deviation)
         - Assign reason codes for policy-relevance
         - Cap output to top 100 most policy-relevant cases

Output: anomaly_list.csv (top 100 only)
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

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

def iqr_outliers(series, multiplier=1.5):
    """Detect outliers using IQR method."""
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - multiplier * iqr
    upper_bound = q3 + multiplier * iqr
    return (series < lower_bound) | (series > upper_bound)

def mad_outliers(series, multiplier=3):
    """Detect outliers using Median Absolute Deviation."""
    median = series.median()
    mad = np.median(np.abs(series - median))
    if mad == 0:
        return pd.Series([False] * len(series), index=series.index)
    lower_bound = median - multiplier * mad
    upper_bound = median + multiplier * mad
    return (series < lower_bound) | (series > upper_bound)

def assign_reason_code(row, global_median_activity, district_baseline):
    """
    Assign reason codes based on multiple factors.
    Priority order:
    1. Population imputation + extreme activity
    2. Very low activity (< 10% of district baseline)
    3. Very high activity (> 500% of district baseline)
    4. Geographic isolation (if applicable)
    """
    reasons = []
    
    # Check for extreme low activity
    if 'district_activity_per_100k' in row.index:
        district_baseline_val = row['district_activity_per_100k']
        if row['activity_per_100k'] < 0.1 * district_baseline_val:
            reasons.append("Sub-threshold activity (<10% of district)")
    
    # Check for extreme high activity
    if 'district_activity_per_100k' in row.index:
        if row['activity_per_100k'] > 5.0 * row['district_activity_per_100k']:
            reasons.append("Extreme high activity (>500% of district)")
    
    # Check for low absolute activity
    if row['total_activity'] < 50:
        reasons.append("Very low absolute activity (<50 records)")
    
    # Check for population concerns
    if row['population'] < 500:
        reasons.append("Very small population (<500)")
    
    # Default
    if not reasons:
        reasons.append("Statistical outlier (IQR/MAD)")
    
    return "; ".join(reasons)

def main():
    logger.info("=" * 60)
    logger.info("OUTLIER AND ANOMALY DETECTION")
    logger.info("=" * 60)
    logger.info("Detecting extreme activity_per_100k using IQR and MAD methods")
    logger.info("Output capped to top 100 most policy-relevant cases")
    
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
    
    # Get district baselines
    district_agg = pincode_agg.groupby('district', as_index=False).agg(
        population=('population', 'sum'),
        total_activity=('total_activity', 'sum')
    )
    district_agg['district_activity_per_100k'] = district_agg['total_activity'] / (district_agg['population'] / 100000)
    
    # Merge district baseline
    pincode_agg = pincode_agg.merge(
        district_agg[['district', 'district_activity_per_100k']],
        on='district',
        how='left'
    )
    
    # Detect outliers
    logger.info("\nDetecting outliers using IQR method")
    iqr_flags = iqr_outliers(pincode_agg['activity_per_100k'], multiplier=1.5)
    
    logger.info("Detecting outliers using MAD method")
    mad_flags = mad_outliers(pincode_agg['activity_per_100k'], multiplier=3)
    
    # Combine flags (OR logic - flagged by either method)
    pincode_agg['outlier_flag'] = iqr_flags | mad_flags
    
    logger.info(f"Outliers detected: {pincode_agg['outlier_flag'].sum():,} ({100 * pincode_agg['outlier_flag'].mean():.2f}%)")
    
    # Assign reason codes to outliers
    logger.info("\nAssigning reason codes to outliers")
    global_median_activity = pincode_agg['activity_per_100k'].median()
    
    outliers = pincode_agg[pincode_agg['outlier_flag']].copy()
    outliers['reason_code'] = outliers.apply(
        lambda row: assign_reason_code(row, global_median_activity, pincode_agg),
        axis=1
    )
    
    # Compute policy relevance score
    # Higher score = more policy-relevant
    # Factors: extreme deviation from district, low absolute activity, large population
    outliers['policy_relevance_score'] = (
        np.abs(outliers['activity_per_100k'] - outliers['district_activity_per_100k']) *
        np.log1p(outliers['population']) /
        (1 + outliers['total_activity'])  # Inverse of activity - lower activity = higher relevance
    )
    
    # Sort by policy relevance and take top 100
    outliers_sorted = outliers.sort_values('policy_relevance_score', ascending=False)
    top_100 = outliers_sorted.head(100)
    
    # Prepare output
    anomaly_output = top_100[[
        'pincode', 'district', 'state', 'population', 'total_activity',
        'activity_per_100k', 'district_activity_per_100k', 'outlier_flag',
        'reason_code', 'policy_relevance_score'
    ]].copy()
    
    # Save
    output_path = OUT_DIR / "anomaly_list.csv"
    anomaly_output.to_csv(output_path, index=False)
    logger.info(f"\nSaved top 100 anomalies to {output_path}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total outliers detected: {len(outliers):,}")
    logger.info(f"Top 100 most policy-relevant anomalies exported")
    logger.info(f"\nReason code distribution (top 100):")
    
    # Count reason codes (they can overlap)
    reason_counts = {}
    for reasons in top_100['reason_code']:
        for reason in reasons.split('; '):
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
    
    for reason, count in sorted(reason_counts.items(), key=lambda x: x[1], reverse=True):
        logger.info(f"  {reason}: {count}")
    
    logger.info(f"\nTop 5 most policy-relevant anomalies:")
    for idx, row in top_100.head(5).iterrows():
        logger.info(f"  {row['pincode']} ({row['district']}, {row['state']})")
        logger.info(f"    Activity: {row['activity_per_100k']:.1f} per 100k (district avg: {row['district_activity_per_100k']:.1f})")
        logger.info(f"    Reason: {row['reason_code']}")
    
    logger.info("\nOutlier and anomaly detection complete")

if __name__ == "__main__":
    main()
