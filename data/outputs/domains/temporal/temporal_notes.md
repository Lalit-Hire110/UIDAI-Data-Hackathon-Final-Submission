# Temporal Domain - Figure Notes
Analyzes time-series trends with strict data quality requirements.

## Coverage Requirement
**Minimum 6 active months** required for trend computation.
Pincodes with less are explicitly flagged as "insufficient_data" (no forced estimates).

## Figures
1. **Activity Trends**: Distribution of trend classifications (growth/stable/decline/insufficient)
2. **Coverage Map**: Districts ranked by percentage of pincodes meeting coverage requirement
3. **Volatility Distribution**: Only computed for pincodes with sufficient temporal data

## Metrics
- **months_active**: Number of unique months with data
- **sufficient_coverage**: Boolean flag (≥6 months)
- **activity_trend**: Classification (only if sufficient_coverage=True)
- **temporal_volatility**: Variability measure (NaN if insufficient data)

## Data Quality Note
Trend and volatility metrics are **only computed** when sufficient temporal coverage exists.
All other pincodes are flagged as "insufficient_data" rather than forcing unreliable estimates.

*Analysis Date: 2026-01-18*
