# Service Quality Domain - Figure Notes

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
