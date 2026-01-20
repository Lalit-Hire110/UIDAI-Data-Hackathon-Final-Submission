"""
Antigravity Analysis Pipeline Orchestrator

Executes all analysis scripts in sequence (01-08).
Exits on first error with traceback logged.

Usage: python run_all.py
"""

import subprocess
import sys
from pathlib import Path
import logging
from datetime import datetime

# Setup
BASE_DIR = Path(__file__).parent
SCRIPTS_DIR = BASE_DIR
OUT_DIR = BASE_DIR / "outputs" / "antigravity"
LOG_FILE = OUT_DIR / "antigravity.log"

# Ensure output directory exists
OUT_DIR.mkdir(parents=True, exist_ok=True)

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

# Scripts to run in order
SCRIPTS = [
    "01_population_audit.py",
    "02_service_desert_sensitivity.py",
    "03_rural_urban_stats.py",
    "04_pop_activity_correlation.py",
    "05_outlier_detection.py",
    "06_district_verification.py",
    "07_visualizations.py",
    "08_generate_report.py"
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
            timeout=1200  # 20 minute timeout per script
        )
        
        # Log stdout
        if result.stdout:
            logger.info(result.stdout)
        
        # Check for errors
        if result.returncode != 0:
            logger.error(f"Script {script_name} failed with return code {result.returncode}")
            if result.stderr:
                logger.error(f"STDERR:\n{result.stderr}")
            return False
        
        logger.info(f"✓ {script_name} completed successfully")
        return True
        
    except subprocess.TimeoutExpired:
        logger.error(f"Script {script_name} timed out after 20 minutes")
        return False
    except Exception as e:
        logger.error(f"Error running {script_name}: {e}")
        return False

def main():
    start_time = datetime.now()
    
    logger.info("*" * 80)
    logger.info("ANTIGRAVITY DATA ANALYSIS PIPELINE")
    logger.info("*" * 80)
    logger.info(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Base directory: {BASE_DIR}")
    logger.info(f"Output directory: {OUT_DIR}")
    logger.info(f"Log file: {LOG_FILE}")
    logger.info(f"Number of scripts: {len(SCRIPTS)}")
    logger.info("")
    
    # Run all scripts
    for i, script in enumerate(SCRIPTS, 1):
        logger.info(f"\nStep {i}/{len(SCRIPTS)}: {script}")
        
        success = run_script(script)
        
        if not success:
            logger.error("")
            logger.error("*" * 80)
            logger.error("PIPELINE FAILED")
            logger.error("*" * 80)
            logger.error(f"Failed at script: {script}")
            logger.error(f"Check {LOG_FILE} for details")
            sys.exit(1)
    
    # Success
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info("")
    logger.info("*" * 80)
    logger.info("PIPELINE COMPLETED SUCCESSFULLY")
    logger.info("*" * 80)
    logger.info(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Total duration: {duration}")
    logger.info(f"\nAll outputs saved to: {OUT_DIR}")
    logger.info("\nGenerated files:")
    logger.info("  - imputed_population_report.csv")
    logger.info("  - service_desert_sensitivity.csv")
    logger.info("  - rural_urban_comparison_stats.json")
    logger.info("  - rural_urban_medians.csv")
    logger.info("  - rural_urban_boxplot.png")
    logger.info("  - pop_activity_stats.json")
    logger.info("  - pop_activity_scatter.png")
    logger.info("  - regression_diagnostics.png")
    logger.info("  - anomaly_list.csv")
    logger.info("  - district_deserts_top15.csv")
    logger.info("  - district_desert_counts.png")
    logger.info("  - viz_*.png (4 additional visualizations)")
    logger.info("  - antigravity_report.md (consolidated report)")
    logger.info("  - antigravity.log (full execution log)")
    logger.info("")
    logger.info("Review antigravity_report.md for comprehensive findings.")

if __name__ == "__main__":
    main()
