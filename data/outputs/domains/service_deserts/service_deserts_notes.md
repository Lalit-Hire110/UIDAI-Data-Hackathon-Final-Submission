# Service Deserts Domain - Figure Notes

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
