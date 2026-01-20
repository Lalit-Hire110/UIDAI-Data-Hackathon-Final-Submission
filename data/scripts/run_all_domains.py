"""
Domain Analysis Orchestrator

Executes all domain scripts in sequence (09-13 + policy simulator).
Aggregates validation results and generates completion summary.
"""

import subprocess
import sys
from pathlib import Path
import logging
import pandas as pd
from datetime import datetime
import io

# Setup
BASE_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = BASE_DIR / "antigravity_scripts"
OUT_DIR = BASE_DIR / "outputs" / "antigravity"
LOG_FILE = OUT_DIR / "antigravity.log"

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
logger = logging.getLogger(__name__)

# Scripts to run
DOMAIN_SCRIPTS = [
    "09_service_deserts.py",
    "10_demand_behavior.py",
    "11_service_quality.py",
    "12_capacity_mismatch.py",
    "13_temporal.py",
    "policy_simulator.py"
]

def run_script(script_name):
    """Run a single script and check for errors."""
    script_path = SCRIPTS_DIR / script_name
    
    if not script_path.exists():
        logger.error(f"Script not found: {script_path}")
        return False
    
    logger.info("=" * 80)
    logger.info(f"RUNNING: {script_name}")
    logger.info("=" * 80)
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout per script
        )
        
        if result.stdout:
            logger.info(result.stdout)
        
        if result.returncode != 0:
            logger.error(f"Script {script_name} failed with return code {result.returncode}")
            if result.stderr:
                logger.error(f"STDERR:\n{result.stderr}")
            return False
        
        logger.info(f"✓ {script_name} completed successfully")
        return True
        
    except subprocess.TimeoutExpired:
        logger.error(f"Script {script_name} timed out after 10 minutes")
        return False
    except Exception as e:
        logger.error(f"Error running {script_name}: {e}")
        return False

def aggregate_validation():
    """Aggregate validation results from all domains."""
    logger.info("\n" + "=" * 80)
    logger.info("AGGREGATING VALIDATION RESULTS")
    logger.info("=" * 80)
    
    domains_dir = BASE_DIR / "outputs" / "domains"
    validation_files = list(domains_dir.glob("*/validation_*.csv"))
    
    all_validations = []
    for vfile in validation_files:
        domain = vfile.parent.name
        vdata = pd.read_csv(vfile)
        vdata['domain'] = domain
        all_validations.append(vdata)
    
    if all_validations:
        combined = pd.concat(all_validations, ignore_index=True)
        
        logger.info(f"\nValidation Summary ({len(validation_files)} domains):")
        logger.info(combined.groupby('result')['check_name'].count().to_string())
        
        failures = combined[combined['result'] == 'FAIL']
        if len(failures) > 0:
            logger.warning(f"\n{len(failures)} validation failures detected:")
            for _, row in failures.iterrows():
                logger.warning(f"  [{row['domain']}] {row['check_name']}: {row['details']}")
        else:
            logger.info("\n✓ All validation checks passed")
        
        return combined
    else:
        logger.warning("No validation files found")
        return None

def generate_summary():
    """Generate domain completion summary."""
    logger.info("\n" + "=" * 80)
    logger.info("DOMAIN ANALYSIS COMPLETION SUMMARY")
    logger.info("=" * 80)
    
    domains_dir = BASE_DIR / "outputs" / "domains"
    
    summary = []
    for domain_dir in sorted(domains_dir.glob("*")):
        if domain_dir.is_dir():
            domain = domain_dir.name
            metrics_file = domain_dir / f"{domain}_metrics.csv"
            summary_file = domain_dir / f"{domain}_summary.csv"
            
            if metrics_file.exists():
                df = pd.read_csv(metrics_file)
                row_count = len(df)
                
                # Top 5 outputs (domain-specific)
                top5_desc = "N/A"
                if domain == "service_deserts" and 'is_service_desert' in df.columns:
                    desert_count = df['is_service_desert'].sum()
                    top5_desc = f"{desert_count} service deserts identified"
                elif domain == "demand_behavior" and 'dominant_service_type' in df.columns:
                    top_type = df['dominant_service_type'].value_counts().index[0]
                    top5_desc = f"Dominant: {top_type}"
                elif domain == "service_quality" and 'consistency_tier' in df.columns:
                    high = (df['consistency_tier'] == 'high_consistency').sum()
                    top5_desc = f"{high} high consistency pincodes"
                elif domain == "capacity_mismatch" and 'mismatch_type' in df.columns:
                    low = (df['mismatch_type'] == 'low_activity').sum()
                    top5_desc = f"{low} low activity pincodes"
                elif domain == "temporal" and 'sufficient_coverage' in df.columns:
                    sufficient = df['sufficient_coverage'].sum()
                    top5_desc = f"{sufficient} pincodes with ≥6 months data"
                
                summary.append({
                    'domain': domain,
                    'pincodes_analyzed': row_count,
                    'key_finding': top5_desc
                })
    
    if summary:
        summary_df = pd.DataFrame(summary)
        logger.info("\n" + summary_df.to_string(index=False))
        
        # Check for population failures
        logger.info("\n" + "=" * 80)
        logger.info("POPULATION COVERAGE CHECK")
        logger.info("=" * 80)
        
        metrics_file = domains_dir / "service_deserts" / "service_deserts_metrics.csv"
        if metrics_file.exists():
            df = pd.read_csv(metrics_file)
            pop_issues = (df['population'] <= 0).sum()
            logger.info(f"Pincodes with missing/zero population: {pop_issues}")
            if pop_issues == 0:
                logger.info("✓ No population failures after imputation")
            else:
                logger.warning(f"⚠ {pop_issues} pincodes with population issues")
        
        return summary_df
    else:
        logger.warning("No domain metrics found")
        return None

def main():
    start_time = datetime.now()
    
    logger.info("*" * 80)
    logger.info("DOMAIN ANALYSIS PIPELINE")
    logger.info("*" * 80)
    logger.info(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Base directory: {BASE_DIR}")
    logger.info(f"Number of scripts: {len(DOMAIN_SCRIPTS)}")
    logger.info("")
    
    # Run all scripts
    for i, script in enumerate(DOMAIN_SCRIPTS, 1):
        logger.info(f"\nStep {i}/{len(DOMAIN_SCRIPTS)}: {script}")
        
        success = run_script(script)
        
        if not success:
            logger.error("")
            logger.error("*" * 80)
            logger.error("PIPELINE FAILED")
            logger.error("*" * 80)
            logger.error(f"Failed at script: {script}")
            logger.error(f"Check {LOG_FILE} for details")
            sys.exit(1)
    
    # Aggregate validation
    validate = aggregate_validation()
    
    # Generate summary
    summary = generate_summary()
    
    # Success
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info("")
    logger.info("*" * 80)
    logger.info("PIPELINE COMPLETED SUCCESSFULLY")
    logger.info("*" * 80)
    logger.info(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Total duration: {duration}")
    logger.info("\nAll domain outputs saved to: outputs/domains/")
    logger.info("All figures saved to: outputs/figures/domains/")
    logger.info("\nReview individual domain notes for interpretation guidance.")

if __name__ == "__main__":
    main()
