"""
Service Deserts Domain Analysis

Purpose: Identify rural service deserts using LOCKED definitions from main notebook.
         - 50% district baseline threshold (PRIMARY, no alternatives)
         - Existing severity/priority logic (no new formulas)
         - Reproduce notebook methodology exactly

Output: service_deserts_metrics.csv, service_deserts_summary.csv, 
        validation_service_deserts.csv, service_deserts_notes.md, 3 PNGs
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import matplotlib.pyplot as plt
import sys

# Setup
np.random.seed(42)
BASE_DIR = Path(r"C:\Users\Lalit Hire\UIDAI Data Hackathon 2026\data")
SNAPSHOT_DIR = BASE_DIR / "outputs" / "data_snapshots"
OUT_DIR = BASE_DIR / "outputs" / "domains" / "service_deserts"
FIG_DIR = BASE_DIR / "outputs" / "figures" / "domains" / "service_deserts"
LOG_FILE = BASE_DIR / "outputs" / "antigravity" / "antigravity.log"

# Create directories
for d in [OUT_DIR, FIG_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Configure logging with UTF-8
import io
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
    logger.info("SERVICE DESERTS DOMAIN ANALYSIS")
    logger.info("=" * 60)
    logger.info("Using LOCKED definitions from main notebook")
    logger.info("Threshold: 50% district baseline (no alternatives)")
    
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
        total_activity=('total_activity', 'sum')
    )
    
    # Activity per 100k
    pincode_agg['activity_per_100k'] = pincode_agg['total_activity'] / (pincode_agg['population'] / 100000)
    
    # District baselines
    logger.info("Computing district baselines")
    district_agg = pincode_agg.groupby('district', as_index=False).agg(
        state=('state', 'first'),
        population=('population', 'sum'),
        total_activity=('total_activity', 'sum')
    )
    district_agg['district_activity_per_100k'] = district_agg['total_activity'] / (district_agg['population'] / 100000)
    
    # Merge baseline
    metrics = pincode_agg.merge(
        district_agg[['district', 'district_activity_per_100k']],
        on='district',
        how='left'
    )
    
    # District median population
    district_pop_median = pincode_agg.groupby('district')['population'].median()
    metrics['district_median_pop'] = metrics['district'].map(district_pop_median)
    
    # Apply LOCKED service desert definition (50% threshold)
    logger.info("Applying LOCKED desert definition (50% threshold)")
    metrics['is_service_desert'] = (
        (metrics['urban_flag'] == 'rural') &
        (metrics['activity_per_100k'] < 0.5 * metrics['district_activity_per_100k']) &
        (metrics['population'] >= metrics['district_median_pop'])
    )
    
    # Desert severity (deviation from baseline) - LOCKED formula
    metrics['desert_severity_score'] = np.where(
        metrics['is_service_desert'],
        -(metrics['activity_per_100k'] - metrics['district_activity_per_100k']),
        0
    )
    
    # Relative gap
    metrics['relative_gap_pct'] = (
        (metrics['activity_per_100k'] - metrics['district_activity_per_100k']) /
        metrics['district_activity_per_100k'] * 100
    )
    
    # Priority rank - LOCKED formula: severity * log(population)
    metrics['priority_score'] = (
        metrics['desert_severity_score'] * np.log1p(metrics['population'])
    )
    
    # Rank deserts
    desert_mask = metrics['is_service_desert']
    metrics['priority_rank'] = 0
    if desert_mask.sum() > 0:
        metrics.loc[desert_mask, 'priority_rank'] = (
            metrics.loc[desert_mask, 'priority_score']
            .rank(ascending=False, method='dense')
        )
    
    logger.info(f"Service deserts identified: {desert_mask.sum():,}")
    
    # Save pincode metrics
    metrics_cols = [
        'pincode', 'district', 'state', 'population', 'urban_flag',
        'total_activity', 'activity_per_100k', 'district_activity_per_100k',
        'is_service_desert', 'desert_severity_score', 'relative_gap_pct',
        'priority_score', 'priority_rank'
    ]
    metrics[metrics_cols].to_csv(OUT_DIR / "service_deserts_metrics.csv", index=False)
    logger.info(f"Saved metrics: {OUT_DIR / 'service_deserts_metrics.csv'}")
    
    # District summary
    logger.info("Computing district summary")
    summary = metrics.groupby('district', as_index=False).agg(
        state=('state', 'first'),
        total_pincodes=('pincode', 'count'),
        rural_pincodes=('urban_flag', lambda x: (x == 'rural').sum()),
        desert_count=('is_service_desert', 'sum'),
        total_population=('population', 'sum'),
        affected_population=('population', lambda x: x[metrics.loc[x.index, 'is_service_desert']].sum()),
        mean_severity=('desert_severity_score', lambda x: x[x > 0].mean() if (x > 0).any() else 0)
    )
    
    summary['desert_ratio'] = summary['desert_count'] / summary['rural_pincodes'].replace(0, np.nan)
    summary = summary.sort_values('desert_count', ascending=False)
    
    summary.to_csv(OUT_DIR / "service_deserts_summary.csv", index=False)
    logger.info(f"Saved summary: {OUT_DIR / 'service_deserts_summary.csv'}")
    
    # Validation checks
    logger.info("Running validation checks")
    validation = []
    
    # Check 1: Total pincodes
    validation.append({
        'check_name': 'total_pincodes',
        'result': 'PASS',
        'details': f"{len(metrics)} pincodes processed"
    })
    
    # Check 2: No infinite values
    inf_check = np.isinf(metrics[metrics_cols[6:]].select_dtypes(include=[np.number])).any().any()
    validation.append({
        'check_name': 'no_infinite_values',
        'result': 'FAIL' if inf_check else 'PASS',
        'details': 'Infinite values detected' if inf_check else 'All metrics finite'
    })
    
    # Check 3: Population coverage
    pop_missing = (metrics['population'] <= 0).sum()
    validation.append({
        'check_name': 'population_coverage',
        'result': 'FAIL' if pop_missing > 0 else 'PASS',
        'details': f"{pop_missing} pincodes with missing/zero population"
    })
    
    # Check 4: Metric ranges
    valid_ranges = (
        (metrics['desert_severity_score'] >= 0).all() and
        (metrics['activity_per_100k'] >= 0).all()
    )
    validation.append({
        'check_name': 'metric_range_valid',
        'result': 'PASS' if valid_ranges else 'FAIL',
        'details': 'Metrics within expected ranges' if valid_ranges else 'Invalid metric ranges'
    })
    
    pd.DataFrame(validation).to_csv(OUT_DIR / "validation_service_deserts.csv", index=False)
    logger.info(f"Saved validation: {OUT_DIR / 'validation_service_deserts.csv'}")
    
    # Visualizations
    logger.info("Generating visualizations")
    
    # Fig 1: Desert distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    desert_data = metrics[metrics['is_service_desert']]
    ax.hist(desert_data['relative_gap_pct'], bins=30, edgecolor='black', alpha=0.7, color='darkred')
    ax.set_xlabel('Relative Gap from District Baseline (%)')
    ax.set_ylabel('Number of Service Desert Pincodes')
    ax.set_title('Distribution of Service Desert Performance Gaps')
    ax.grid(alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(FIG_DIR / "desert_distribution.png", dpi=200, bbox_inches='tight')
    plt.close()
    
    # Fig 2: Severity by population
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(desert_data['population'], desert_data['desert_severity_score'], 
               alpha=0.5, s=30, color='darkred')
    ax.set_xlabel('Population (log scale)')
    ax.set_ylabel('Desert Severity Score')
    ax.set_title('Service Desert Severity vs Population Size')
    ax.set_xscale('log')
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "desert_severity_map.png", dpi=200, bbox_inches='tight')
    plt.close()
    
    # Fig 3: Top districts
    fig, ax = plt.subplots(figsize=(10, 8))
    top15 = summary.head(15).sort_values('desert_count', ascending=True)
    ax.barh(range(len(top15)), top15['desert_count'], color='darkred')
    ax.set_yticks(range(len(top15)))
    ax.set_yticklabels(top15['district'])
    ax.set_xlabel('Number of Service Desert Pincodes')
    ax.set_title('Top 15 Districts by Service Desert Concentration')
    ax.grid(alpha=0.3, axis='x')
    plt.tight_layout()
    plt.savefig(FIG_DIR / "top_districts_deserts.png", dpi=200, bbox_inches='tight')
    plt.close()
    
    logger.info(f"Saved 3 visualizations to {FIG_DIR}")
    
    # Notes
    notes = f"""# Service Deserts Domain - Figure Notes

## Overview
This domain identifies rural service deserts using the locked 50% district baseline threshold established in the main analysis.

## Figures

### 1. Desert Distribution (`desert_distribution.png`)
**Description:** Histogram showing the distribution of relative performance gaps for identified service desert pincodes.

**Interpretation:** Shows how far below their district baseline service deserts perform. More negative values indicate larger gaps.

### 2. Desert Severity Map (`desert_severity_map.png`)
**Description:** Scatter plot of desert severity scores against population size (log scale).

**Interpretation:** Larger populations with high severity scores represent higher-priority intervention targets.

### 3. Top Districts by Desert Concentration (`top_districts_deserts.png`)
**Description:** Horizontal bar chart of the 15 districts with the most service desert pincodes.

**Interpretation:** Districts with high counts may benefit from systemic interventions rather than pincode-specific actions.

## Key Metrics

- **is_service_desert**: Boolean flag applying the locked 50% threshold definition
- **desert_severity_score**: Absolute deviation from district baseline (higher = worse)
- **priority_score**: Population-weighted severity for intervention prioritization
- **relative_gap_pct**: Percentage gap from district average

## Methodology

Uses the established service desert definition:
- Rural classification
- Activity rate < 50% of district average
- Population ≥ district median population

No alternative thresholds or new ranking formulas introduced.

---
*Analysis Date: 2026-01-18*
"""
    
    with open(OUT_DIR / "service_deserts_notes.md", 'w', encoding='utf-8') as f:
        f.write(notes)
    
    logger.info(f"Saved notes: {OUT_DIR / 'service_deserts_notes.md'}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total pincodes analyzed: {len(metrics):,}")
    logger.info(f"Service deserts identified: {desert_mask.sum():,}")
    logger.info(f"Affected population: {summary['affected_population'].sum():,.0f}")
    logger.info(f"Top district: {summary.iloc[0]['district']} ({summary.iloc[0]['desert_count']} deserts)")
    logger.info("\nService deserts domain analysis complete")

if __name__ == "__main__":
    main()
