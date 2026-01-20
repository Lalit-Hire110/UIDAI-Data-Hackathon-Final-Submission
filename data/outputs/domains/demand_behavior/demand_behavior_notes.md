# Demand Behavior Domain - Figure Notes

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
