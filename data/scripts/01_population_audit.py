"""
Population Imputation Audit - Descriptive Analysis Only

Purpose: Identify pincodes where population was imputed using district/state/global
         median hierarchy. This is a transparency report only; no recommendations
         for changes to the locked population logic are provided.

Output: imputed_population_report.csv
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

def detect_imputation_source(df):
    """
    Backward-trace population imputation sources by reconstructing the hierarchy.
    
    Returns DataFrame with imputation_source column indicating:
    - 'original': Population was present in source data
    - 'district_median': Imputed from district median
    - 'state_median': Imputed from state median
    - 'global_median': Imputed from global median
    """
    logger.info("Starting population imputation audit")
    
    # Identify population columns
    pop_col = None
    for c in ['Total_Population', 'total_population', 'population']:
        if c in df.columns:
            pop_col = c
            break
    
    if not pop_col:
        logger.warning("No population column found, attempting to derive from male+female")
        male_col = next((c for c in ['Male_Population', 'male_population'] if c in df.columns), None)
        female_col = next((c for c in ['Female_Population', 'female_population'] if c in df.columns), None)
        if male_col and female_col:
            df['_pop_raw'] = pd.to_numeric(df[male_col], errors='coerce') + pd.to_numeric(df[female_col], errors='coerce')
        else:
            raise ValueError("Cannot find population data columns")
    else:
        df['_pop_raw'] = pd.to_numeric(df[pop_col], errors='coerce')
    
    # Mark original valid populations
    df['_has_original'] = df['_pop_raw'].notna() & (df['_pop_raw'] > 0)
    
    # Compute district medians (excluding invalid values)
    district_median = df[df['_has_original']].groupby('district')['_pop_raw'].median()
    
    # Compute state medians
    state_median = df[df['_has_original']].groupby('state')['_pop_raw'].median()
    
    # Global median
    global_median = df.loc[df['_has_original'], '_pop_raw'].median()
    
    # Assign imputation sources
    df['imputation_source'] = 'original'
    
    # District median imputation
    df.loc[~df['_has_original'], 'imputation_source'] = df.loc[~df['_has_original'], 'district'].map(
        lambda d: 'district_median' if d in district_median.index else 'unknown'
    )
    
    # State median fallback
    mask_state = (~df['_has_original']) & (~df['district'].isin(district_median.index))
    df.loc[mask_state, 'imputation_source'] = df.loc[mask_state, 'state'].map(
        lambda s: 'state_median' if s in state_median.index else 'global_median'
    )
    
    # Global median final fallback
    df.loc[(~df['_has_original']) & (df['imputation_source'] == 'unknown'), 'imputation_source'] = 'global_median'
    
    logger.info(f"Imputation source distribution:\n{df['imputation_source'].value_counts()}")
    
    return df

def main():
    logger.info("=" * 60)
    logger.info("POPULATION IMPUTATION AUDIT")
    logger.info("=" * 60)
    
    # Load data
    logger.info(f"Loading data from {INPUT_CSV}")
    df = pd.read_csv(INPUT_CSV, low_memory=False)
    logger.info(f"Loaded {len(df):,} rows, {len(df.columns)} columns")
    
    # Detect imputation sources
    df = detect_imputation_source(df)
    
    # Aggregate to pincode level for reporting
    pincode_report = df.groupby('pincode', as_index=False).agg(
        district=('district', 'first'),
        state=('state', 'first'),
        population=('_pop_raw', 'sum'),
        imputation_source=('imputation_source', lambda x: x.mode()[0] if len(x.mode()) > 0 else 'unknown'),
        records_count=('pincode', 'size')
    )
    
    # Sort by imputation source then population
    pincode_report = pincode_report.sort_values(['imputation_source', 'population'], ascending=[True, False])
    
    # Save report
    output_path = OUT_DIR / "imputed_population_report.csv"
    pincode_report.to_csv(output_path, index=False)
    logger.info(f"Saved imputation report to {output_path}")
    
    # Summary statistics
    imputed_count = (pincode_report['imputation_source'] != 'original').sum()
    imputed_pct = 100 * imputed_count / len(pincode_report)
    
    logger.info("\n" + "=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total unique pincodes: {len(pincode_report):,}")
    logger.info(f"Pincodes with imputed population: {imputed_count:,} ({imputed_pct:.2f}%)")
    logger.info(f"Pincodes with original population: {(pincode_report['imputation_source'] == 'original').sum():,}")
    logger.info("\nImputation breakdown:")
    for source, count in pincode_report['imputation_source'].value_counts().items():
        pct = 100 * count / len(pincode_report)
        logger.info(f"  {source}: {count:,} ({pct:.2f}%)")
    
    logger.info("\nPopulation imputation audit complete (descriptive only)")

if __name__ == "__main__":
    main()
