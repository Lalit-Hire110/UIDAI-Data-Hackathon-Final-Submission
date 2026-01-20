"""
UIDAI Insight Command Center - Configuration
=============================================
Centralized configuration for paths, colors, and constants.
"""

from pathlib import Path

# =============================================================================
# DIRECTORY PATHS
# =============================================================================

# App root directory
APP_DIR = Path(__file__).parent.resolve()

# Static assets
STATIC_DIR = APP_DIR / "static"
ASSETS_DIR = APP_DIR / "assets"

# Data directories (local cached data)
DATA_DIR = APP_DIR / "data"
SCENARIO_DIR = DATA_DIR / "scenario_matrices"

# Parent directory artifacts (READ-ONLY)
PARENT_DIR = APP_DIR.parent
PARENT_DATA_DIR = PARENT_DIR / "data"

# AG_Analysis artifact paths (READ-ONLY - Single Source of Truth)
OUTPUTS_DIR = PARENT_DATA_DIR / "outputs"
STREAMLIT_DATA_DIR = OUTPUTS_DIR / "streamlit"
DOMAINS_DIR = OUTPUTS_DIR / "domains"
FIGURES_DIR = OUTPUTS_DIR / "figures"
DECISION_MATRIX_DIR = OUTPUTS_DIR / "final_decision_matrix"
VALIDATION_DIR = OUTPUTS_DIR / "validation"
ANTIGRAVITY_DIR = OUTPUTS_DIR / "antigravity"

# Primary dataset
PRIMARY_DATASET = PARENT_DATA_DIR / "UIDAI_with_population.csv"

# =============================================================================
# ARTIFACT FILE PATHS (READ-ONLY)
# =============================================================================

# Streamlit-ready aggregates
PINCODE_AGGREGATES = STREAMLIT_DATA_DIR / "pincode_aggregates.csv"
DISTRICT_AGGREGATES = STREAMLIT_DATA_DIR / "district_aggregates.csv"
TOP50_SERVICE_DESERTS = STREAMLIT_DATA_DIR / "top50_service_deserts.csv"

# Decision matrix
PRIORITY_MATRIX = DECISION_MATRIX_DIR / "final_priority_pincode_matrix.csv"
PRIORITY_BUCKETS = DECISION_MATRIX_DIR / "priority_bucket_summary.csv"

# Domain data
POLICY_RECOMMENDATIONS = DOMAINS_DIR / "policy_recommendations.csv"

# Domain subdirectories
SERVICE_DESERTS_DIR = DOMAINS_DIR / "service_deserts"
CAPACITY_MISMATCH_DIR = DOMAINS_DIR / "capacity_mismatch"
DEMAND_BEHAVIOR_DIR = DOMAINS_DIR / "demand_behavior"
TEMPORAL_DIR = DOMAINS_DIR / "temporal"
SERVICE_QUALITY_DIR = DOMAINS_DIR / "service_quality"

# Figure paths
UNIVARIATE_FIGS = FIGURES_DIR / "univariate"
BIVARIATE_FIGS = FIGURES_DIR / "bivariate"
MULTIVARIATE_FIGS = FIGURES_DIR / "multivariate"

# Stats JSON
POP_ACTIVITY_STATS = ANTIGRAVITY_DIR / "pop_activity_stats.json"
RURAL_URBAN_STATS = ANTIGRAVITY_DIR / "rural_urban_comparison_stats.json"

# =============================================================================
# UIDAI COLOR PALETTE
# =============================================================================

# Primary colors
AADHAAR_BLUE = "#1A73E8"
SAFFRON = "#FF9933"

# Dark mode backgrounds
DARK_BG = "#0D1117"
CARD_BG = "rgba(22, 27, 34, 0.8)"
GLASS_BORDER = "rgba(255, 255, 255, 0.1)"

# Text colors
TEXT_PRIMARY = "#E6EDF3"
TEXT_SECONDARY = "#8B949E"

# Status colors
COLOR_CRITICAL = "#F85149"
COLOR_HIGH = "#FF9933"
COLOR_MEDIUM = "#1A73E8"
COLOR_SUCCESS = "#3FB950"
COLOR_WARNING = "#D29922"

# =============================================================================
# PRIORITY BUCKET CONFIGURATION
# =============================================================================

PRIORITY_BUCKETS_CONFIG = {
    "critical": {
        "label": "Critical",
        "color": COLOR_CRITICAL,
        "threshold": 100,
        "description": "Immediate intervention required"
    },
    "high": {
        "label": "High",
        "color": COLOR_HIGH,
        "threshold": 400,
        "description": "Priority attention within 6 months"
    },
    "medium": {
        "label": "Medium",
        "color": COLOR_MEDIUM,
        "threshold": 1500,
        "description": "Scheduled intervention 6-18 months"
    },
    "monitor": {
        "label": "Monitor",
        "color": COLOR_SUCCESS,
        "threshold": None,
        "description": "Regular monitoring"
    }
}

# =============================================================================
# TIMELINE CONFIGURATION
# =============================================================================

TIMELINE_CONFIG = {
    "immediate": {
        "label": "0-6 Months",
        "color": COLOR_CRITICAL,
        "description": "Critical interventions and mobile unit deployment"
    },
    "medium_term": {
        "label": "6-18 Months",
        "color": COLOR_HIGH,
        "description": "Permanent center establishment and capacity building"
    },
    "long_term": {
        "label": "18+ Months",
        "color": COLOR_SUCCESS,
        "description": "Infrastructure expansion and sustainability"
    }
}

# =============================================================================
# SEARCH CONFIGURATION
# =============================================================================

SEARCH_CONFIG = {
    "min_query_length": 3,
    "max_results": 50,
    "debounce_ms": 300
}

# =============================================================================
# WHAT-IF SIMULATOR BOUNDS
# =============================================================================

SIMULATOR_CONFIG = {
    "rural_enrollment_increase": {
        "min": 0,
        "max": 50,
        "step": 5,
        "unit": "%",
        "label": "Rural Enrollment Increase"
    },
    "urban_capacity_boost": {
        "min": 0,
        "max": 30,
        "step": 5,
        "unit": "%",
        "label": "Urban Capacity Boost"
    },
    "mobile_units_deployed": {
        "min": 0,
        "max": 500,
        "step": 25,
        "unit": "units",
        "label": "Mobile Units Deployed"
    }
}

# =============================================================================
# DISPLAY CONFIGURATION
# =============================================================================

# Number formatting
POPULATION_DECIMALS = 0
PERCENTAGE_DECIMALS = 1
SCORE_DECIMALS = 2

# Table display
MAX_TABLE_ROWS = 100
DEFAULT_PAGE_SIZE = 25

# Chart dimensions
CHART_HEIGHT = 400
CHART_WIDTH = None  # Auto

# =============================================================================
# VALIDATION
# =============================================================================

def validate_paths():
    """Validate that critical read-only paths exist"""
    critical_paths = [
        PINCODE_AGGREGATES,
        DISTRICT_AGGREGATES,
        PRIORITY_BUCKETS,
        POLICY_RECOMMENDATIONS
    ]
    
    missing = []
    for path in critical_paths:
        if not path.exists():
            missing.append(str(path))
    
    return missing

def get_data_status():
    """Get status of all data sources"""
    status = {
        "pincode_aggregates": PINCODE_AGGREGATES.exists(),
        "district_aggregates": DISTRICT_AGGREGATES.exists(),
        "priority_matrix": PRIORITY_MATRIX.exists(),
        "priority_buckets": PRIORITY_BUCKETS.exists(),
        "policy_recommendations": POLICY_RECOMMENDATIONS.exists(),
        "primary_dataset": PRIMARY_DATASET.exists()
    }
    return status
