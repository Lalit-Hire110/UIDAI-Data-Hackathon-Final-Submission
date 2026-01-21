# Scripts - Documentation

This directory contains modular, well-documented Python scripts for comprehensive data validation and robustness testing of the UIDAI service desert analysis.

---

## Script Inventory

### 01_population_audit.py
**Purpose:** Population imputation transparency audit  
**Output:** `imputed_population_report.csv`  
**Key Feature:** Backward-traces imputation sources (district/state/global median)  
**Runtime:** ~10 seconds  
**Note:** Descriptive only - no recommendations for changes

### 02_service_desert_sensitivity.py
**Purpose:** Service desert threshold sensitivity analysis  
**Output:** `service_desert_sensitivity.csv`  
**Thresholds:** 40%, 50% (PRIMARY), 60%  
**Runtime:** ~5 seconds  
**Note:** Frames 50% as operational definition, others as robustness checks

### 03_rural_urban_stats.py
**Purpose:** Rural vs urban statistical validation  
**Outputs:** `rural_urban_comparison_stats.json`, `rural_urban_medians.csv`, `rural_urban_boxplot.png`  
**Methods:** Cohen's d, Mann-Whitney U, bootstrap 95% CI (10,000 resamples)  
**Runtime:** ~15 seconds (bootstrap-intensive)  
**Note:** Exports median CSV for citation in reports

### 04_pop_activity_correlation.py
**Purpose:** Population-activity correlation analysis  
**Outputs:** `pop_activity_stats.json`, `pop_activity_scatter.png`, `regression_diagnostics.png`  
**Methods:** Pearson & Spearman correlations, LOWESS smoothing, Huber robust regression, Breusch-Pagan test  
**Runtime:** ~15 seconds  
**Note:** Emphasizes heteroskedasticity; explicitly warns against normative interpretation

### 05_outlier_detection.py
**Purpose:** Outlier and anomaly detection  
**Output:** `anomaly_list.csv` (top 100)  
**Methods:** IQR (1.5×), MAD (3×), policy relevance scoring  
**Runtime:** ~8 seconds  
**Note:** Caps output to top 100 most policy-relevant cases with reason codes

### 06_district_verification.py
**Purpose:** District-level service desert verification  
**Outputs:** `district_deserts_top15.csv`, `district_desert_counts.png`  
**Key Feature:** Reproducible district count summary with desert ratios  
**Runtime:** ~8 seconds  
**Note:** Confirms top 15 districts match notebook findings

### 07_visualizations.py
**Purpose:** Generate summary visualizations  
**Outputs:** `viz_imputation_distribution.png`, `viz_sensitivity_comparison.png`, `viz_activity_distribution.png`, `viz_top_anomalies.png`  
**Runtime:** ~10 seconds  
**Note:** Individual PNGs only - no combined grids (PDF readability)

### 08_generate_report.py
**Purpose:** Consolidated markdown report generation  
**Output:** `antigravity_report.md`  
**Key Feature:** Parses all outputs, embeds visualizations, provides executive summary  
**Runtime:** <1 second  
**Note:** Validation-oriented tone - confirms existing findings, no new narratives

---

## Orchestration

### run_all.py
**Purpose:** Execute all 8 scripts in sequence  
**Error Handling:** Exits on first failure with detailed traceback  
**Logging:** All output logged to `outputs/antigravity/antigravity.log`  
**Timeout:** 20 minutes per script  
**Usage:**
```powershell
python run_all.py
```

---

## Dependencies

See `requirements.txt`:
- pandas==2.2.0
- numpy==1.26.3
- scipy==1.12.0
- statsmodels==0.14.1
- matplotlib==3.8.2

Install all:
```powershell
pip install -r requirements.txt
```

---

## Design Principles

1. **Modularity**: Each script is self-contained and can run independently
2. **Reproducibility**: Fixed random seed (42), explicit package versions
3. **Logging**: All scripts log to shared `antigravity.log` with timestamps
4. **Error Handling**: Graceful failures with informative error messages
5. **Validation-Oriented**: Confirms existing notebook findings, no new definitions
6. **Non-Normative**: Explicit warnings against equity/adequacy interpretations
7. **Policy-Relevant**: Outputs prioritized for actionable insights

---

## Output Guarantees

Each script guarantees:
- ✓ Fixed column order in CSV outputs
- ✓ Deterministic results (seeded randomness)
- ✓ JSON with standard Python types (no numpy types)
- ✓ PNG plots at 200 DPI for print quality
- ✓ Markdown report with embedded relative image paths
- ✓ Comprehensive logging of all operations

---

## Maintenance Notes

- All file paths use `Path` from `pathlib` for cross-platform compatibility
- Data loading uses `low_memory=False` for consistent type inference
- Population handling includes defensive checks for zero/null values
- All aggregations explicitly specify `as_index=False` for clarity
- Regression diagnostics use 2×2 subplots for comprehensive checks

---
