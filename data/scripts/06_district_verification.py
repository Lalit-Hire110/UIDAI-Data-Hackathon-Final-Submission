"""
District-Level Verification

Purpose: Re-aggregate service deserts by district and verify top 15 districts
         match prior notebook findings. Generates reproducible district count
         summary with desert ratio.

Output: district_deserts_top15.csv, district_desert_counts.png
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
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

def main():
    logger.info("=" * 60)
    logger.info("DISTRICT-LEVEL VERIFICATION")
    logger.info("=" * 60)
    logger.info("Verifying top 15 districts by service desert concentration")
    
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
    
    # District aggregates
    logger.info("Computing district baselines")
    district_agg = pincode_agg.groupby('district', as_index=False).agg(
        state=('state', 'first'),
        population=('population', 'sum'),
        total_activity=('total_activity', 'sum')
    )
    district_agg['activity_per_100k'] = district_agg['total_activity'] / (district_agg['population'] / 100000)
    
    # Merge district baseline
    pincode_with_baseline = pincode_agg.merge(
        district_agg[['district', 'activity_per_100k']].rename(
            columns={'activity_per_100k': 'district_activity_per_100k'}
        ),
        on='district',
        how='left'
    )
    
    # Compute district median population
    district_pop_median = pincode_agg.groupby('district')['population'].median()
    pincode_with_baseline['district_median_pop'] = pincode_with_baseline['district'].map(district_pop_median)
    
    # Apply service desert definition (50% threshold - PRIMARY operational definition)
    logger.info("\nApplying service desert definition (50% threshold)")
    is_desert = (
        (pincode_with_baseline['urban_flag'] == 'rural') &
        (pincode_with_baseline['activity_per_100k'] < 0.5 * pincode_with_baseline['district_activity_per_100k']) &
        (pincode_with_baseline['population'] >= pincode_with_baseline['district_median_pop'])
    )
    
    pincode_with_baseline['is_service_desert'] = is_desert
    
    logger.info(f"Total service deserts identified: {is_desert.sum():,}")
    
    # Aggregate by district
    logger.info("\nAggregating service deserts by district")
    district_deserts = pincode_with_baseline.groupby('district', as_index=False).agg(
        state=('state', 'first'),
        total_pincodes=('pincode', 'count'),
        rural_pincodes=('urban_flag', lambda x: (x == 'rural').sum()),
        desert_count=('is_service_desert', 'sum'),
        total_population=('population', 'sum'),
        desert_population=('population', lambda x: x[pincode_with_baseline.loc[x.index, 'is_service_desert']].sum())
    )
    
    # Compute desert ratio
    district_deserts['desert_ratio'] = district_deserts['desert_count'] / district_deserts['rural_pincodes'].replace(0, np.nan)
    
    # Sort by desert count and take top 15
    top_15 = district_deserts.sort_values('desert_count', ascending=False).head(15)
    
    # Save
    output_path = OUT_DIR / "district_deserts_top15.csv"
    top_15.to_csv(output_path, index=False)
    logger.info(f"\nSaved top 15 districts to {output_path}")
    
    # Create bar chart
    logger.info("Generating bar chart visualization")
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Sort for plotting
    plot_data = top_15.sort_values('desert_count', ascending=True)
    
    ax.barh(range(len(plot_data)), plot_data['desert_count'], color='steelblue')
    ax.set_yticks(range(len(plot_data)))
    ax.set_yticklabels(plot_data['district'])
    ax.set_xlabel('Number of Service Desert Pincodes')
    ax.set_title('Top 15 Districts by Service Desert Concentration\n(50% threshold, rural areas only)')
    ax.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plot_path = OUT_DIR / "district_desert_counts.png"
    plt.savefig(plot_path, dpi=200, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved bar chart to {plot_path}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("SUMMARY - TOP 15 DISTRICTS")
    logger.info("=" * 60)
    
    for idx, row in top_15.iterrows():
        logger.info(f"{row['district']} ({row['state']})")
        logger.info(f"  Service deserts: {row['desert_count']}")
        logger.info(f"  Rural pincodes: {row['rural_pincodes']}")
        logger.info(f"  Desert ratio: {row['desert_ratio']:.2%}")
        logger.info(f"  Affected population: {row['desert_population']:,.0f}")
        logger.info("")
    
    logger.info("District-level verification complete")

if __name__ == "__main__":
    main()
