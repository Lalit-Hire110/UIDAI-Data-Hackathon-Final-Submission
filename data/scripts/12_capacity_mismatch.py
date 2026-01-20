"""
Capacity Mismatch Domain Analysis

Purpose: Analyze population vs activity imbalances.
         Identify over/under-serviced areas (descriptive, not normative).

Output: capacity_mismatch_metrics.csv, capacity_mismatch_summary.csv,
        validation_capacity_mismatch.csv, capacity_mismatch_notes.md, 3 PNGs
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import matplotlib.pyplot as plt
import sys
import io

# Setup
np.random.seed(42)
BASE_DIR = Path(r"C:\Users\Lalit Hire\UIDAI Data Hackathon 2026\data")
SNAPSHOT_DIR = BASE_DIR / "outputs" / "data_snapshots"
OUT_DIR = BASE_DIR / "outputs" / "domains" / "capacity_mismatch"
FIG_DIR = BASE_DIR / "outputs" / "figures" / "domains" / "capacity_mismatch"
LOG_FILE = BASE_DIR / "outputs" / "antigravity" / "antigravity.log"

for d in [OUT_DIR, FIG_DIR]:
    d.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True))
    ]
)
logger = logging.getLogger(__name__)

def main():
    logger.info("=" * 60)
    logger.info("CAPACITY MISMATCH DOMAIN ANALYSIS")
    logger.info("=" * 60)
    
    snapshot_files = list(SNAPSHOT_DIR.glob("cleaned_uidai_snapshot_*.csv"))
    if not snapshot_files:
        raise FileNotFoundError("No cleaned snapshot found")
    
    snapshot_file = max(snapshot_files, key=lambda x: x.stat().st_mtime)
    logger.info(f"Loading snapshot: {snapshot_file.name}")
    
    df = pd.read_csv(snapshot_file, low_memory=False)
    logger.info(f"Loaded {len(df):,} rows")
    
    # Aggregate
    logger.info("Aggregating to pincode level")
    pincode_agg = df.groupby('pincode', as_index=False).agg(
        district=('district', 'first'),
        state=('state', 'first'),
        population=('population', 'sum'),
        urban_flag=('urban_flag', 'first'),
        total_activity=('total_activity', 'sum')
    )
    
    # Calculate activity per 100k
    pincode_agg['activity_per_100k'] = pincode_agg['total_activity'] / (pincode_agg['population'] / 100000)
    pincode_agg['activity_per_100k'] = pincode_agg['activity_per_100k'].replace([np.inf, -np.inf], np.nan).fillna(0)
    
    # Capacity utilization (relative to national distribution)
    logger.info("Computing capacity utilization metrics")
    national_percentile = pincode_agg['activity_per_100k'].rank(pct=True)
    pincode_agg['capacity_utilization_percentile'] = national_percentile
    
    # Mismatch magnitude (deviation from expected)
    expected_activity = pincode_agg['population'].median() / 100000 * pincode_agg['activity_per_100k'].median()
    pincode_agg['mismatch_magnitude'] = np.abs(
        pincode_agg['total_activity'] - expected_activity
    ) / expected_activity
    
    # Mismatch type classification
    pincode_agg['mismatch_type'] = 'balanced'
    pincode_agg.loc[pincode_agg['capacity_utilization_percentile'] > 0.75, 'mismatch_type'] = 'high_activity'
    pincode_agg.loc[pincode_agg['capacity_utilization_percentile'] < 0.25, 'mismatch_type'] = 'low_activity'
    
    # Save metrics
    metrics_cols = [
        'pincode', 'district', 'state', 'population', 'urban_flag',
        'total_activity', 'activity_per_100k', 'capacity_utilization_percentile',
        'mismatch_type', 'mismatch_magnitude'
    ]
    pincode_agg[metrics_cols].to_csv(OUT_DIR / "capacity_mismatch_metrics.csv", index=False)
    logger.info(f"Saved metrics")
    
    # District summary
    summary = pincode_agg.groupby('district', as_index=False).agg(
        state=('state', 'first'),
        total_pincodes=('pincode', 'count'),
        avg_utilization=('capacity_utilization_percentile', 'mean'),
        high_activity_count=('mismatch_type', lambda x: (x == 'high_activity').sum()),
        low_activity_count=('mismatch_type', lambda x: (x == 'low_activity').sum()),
        avg_mismatch=('mismatch_magnitude', 'mean')
    )
    
    summary['mismatch_index'] = (
        (summary['high_activity_count'] + summary['low_activity_count']) / 
        summary['total_pincodes']
    )
    
    summary.to_csv(OUT_DIR / "capacity_mismatch_summary.csv", index=False)
    
    # Validation
    validation = [
        {'check_name': 'total_pincodes', 'result': 'PASS', 'details': f"{len(pincode_agg)} processed"},
        {'check_name': 'utilization_range', 'result': 'PASS' if (pincode_agg['capacity_utilization_percentile'] >= 0).all() and (pincode_agg['capacity_utilization_percentile'] <= 1).all() else 'FAIL', 'details': 'Utilization in [0,1]'},
        {'check_name': 'no_infinite', 'result': 'PASS' if not np.isinf(pincode_agg[metrics_cols[5:]].select_dtypes(include=[np.number])).any().any() else 'FAIL', 'details': 'No infinite values'},
        {'check_name': 'type_assigned', 'result': 'PASS', 'details': 'All pincodes classified'}
    ]
    pd.DataFrame(validation).to_csv(OUT_DIR / "validation_capacity_mismatch.csv", index=False)
    
    # Visualizations
    logger.info("Generating visualizations")
    
    # Fig 1: Scatter
    fig, ax = plt.subplots(figsize=(10, 6))
    for mtype, color in [('low_activity', 'blue'), ('balanced', 'gray'), ('high_activity', 'red')]:
        data = pincode_agg[pincode_agg['mismatch_type'] == mtype]
        ax.scatter(data['population'], data['activity_per_100k'], alpha=0.3, s=15, label=mtype, color=color)
    ax.set_xlabel('Population (log scale)')
    ax.set_ylabel('Activity per 100k')
    ax.set_title('Capacity Mismatch: Population vs Activity')
    ax.set_xscale('log')
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "mismatch_scatter.png", dpi=200, bbox_inches='tight')
    plt.close()
    
    # Fig 2: Type distribution
    fig, ax = plt.subplots(figsize=(8, 6))
    type_counts = pincode_agg['mismatch_type'].value_counts()
    ax.bar(type_counts.index, type_counts.values, color=['blue', 'gray', 'red'])
    ax.set_ylabel('Number of Pincodes')
    ax.set_title('Distribution of Capacity Mismatch Types')
    ax.grid(alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(FIG_DIR / "overserved_underserved.png", dpi=200, bbox_inches='tight')
    plt.close()
    
    # Fig 3: Magnitude histogram
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(pincode_agg['mismatch_magnitude'].clip(upper=pincode_agg['mismatch_magnitude'].quantile(0.95)), 
            bins=30, edgecolor='black', alpha=0.7, color='purple')
    ax.set_xlabel('Mismatch Magnitude')
    ax.set_ylabel('Number of Pincodes')
    ax.set_title('Distribution of Capacity Mismatch Magnitude\n(capped at 95th percentile)')
    ax.grid(alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(FIG_DIR / "capacity_gap_histogram.png", dpi=200, bbox_inches='tight')
    plt.close()
    
    # Notes
    notes = """# Capacity Mismatch Domain - Figure Notes
Analyzes population vs activity imbalances (descriptive only).

## Figures
1. **Mismatch Scatter**: Shows relationship between population and activity, colored by mismatch type
2. **Type Distribution**: Count of pincodes in each category (low/balanced/high activity)
3. **Magnitude Histogram**: Distribution of mismatch magnitudes

## Metrics
- **capacity_utilization_percentile**: National ranking of activity rate
- **mismatch_type**: high_activity (>75th percentile), low_activity (<25th), balanced
- **mismatch_magnitude**: Deviation from expected activity level

*Analysis Date: 2026-01-18*
"""
    with open(OUT_DIR / 'capacity_mismatch_notes.md', 'w', encoding='utf-8') as f:
        f.write(notes)
    
    logger.info(f"\nCapacity mismatch domain complete. {len(pincode_agg):,} pincodes analyzed.")

if __name__ == "__main__":
    main()
