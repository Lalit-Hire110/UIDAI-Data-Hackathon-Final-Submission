"""
Service Quality Domain Analysis

Purpose: Analyze activity consistency patterns using NEUTRAL terminology.
         - Terms: "activity consistency" (not failure)
         - "potential service stress" (not poor quality)
         - "inconsistent patterns" (not failures)
         - All outputs framed as SIGNALS, not definitive failures

Output: service_quality_metrics.csv, service_quality_summary.csv,
        validation_service_quality.csv, service_quality_notes.md, 3 PNGs
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
OUT_DIR = BASE_DIR / "outputs" / "domains" / "service_quality"
FIG_DIR = BASE_DIR / "outputs" / "figures" / "domains" / "service_quality"
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

def main():
    logger.info("=" * 60)
    logger.info("SERVICE QUALITY DOMAIN ANALYSIS")
    logger.info("=" * 60)
    logger.info("Using neutral terminology:")
    logger.info("  - Activity consistency (not failure)")
    logger.info("  - Potential service stress (not poor quality)")
    logger.info("  - Signals (not definitive failures)")
    
    # Find latest snapshot
    snapshot_files = list(SNAPSHOT_DIR.glob("cleaned_uidai_snapshot_*.csv"))
    if not snapshot_files:
        raise FileNotFoundError("No cleaned snapshot found")
    
    snapshot_file = max(snapshot_files, key=lambda x: x.stat().st_mtime)
    logger.info(f"Loading snapshot: {snapshot_file.name}")
    
    # Load data
    df = pd.read_csv(snapshot_file, low_memory=False)
    logger.info(f"Loaded {len(df):,} rows")
    
    # Aggregate to pincode level - defensive aggregation
    logger.info("Aggregating to pincode level")
    pincode_agg = df.groupby('pincode', as_index=False).agg(
        district=('district', 'first'),
        state=('state', 'first'),
        population=('population', 'sum'),
        urban_flag=('urban_flag', 'first'),
        total_activity=('total_activity', 'sum')
    )
    
    # Derive activity_per_100k after aggregation
    pincode_agg['activity_per_100k'] = pincode_agg['total_activity'] / (pincode_agg['population'] / 100000)
    pincode_agg['activity_per_100k'] = pincode_agg['activity_per_100k'].replace([np.inf, -np.inf], np.nan).fillna(0)
    
    # Compute activity consistency score
    # If temporal data available, use coefficient of variation
    # Otherwise, use relative position to district median as proxy
    
    logger.info("Computing activity consistency metrics")
    
    # District baselines for comparison
    district_stats = pincode_agg.groupby('district')['activity_per_100k'].agg(['median', 'std']).reset_index()
    pincode_agg = pincode_agg.merge(district_stats, on='district', suffixes=('', '_district'))
    
    # Activity consistency score (inverse of relative deviation)
    # Higher score = more consistent with district pattern
    pincode_agg['relative_deviation'] = np.abs(
        pincode_agg['activity_per_100k'] - pincode_agg['median']
    ) / (pincode_agg['std'].replace(0, 1))
    
    # Normalize to [0,1] where 1 = highest consistency
    max_dev = pincode_agg['relative_deviation'].quantile(0.95)  # Cap outliers
    pincode_agg['activity_consistency_score'] = 1 - (
        pincode_agg['relative_deviation'].clip(upper=max_dev) / max_dev
    )
    
    # Service stress signals (neutral framing)
    # Below median + high deviation = potential stress signal
    pincode_agg['below_district_median'] = (
        pincode_agg['activity_per_100k'] < pincode_agg['median']
    )
    
    pincode_agg['potential_stress_signal'] = (
        pincode_agg['below_district_median'] &
        (pincode_agg['activity_consistency_score'] < 0.5)
    )
    
    # Quality tier classification (neutral language)
    # Based on consistency scores, not normative judgments
    pincode_agg['consistency_tier'] = pd.cut(
        pincode_agg['activity_consistency_score'],
        bins=[0, 0.33, 0.67, 1.0],
        labels=['inconsistent_pattern', 'moderate_consistency', 'high_consistency']
    )
    
    logger.info(f"Consistency tier distribution:\n{pincode_agg['consistency_tier'].value_counts()}")
    
    # Save metrics
    metrics_cols = [
        'pincode', 'district', 'state', 'population', 'urban_flag',
        'total_activity', 'activity_per_100k', 'activity_consistency_score',
        'potential_stress_signal', 'consistency_tier', 'relative_deviation'
    ]
    pincode_agg[metrics_cols].to_csv(OUT_DIR / "service_quality_metrics.csv", index=False)
    logger.info(f"Saved metrics: {OUT_DIR / 'service_quality_metrics.csv'}")
    
    # District summary
    logger.info("Computing district summary")
    summary = pincode_agg.groupby('district', as_index=False).agg(
        state=('state', 'first'),
        total_pincodes=('pincode', 'count'),
        avg_consistency=('activity_consistency_score', 'mean'),
        pct_high_consistency=('consistency_tier', lambda x: (x == 'high_consistency').sum() / len(x) * 100),
        consistency_variance=('activity_consistency_score', 'std'),
        stress_signal_count=('potential_stress_signal', 'sum')
    )
    
    summary['stress_signal_ratio'] = summary['stress_signal_count'] / summary['total_pincodes']
    
    summary.to_csv(OUT_DIR / "service_quality_summary.csv", index=False)
    logger.info(f"Saved summary: {OUT_DIR / 'service_quality_summary.csv'}")
    
    # Validation checks
    logger.info("Running validation checks")
    validation = []
    
    # Check 1: Total pincodes
    validation.append({
        'check_name': 'total_pincodes',
        'result': 'PASS',
        'details': f"{len(pincode_agg)} pincodes processed"
    })
    
    # Check 2: Consistency score range
    score_range = (
        (pincode_agg['activity_consistency_score'] >= 0).all() and
        (pincode_agg['activity_consistency_score'] <= 1).all()
    )
    validation.append({
        'check_name': 'consistency_score_range',
        'result': 'PASS' if score_range else 'FAIL',
        'details': 'Consistency scores in [0,1]' if score_range else 'Consistency scores outside [0,1]'
    })
    
    # Check 3: No infinite values
    inf_check = np.isinf(pincode_agg[metrics_cols[5:]].select_dtypes(include=[np.number])).any().any()
    validation.append({
        'check_name': 'no_infinite_values',
        'result': 'FAIL' if inf_check else 'PASS',
        'details': 'Infinite values detected' if inf_check else 'All metrics finite'
    })
    
    # Check 4: Tier assignment complete
    tier_missing = pincode_agg['consistency_tier'].isna().sum()
    validation.append({
        'check_name': 'tier_assignment_complete',
        'result': 'FAIL' if tier_missing > 0 else 'PASS',
        'details': f"{tier_missing} pincodes without tier assignment" if tier_missing > 0 else "All pincodes assigned tiers"
    })
    
    pd.DataFrame(validation).to_csv(OUT_DIR / "validation_service_quality.csv", index=False)
    logger.info(f"Saved validation: {OUT_DIR / 'validation_service_quality.csv'}")
    
    # Visualizations
    logger.info("Generating visualizations")
    
    # Fig 1: Consistency distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(pincode_agg['activity_consistency_score'], bins=30, edgecolor='black', alpha=0.7, color='steelblue')
    ax.set_xlabel('Activity Consistency Score')
    ax.set_ylabel('Number of Pincodes')
    ax.set_title('Distribution of Activity Consistency Scores\n(Higher = more consistent with district pattern)')
    ax.grid(alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(FIG_DIR / "consistency_distribution.png", dpi=200, bbox_inches='tight')
    plt.close()
    
    # Fig 2: Consistency by tier
    fig, ax = plt.subplots(figsize=(10, 6))
    tier_counts = pincode_agg['consistency_tier'].value_counts().sort_index()
    colors = ['#ff9999', '#ffcc99', '#99ccff']
    ax.bar(range(len(tier_counts)), tier_counts.values, color=colors, edgecolor='black')
    ax.set_xticks(range(len(tier_counts)))
    ax.set_xticklabels(tier_counts.index, rotation=15, ha='right')
    ax.set_ylabel('Number of Pincodes')
    ax.set_title('Pincodes by Consistency Tier\n(Descriptive classification, not normative judgment)')
    ax.grid(alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(FIG_DIR / "volatility_scores.png", dpi=200, bbox_inches='tight')
    plt.close()
    
    # Fig 3: Consistency by district (top 15)
    fig, ax = plt.subplots(figsize=(10, 8))
    top15 = summary.nlargest(15, 'avg_consistency').sort_values('avg_consistency', ascending=True)
    ax.barh(range(len(top15)), top15['avg_consistency'], color='steelblue')
    ax.set_yticks(range(len(top15)))
    ax.set_yticklabels(top15['district'])
    ax.set_xlabel('Average Consistency Score')
    ax.set_title('Top 15 Districts by Average Activity Consistency')
    ax.grid(alpha=0.3, axis='x')
    plt.tight_layout()
    plt.savefig(FIG_DIR / "quality_by_district.png", dpi=200, bbox_inches='tight')
    plt.close()
    
    logger.info(f"Saved 3 visualizations to {FIG_DIR}")
    
    # Notes
    notes = """# Service Quality Domain - Figure Notes

## Overview
This domain analyzes activity consistency patterns using neutral, signal-based terminology.

## Figures

### 1. Consistency Distribution (`consistency_distribution.png`)
**Description:** Histogram of activity consistency scores across all pincodes.

**Interpretation:** 
- Higher scores indicate patterns more consistent with district norms
- Lower scores suggest inconsistent patterns (potential service stress signals)
- This is a DESCRIPTIVE metric, not a normative quality judgment

### 2. Pincodes by Consistency Tier (`volatility_scores.png`)
**Description:** Bar chart showing the number of pincodes in each consistency tier.

**Interpretation:**
- **high_consistency**: Activity patterns align well with district norms
- **moderate_consistency**: Some deviation from typical patterns
- **inconsistent_pattern**: Signals potential service stress or unusual conditions
- Tiers are descriptive classifications, not failure categories

### 3. Top Districts by Consistency (`quality_by_district.png`)
**Description:** Horizontal bar chart of the 15 districts with highest average consistency scores.

**Interpretation:** Districts with high average consistency show stable, predictable activity patterns. This does NOT imply superiority, only consistency with local norms.

## Key Metrics

- **activity_consistency_score**: [0,1] measure of pattern consistency (1 = highly consistent)
- **potential_stress_signal**: Boolean flag for pincodes showing below-median activity with low consistency
- **consistency_tier**: Descriptive classification (inconsistent/moderate/high)
- **relative_deviation**: Standardized deviation from district median

## Terminology (Neutral Framing)

- **Consistent patterns** (not "good quality")
- **Inconsistent patterns** (not "failures" or "poor quality")
- **Potential stress signals** (not "problem areas")
- **Activity consistency** (not "service quality")

## Methodology

Consistency scores measure how well a pincode's activity aligns with its district's typical pattern. This is a SIGNAL for further investigation, not a definitive assessment of service adequacy or quality.

---
*Analysis Date: 2026-01-18*
"""
    
    with open(OUT_DIR / 'service_quality_notes.md', 'w', encoding='utf-8') as f:
        f.write(notes)
    
    logger.info(f"Saved notes: {OUT_DIR / 'service_quality_notes.md'}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total pincodes analyzed: {len(pincode_agg):,}")
    logger.info(f"High consistency: {(pincode_agg['consistency_tier'] == 'high_consistency').sum():,}")
    logger.info(f"Potential stress signals: {pincode_agg['potential_stress_signal'].sum():,}")
    logger.info(f"Average consistency score: {pincode_agg['activity_consistency_score'].mean():.3f}")
    logger.info("\nService quality domain analysis complete")

if __name__ == "__main__":
    main()
