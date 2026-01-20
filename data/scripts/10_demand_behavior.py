"""
Demand Behavior Domain Analysis

Purpose: Analyze service type preferences and demand patterns.
         - Shannon entropy normalized to [0,1] range
         - Described as SERVICE-TYPE DIVERSITY (not quality)
         - Urban vs rural demand comparisons

Output: demand_behavior_metrics.csv, demand_behavior_summary.csv,
        validation_demand_behavior.csv, demand_behavior_notes.md, 3 PNGs
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import matplotlib.pyplot as plt
from scipy.stats import entropy
import sys
import io

# Setup
np.random.seed(42)
BASE_DIR = Path(r"C:\Users\Lalit Hire\UIDAI Data Hackathon 2026\data")
SNAPSHOT_DIR = BASE_DIR / "outputs" / "data_snapshots"
OUT_DIR = BASE_DIR / "outputs" / "domains" / "demand_behavior"
FIG_DIR = BASE_DIR / "outputs" / "figures" / "domains" / "demand_behavior"
LOG_FILE = BASE_DIR / "outputs" / "antigravity" / "antigravity.log"

# Create directories
for d in [OUT_DIR, FIG_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Configure logging with UTF-8
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True))
    ]
)
logger = logging.getLogger(__name__)

def normalized_shannon_entropy(bio, demo, enroll):
    """
    Compute Shannon entropy normalized to [0,1] range.
    Measures service-type DIVERSITY, not quality.
    
    Returns 0 for complete concentration, 1 for perfect balance.
    """
    total = bio + demo + enroll
    if total == 0:
        return 0
    
    probs = np.array([bio, demo, enroll]) / total
    probs = probs[probs > 0]  # Remove zeros
    
    # Shannon entropy
    h = entropy(probs, base=3)  # Base 3 for 3 categories
    
    # Normalized to [0,1]: divide by max entropy (log_3(3) = 1)
    return h

def main():
    logger.info("=" * 60)
    logger.info("DEMAND BEHAVIOR DOMAIN ANALYSIS")
    logger.info("=" * 60)
    logger.info("Shannon entropy normalized to [0,1]")
    logger.info("Described as service-type diversity, NOT quality")
    
    # Find latest snapshot
    snapshot_files = list(SNAPSHOT_DIR.glob("cleaned_uidai_snapshot_*.csv"))
    if not snapshot_files:
        raise FileNotFoundError("No cleaned snapshot found")
    
    snapshot_file = max(snapshot_files, key=lambda x: x.stat().st_mtime)
    logger.info(f"Loading snapshot: {snapshot_file.name}")
    
    # Load data
    df = pd.read_csv(snapshot_file, low_memory=False)
    logger.info(f"Loaded {len(df):,} rows")
    
    # Aggregate to pincode level
    logger.info("Aggregating to pincode level")
    pincode_agg = df.groupby('pincode', as_index=False).agg(
        district=('district', 'first'),
        state=('state', 'first'),
        population=('population', 'sum'),
        urban_flag=('urban_flag', 'first'),
        bio_count=('bio_raw_row_count', 'sum'),
        demo_count=('demo_raw_row_count', 'sum'),
        enroll_count=('enroll_raw_row_count', 'sum'),
        total_activity=('total_activity', 'sum')
    )
    
    # Compute ratios
    logger.info("Computing service type ratios")
    pincode_agg['bio_ratio'] = pincode_agg['bio_count'] / pincode_agg['total_activity'].replace(0, np.nan)
    pincode_agg['demo_ratio'] = pincode_agg['demo_count'] / pincode_agg['total_activity'].replace(0, np.nan)
    pincode_agg['enroll_ratio'] = pincode_agg['enroll_count'] / pincode_agg['total_activity'].replace(0, np.nan)
    
    # Fill NaN for pincodes with zero activity
    pincode_agg['bio_ratio'].fillna(0, inplace=True)
    pincode_agg['demo_ratio'].fillna(0, inplace=True)
    pincode_agg['enroll_ratio'].fillna(0, inplace=True)
    
    # Dominant service type
    pincode_agg['dominant_service_type'] = pincode_agg[['bio_ratio', 'demo_ratio', 'enroll_ratio']].idxmax(axis=1)
    pincode_agg['dominant_service_type'] = pincode_agg['dominant_service_type'].str.replace('_ratio', '')
    
    # Demand diversity score (normalized Shannon entropy)
    logger.info("Computing demand diversity scores (normalized Shannon entropy)")
    pincode_agg['demand_diversity_score'] = pincode_agg.apply(
        lambda row: normalized_shannon_entropy(row['bio_count'], row['demo_count'], row['enroll_count']),
        axis=1
    )
    
    logger.info(f"Demand diversity range: [{pincode_agg['demand_diversity_score'].min():.3f}, {pincode_agg['demand_diversity_score'].max():.3f}]")
    
    # Save metrics
    metrics_cols = [
        'pincode', 'district', 'state', 'population', 'urban_flag',
        'total_activity', 'bio_count', 'demo_count', 'enroll_count',
        'bio_ratio', 'demo_ratio', 'enroll_ratio',
        'dominant_service_type', 'demand_diversity_score'
    ]
    pincode_agg[metrics_cols].to_csv(OUT_DIR / "demand_behavior_metrics.csv", index=False)
    logger.info(f"Saved metrics: {OUT_DIR / 'demand_behavior_metrics.csv'}")
    
    # District summary
    logger.info("Computing district summary")
    summary = pincode_agg.groupby('district', as_index=False).agg(
        state=('state', 'first'),
        total_pincodes=('pincode', 'count'),
        avg_bio_ratio=('bio_ratio', 'mean'),
        avg_demo_ratio=('demo_ratio', 'mean'),
        avg_enroll_ratio=('enroll_ratio', 'mean'),
        avg_diversity_score=('demand_diversity_score', 'mean'),
        total_activity=('total_activity', 'sum')
    )
    
    # Urban vs rural demand difference
    urban_rural = pincode_agg.groupby(['district', 'urban_flag'])[['bio_ratio', 'demo_ratio', 'enroll_ratio']].mean().reset_index()
    urban_data = urban_rural[urban_rural['urban_flag'] == 'urban'].set_index('district')
    rural_data = urban_rural[urban_rural['urban_flag'] == 'rural'].set_index('district')
    
    summary['urban_rural_bio_diff'] = summary['district'].map(
        lambda d: urban_data.loc[d, 'bio_ratio'] - rural_data.loc[d, 'bio_ratio'] if d in urban_data.index and d in rural_data.index else np.nan
    )
    
    # Demand concentration index (Herfindahl)
    summary['demand_concentration_index'] = summary.apply(
        lambda row: row['avg_bio_ratio']**2 + row['avg_demo_ratio']**2 + row['avg_enroll_ratio']**2,
        axis=1
    )
    
    summary.to_csv(OUT_DIR / "demand_behavior_summary.csv", index=False)
    logger.info(f"Saved summary: {OUT_DIR / 'demand_behavior_summary.csv'}")
    
    # Validation checks
    logger.info("Running validation checks")
    validation = []
    
    # Check 1: Total pincodes
    validation.append({
        'check_name': 'total_pincodes',
        'result': 'PASS',
        'details': f"{len(pincode_agg)} pincodes processed"
    })
    
    # Check 2: Ratio sums to 1
    ratio_sum = (pincode_agg['bio_ratio'] + pincode_agg['demo_ratio'] + pincode_agg['enroll_ratio']).round(2)
    ratio_check = ((ratio_sum == 1.0) | (ratio_sum == 0.0)).all()
    validation.append({
        'check_name': 'ratios_sum_to_one',
        'result': 'PASS' if ratio_check else 'FAIL',
        'details': 'All non-zero ratios sum to 1.0' if ratio_check else 'Some ratios do not sum to 1.0'
    })
    
    # Check 3: Diversity score in [0,1]
    diversity_range = (
        (pincode_agg['demand_diversity_score'] >= 0).all() and
        (pincode_agg['demand_diversity_score'] <= 1).all()
    )
    validation.append({
        'check_name': 'diversity_score_range',
        'result': 'PASS' if diversity_range else 'FAIL',
        'details': 'Diversity scores in [0,1]' if diversity_range else 'Diversity scores outside [0,1]'
    })
    
    # Check 4: No infinite values
    inf_check = np.isinf(pincode_agg[metrics_cols[5:]].select_dtypes(include=[np.number])).any().any()
    validation.append({
        'check_name': 'no_infinite_values',
        'result': 'FAIL' if inf_check else 'PASS',
        'details': 'Infinite values detected' if inf_check else 'All metrics finite'
    })
    
    pd.DataFrame(validation).to_csv(OUT_DIR / "validation_demand_behavior.csv", index=False)
    logger.info(f"Saved validation: {OUT_DIR / 'validation_demand_behavior.csv'}")
    
    # Visualizations
    logger.info("Generating visualizations")
    
    # Fig 1: Service type distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    service_counts = pincode_agg['dominant_service_type'].value_counts()
    ax.bar(service_counts.index, service_counts.values, color=['steelblue', 'darkorange', 'forestgreen'])
    ax.set_xlabel('Dominant Service Type')
    ax.set_ylabel('Number of Pincodes')
    ax.set_title('Distribution of Dominant Service Types Across Pincodes')
    ax.grid(alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(FIG_DIR / "service_type_distribution.png", dpi=200, bbox_inches='tight')
    plt.close()
    
    # Fig 2: Urban vs rural preferences
    fig, ax = plt.subplots(figsize=(10, 6))
    urban_avg = pincode_agg[pincode_agg['urban_flag'] == 'urban'][['bio_ratio', 'demo_ratio', 'enroll_ratio']].mean()
    rural_avg = pincode_agg[pincode_agg['urban_flag'] == 'rural'][['bio_ratio', 'demo_ratio', 'enroll_ratio']].mean()
    
    x = np.arange(3)
    width = 0.35
    ax.bar(x - width/2, [urban_avg['bio_ratio'], urban_avg['demo_ratio'], urban_avg['enroll_ratio']], 
           width, label='Urban', color='steelblue')
    ax.bar(x + width/2, [rural_avg['bio_ratio'], rural_avg['demo_ratio'], rural_avg['enroll_ratio']], 
           width, label='Rural', color='darkorange')
    
    ax.set_xlabel('Service Type')
    ax.set_ylabel('Average Ratio')
    ax.set_title('Urban vs Rural Service Type Preferences')
    ax.set_xticks(x)
    ax.set_xticklabels(['Biometric', 'Demographic', 'Enrollment'])
    ax.legend()
    ax.grid(alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(FIG_DIR / "urban_rural_preferences.png", dpi=200, bbox_inches='tight')
    plt.close()
    
    # Fig 3: Demand diversity heatmap (binned)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(pincode_agg['demand_diversity_score'], bins=30, edgecolor='black', alpha=0.7, color='purple')
    ax.set_xlabel('Demand Diversity Score (normalized Shannon entropy)')
    ax.set_ylabel('Number of Pincodes')
    ax.set_title('Distribution of Service-Type Diversity Across Pincodes\n(0 = concentrated, 1 = balanced)')
    ax.grid(alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(FIG_DIR / "demand_intensity_heatmap.png", dpi=200, bbox_inches='tight')
    plt.close()
    
    logger.info(f"Saved 3 visualizations to {FIG_DIR}")
    
    # Notes
    notes = """# Demand Behavior Domain - Figure Notes

## Overview
This domain analyzes service type preferences and demand patterns across pincodes.

## Figures

### 1. Service Type Distribution (`service_type_distribution.png`)
**Description:** Bar chart showing the number of pincodes where each service type (biometric, demographic, enrollment) is dominant.

**Interpretation:** Indicates which service types are most commonly preferred across regions.

### 2. Urban vs Rural Preferences (`urban_rural_preferences.png`)
**Description:** Grouped bar chart comparing average service type ratios between urban and rural areas.

**Interpretation:** Reveals systematic differences in service preferences between settlement types.

### 3. Demand Diversity Distribution (`demand_intensity_heatmap.png`)
**Description:** Histogram of demand diversity scores (normalized Shannon entropy) across all pincodes.

**Interpretation:** 
- Scores near 0 indicate concentrated demand (one service type dominates)
- Scores near 1 indicate balanced demand (all service types used equally)
- This measures service-type DIVERSITY, not service quality

## Key Metrics

- **bio_ratio, demo_ratio, enroll_ratio**: Proportion of each service type
- **dominant_service_type**: The most-used service category
- **demand_diversity_score**: Normalized Shannon entropy [0,1]
  - 0 = complete concentration on one service type
  - 1 = perfect balance across all three types
  - **Interpretation**: Measures diversity of service usage, NOT service quality or adequacy

## Methodology

Shannon entropy is normalized to [0,1] by dividing by log₃(3) = 1 (maximum entropy for 3 categories). This creates a standardized diversity metric independent of the number of service types.

---
*Analysis Date: 2026-01-18*
"""
    
    with open(OUT_DIR / 'demand_behavior_notes.md', 'w', encoding='utf-8') as f:
        f.write(notes)
    
    logger.info(f"Saved notes: {OUT_DIR / 'demand_behavior_notes.md'}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total pincodes analyzed: {len(pincode_agg):,}")
    logger.info(f"Most common dominant service: {service_counts.index[0]} ({service_counts.values[0]:,} pincodes)")
    logger.info(f"Average demand diversity: {pincode_agg['demand_diversity_score'].mean():.3f}")
    logger.info("\nDemand behavior domain analysis complete")

if __name__ == "__main__":
    main()
