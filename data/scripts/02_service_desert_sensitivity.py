"""
Service Desert Sensitivity Analysis

Purpose: Recompute service desert counts using thresholds 40%, 50%, 60% of district
         baseline. The 50% threshold is the PRIMARY operational definition; 40% and 60%
         are treated strictly as robustness checks.

Output: service_desert_sensitivity.csv
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

def compute_service_deserts(pincode_agg, district_agg, threshold_pct):
    """
    Compute service desert count at given threshold.
    
    A pincode is a service desert if:
    - Rural area
    - activity_per_100k < (threshold_pct / 100) * district_activity_per_100k
    - population >= district median population
    """
    # Merge district baseline
    pincode_with_baseline = pincode_agg.merge(
        district_agg[['district', 'activity_per_100k', 'population']].rename(
            columns={
                'activity_per_100k': 'district_activity_per_100k',
                'population': 'district_population'
            }
        ),
        on='district',
        how='left'
    )
    
    # Compute district median population
    district_pop_median = pincode_agg.groupby('district')['population'].median()
    pincode_with_baseline['district_median_pop'] = pincode_with_baseline['district'].map(district_pop_median)
    
    # Apply threshold
    threshold_decimal = threshold_pct / 100.0
    is_desert = (
        (pincode_with_baseline['urban_flag'] == 'rural') &
        (pincode_with_baseline['activity_per_100k'] < threshold_decimal * pincode_with_baseline['district_activity_per_100k']) &
        (pincode_with_baseline['population'] >= pincode_with_baseline['district_median_pop'])
    )
    
    desert_count = is_desert.sum()
    
    # Compute relative gap for deserts
    desert_pincodes = pincode_with_baseline[is_desert]
    mean_gap_pct = (
        (desert_pincodes['activity_per_100k'] - desert_pincodes['district_activity_per_100k']) /
        desert_pincodes['district_activity_per_100k'] * 100
    ).mean() if desert_count > 0 else np.nan
    
    # Get affected pincode list
    pincodes_affected = desert_pincodes['pincode'].tolist()
    
    return {
        'threshold_pct': threshold_pct,
        'desert_count': desert_count,
        'mean_gap_pct': mean_gap_pct,
        'pincodes_affected': pincodes_affected
    }

def main():
    logger.info("=" * 60)
    logger.info("SERVICE DESERT SENSITIVITY ANALYSIS")
    logger.info("=" * 60)
    logger.info("Primary threshold: 50% (operational definition)")
    logger.info("Robustness checks: 40%, 60%")
    
    # Load data
    logger.info(f"Loading data from {INPUT_CSV}")
    df = pd.read_csv(INPUT_CSV, low_memory=False)
    logger.info(f"Loaded {len(df):,} rows")
    
    # Standardize columns
    df.columns = [c.strip().lower().replace(' ', '_').replace('-', '_') for c in df.columns]
    
    # Get population column
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
    
    # Ensure pincode is string
    if 'pincode' in df.columns:
        df['pincode'] = df['pincode'].astype(str).str.zfill(6)
    
    # Get urban flag
    if 'urban_flag' not in df.columns:
        if 'urban_share' in df.columns:
            urban_share = pd.to_numeric(df['urban_share'], errors='coerce')
            df['urban_flag'] = 'unknown'
            df.loc[urban_share >= 0.5, 'urban_flag'] = 'urban'
            df.loc[urban_share < 0.5, 'urban_flag'] = 'rural'
        else:
            df['urban_flag'] = 'unknown'
    
    # Get activity counts
    for c in ['bio_raw_row_count', 'demo_raw_row_count', 'enroll_raw_row_count']:
        if c not in df.columns:
            df[c] = 0
        else:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
    
    df['total_activity'] = df['bio_raw_row_count'] + df['demo_raw_row_count'] + df['enroll_raw_row_count']
    
    # Aggregate to pincode level
    logger.info("Aggregating to pincode level")
    pincode_agg = df.groupby('pincode', as_index=False).agg(
        district=('district', 'first'),
        state=('state', 'first'),
        population=(pop_col, 'sum'),
        urban_flag=('urban_flag', 'first'),
        total_activity=('total_activity', 'sum')
    )
    
    # Handle zero/negative population
    pincode_agg.loc[pincode_agg['population'] <= 0, 'population'] = np.nan
    global_median = pincode_agg['population'].median()
    pincode_agg['population'].fillna(global_median, inplace=True)
    
    # Compute activity per 100k
    pincode_agg['activity_per_100k'] = pincode_agg['total_activity'] / (pincode_agg['population'] / 100000)
    
    # District aggregates
    logger.info("Computing district baselines")
    district_agg = pincode_agg.groupby('district', as_index=False).agg(
        state=('state', 'first'),
        population=('population', 'sum'),
        total_activity=('total_activity', 'sum')
    )
    district_agg['activity_per_100k'] = district_agg['total_activity'] / (district_agg['population'] / 100000)
    
    # Test thresholds
    thresholds = [40, 50, 60]
    results = []
    
    for threshold in thresholds:
        logger.info(f"\nTesting threshold: {threshold}%")
        result = compute_service_deserts(pincode_agg, district_agg, threshold)
        results.append(result)
        logger.info(f"  Desert count: {result['desert_count']:,}")
        logger.info(f"  Mean gap: {result['mean_gap_pct']:.2f}%")
    
    # Create summary DataFrame (without pincode lists)
    sensitivity_summary = pd.DataFrame([
        {
            'threshold_pct': r['threshold_pct'],
            'desert_count': r['desert_count'],
            'mean_gap_pct': r['mean_gap_pct']
        }
        for r in results
    ])
    
    # Save
    output_path = OUT_DIR / "service_desert_sensitivity.csv"
    sensitivity_summary.to_csv(output_path, index=False)
    logger.info(f"\nSaved sensitivity analysis to {output_path}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Primary definition (50%): {results[1]['desert_count']:,} service deserts")
    logger.info(f"Robustness check (40%): {results[0]['desert_count']:,} service deserts")
    logger.info(f"Robustness check (60%): {results[2]['desert_count']:,} service deserts")
    
    pct_change_low = 100 * (results[0]['desert_count'] - results[1]['desert_count']) / results[1]['desert_count']
    pct_change_high = 100 * (results[2]['desert_count'] - results[1]['desert_count']) / results[1]['desert_count']
    
    logger.info(f"Variation from 50% baseline:")
    logger.info(f"  40% threshold: {pct_change_low:+.1f}% change")
    logger.info(f"  60% threshold: {pct_change_high:+.1f}% change")
    
    logger.info("\nService desert sensitivity analysis complete")

if __name__ == "__main__":
    main()
