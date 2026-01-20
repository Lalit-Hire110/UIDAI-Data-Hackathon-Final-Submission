"""
Policy Simulator (PROTOTYPE)

Purpose: ILLUSTRATIVE scenario modeling for resource allocation.
         - Labeled as prototype/illustrative
         - NO claims of guaranteed real-world impact
         - Simple prioritization logic for demonstration

Output: policy_recommendations.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import sys
import io

np.random.seed(42)
BASE_DIR = Path(r"C:\Users\Lalit Hire\UIDAI Data Hackathon 2026\data")
DOMAINS_DIR = BASE_DIR / "outputs" / "domains"
OUT_DIR = DOMAINS_DIR
LOG_FILE = BASE_DIR / "outputs" / "antigravity" / "antigravity.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True))
    ]
)
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)

def main():
    logger.info("=" * 60)
    logger.info("POLICY SIMULATOR (PROTOTYPE)")
    logger.info("=" * 60)
    logger.info("ILLUSTRATIVE scenarios only - NO guaranteed real-world impact")
    logger.info("Simple prioritization logic for demonstration purposes")
    
    # Load domain metrics
    logger.info("Loading domain metrics")
    
    try:
        deserts = pd.read_csv(DOMAINS_DIR / "service_deserts" / "service_deserts_metrics.csv")
        quality = pd.read_csv(DOMAINS_DIR / "service_quality" / "service_quality_metrics.csv")
        mismatch = pd.read_csv(DOMAINS_DIR / "capacity_mismatch" / "capacity_mismatch_metrics.csv")
        logger.info("Loaded 3 domain metric files")
    except FileNotFoundError as e:
        logger.error(f"Domain metrics not found: {e}")
        logger.error("Run domain scripts first (09-13)")
        return
    
    # Merge metrics
    logger.info("Merging domain metrics")
    combined = deserts[['pincode', 'district', 'state', 'population', 'is_service_desert', 'priority_score']].copy()
    
    combined = combined.merge(
        quality[['pincode', 'activity_consistency_score', 'potential_stress_signal']],
        on='pincode',
        how='left'
    )
    
    combined = combined.merge(
        mismatch[['pincode', 'mismatch_type', 'mismatch_magnitude']],
        on='pincode',
        how='left'
    )
    
    # Compute composite priority score (ILLUSTRATIVE formula)
    logger.info("Computing composite priority scores (ILLUSTRATIVE)")
    
    # Simple weighted combination
    combined['desert_weight'] = combined['is_service_desert'].astype(int) * 3
    combined['quality_weight'] = combined['potential_stress_signal'].fillna(False).astype(int) * 2
    combined['mismatch_weight'] = (combined['mismatch_type'] == 'low_activity').fillna(False).astype(int) * 1
    
    combined['composite_priority'] = (
        combined['desert_weight'] +
        combined['quality_weight'] +
        combined['mismatch_weight'] +
        np.log1p(combined['population']) / 10  # Population factor
    )
    
    # Rank pincodes
    combined = combined.sort_values('composite_priority', ascending=False)
    combined['priority_rank'] = range(1, len(combined) + 1)
    
    # Identify top intervention targets (top 100)
    top_targets = combined.head(100).copy()
    
    # Illustrative resource estimates (PROTOTYPE logic)
    logger.info("Generating illustrative resource recommendations (PROTOTYPE)")
    
    top_targets['recommended_mobile_units'] = np.ceil(top_targets['population'] / 50000).astype(int)
    top_targets['estimated_field_staff'] = (top_targets['recommended_mobile_units'] * 3).astype(int)
    top_targets['intervention_type'] = 'mobile_enrollment'
    
    # High population + desert = permanent center
    top_targets.loc[
        (top_targets['population'] > 100000) & (top_targets['is_service_desert']),
        'intervention_type'
    ] = 'permanent_center'
    
    # Low activity mismatch = capacity expansion
    top_targets.loc[
        top_targets['mismatch_type'] == 'low_activity',
        'intervention_type'
    ] = 'capacity_expansion'
    
    # Save recommendations
    output_cols = [
        'priority_rank', 'pincode', 'district', 'state', 'population',
        'is_service_desert', 'potential_stress_signal', 'mismatch_type',
        'composite_priority', 'intervention_type',
        'recommended_mobile_units', 'estimated_field_staff'
    ]
    
    top_targets[output_cols].to_csv(OUT_DIR / "policy_recommendations.csv", index=False)
    logger.info(f"Saved recommendations: {OUT_DIR / 'policy_recommendations.csv'}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("SUMMARY (ILLUSTRATIVE PROTOTYPE)")
    logger.info("=" * 60)
    logger.info(f"Top 100 intervention targets identified")
    logger.info(f"Total mobile units (illustrative): {top_targets['recommended_mobile_units'].sum()}")
    logger.info(f"Total field staff (illustrative): {top_targets['estimated_field_staff'].sum()}")
    logger.info("\nIntervention type distribution:")
    logger.info(top_targets['intervention_type'].value_counts().to_string())
    logger.info("\n**IMPORTANT: These are ILLUSTRATIVE scenarios for demonstration.**")
    logger.info("**NO claims of guaranteed real-world impact or operational feasibility.**")
    logger.info("**Actual deployment requires detailed operational planning and validation.**")

if __name__ == "__main__":
    main()
