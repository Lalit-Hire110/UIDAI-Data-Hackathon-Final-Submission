"""
UIDAI Insight Command Center - Data Handler
============================================
Optimized data loading with persistent caching.
All data from AG_Analysis artifacts (single source of truth).
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
from pathlib import Path
from typing import Dict, Optional, Tuple, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# PATH CONFIGURATION (Import from config)
# =============================================================================
from config import (
    PINCODE_AGGREGATES,
    DISTRICT_AGGREGATES,
    PRIORITY_BUCKETS,
    POLICY_RECOMMENDATIONS,
    POP_ACTIVITY_STATS,
    RURAL_URBAN_STATS,
    TOP50_SERVICE_DESERTS,
    PRIORITY_MATRIX
)

# =============================================================================
# COLUMN DEFINITIONS (Selective Loading)
# =============================================================================

# Pincode aggregates - columns by view
PINCODE_CORE_COLS = [
    "pincode", "district", "state", "population", "urban_flag"
]

PINCODE_METRICS_COLS = [
    "pincode", "total_activity", "activity_per_100k", 
    "is_service_desert", "priority_score", "priority_rank"
]

PINCODE_SEARCH_COLS = [
    "pincode", "district", "state", "population", "urban_flag",
    "total_activity", "activity_per_100k", "is_service_desert", 
    "priority_score", "priority_rank"
]

# District aggregates - columns by view
DISTRICT_CORE_COLS = [
    "district", "state", "population", "total_activity", "activity_per_100k"
]

DISTRICT_FULL_COLS = [
    "district", "state", "population", "total_activity", 
    "bio_count", "demo_count", "enroll_count", "activity_per_100k"
]

# Policy recommendations - columns
POLICY_COLS = [
    "priority_rank", "pincode", "district", "state", "population",
    "is_service_desert", "mismatch_type", "composite_priority",
    "intervention_type", "recommended_mobile_units", "estimated_field_staff"
]


# =============================================================================
# MEMORY OPTIMIZATION UTILITIES
# =============================================================================

def optimize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Downcast numeric columns and convert strings to categories.
    Memory reduction: typically 40-60% for large datasets.
    """
    for col in df.columns:
        col_type = df[col].dtype
        
        # Downcast floats
        if col_type == "float64":
            df[col] = pd.to_numeric(df[col], downcast="float")
        
        # Downcast integers
        elif col_type == "int64":
            df[col] = pd.to_numeric(df[col], downcast="integer")
        
        # Convert low-cardinality strings to category
        elif col_type == "object":
            num_unique = df[col].nunique()
            num_total = len(df[col])
            # If < 50% unique values, use category
            if num_unique / num_total < 0.5:
                df[col] = df[col].astype("category")
    
    return df


def get_memory_usage(df: pd.DataFrame) -> str:
    """Return human-readable memory usage."""
    mem_bytes = df.memory_usage(deep=True).sum()
    if mem_bytes < 1024:
        return f"{mem_bytes} B"
    elif mem_bytes < 1024**2:
        return f"{mem_bytes/1024:.1f} KB"
    else:
        return f"{mem_bytes/1024**2:.1f} MB"


# =============================================================================
# CACHED DATA LOADERS
# =============================================================================

@st.cache_data(persist="disk", show_spinner=False)
def load_pincode_aggregates(columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Load pincode aggregates with selective columns and optimization.
    Cached to disk for instant subsequent loads.
    """
    if not PINCODE_AGGREGATES.exists():
        logger.warning(f"Pincode aggregates not found: {PINCODE_AGGREGATES}")
        return pd.DataFrame()
    
    usecols = columns if columns else None
    
    df = pd.read_csv(
        PINCODE_AGGREGATES,
        usecols=usecols,
        dtype={
            "pincode": str,
            "district": str,
            "state": str,
            "urban_flag": str
        }
    )
    
    # Optimize memory
    df = optimize_dtypes(df)
    
    # Log memory usage
    logger.info(f"Pincode aggregates loaded: {len(df)} rows, {get_memory_usage(df)}")
    
    return df


@st.cache_data(persist="disk", show_spinner=False)
def load_district_aggregates(columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Load district aggregates with selective columns.
    """
    if not DISTRICT_AGGREGATES.exists():
        logger.warning(f"District aggregates not found: {DISTRICT_AGGREGATES}")
        return pd.DataFrame()
    
    usecols = columns if columns else None
    
    df = pd.read_csv(
        DISTRICT_AGGREGATES,
        usecols=usecols,
        dtype={
            "district": str,
            "state": str
        }
    )
    
    df = optimize_dtypes(df)
    logger.info(f"District aggregates loaded: {len(df)} rows, {get_memory_usage(df)}")
    
    return df


@st.cache_data(persist="disk", show_spinner=False)
def load_priority_buckets() -> pd.DataFrame:
    """Load priority bucket summary."""
    if not PRIORITY_BUCKETS.exists():
        logger.warning(f"Priority buckets not found: {PRIORITY_BUCKETS}")
        return pd.DataFrame()
    
    df = pd.read_csv(PRIORITY_BUCKETS)
    return df


@st.cache_data(persist="disk", show_spinner=False)
def load_policy_recommendations(top_n: int = 100) -> pd.DataFrame:
    """Load top N policy recommendations."""
    if not POLICY_RECOMMENDATIONS.exists():
        logger.warning(f"Policy recommendations not found: {POLICY_RECOMMENDATIONS}")
        return pd.DataFrame()
    
    df = pd.read_csv(
        POLICY_RECOMMENDATIONS,
        usecols=POLICY_COLS,
        nrows=top_n,
        dtype={
            "pincode": str,
            "district": str,
            "state": str
        }
    )
    
    df = optimize_dtypes(df)
    return df


@st.cache_data(persist="disk", show_spinner=False)
def load_top_service_deserts() -> pd.DataFrame:
    """Load top 50 service deserts."""
    if not TOP50_SERVICE_DESERTS.exists():
        logger.warning(f"Service deserts not found: {TOP50_SERVICE_DESERTS}")
        return pd.DataFrame()
    
    df = pd.read_csv(TOP50_SERVICE_DESERTS, dtype={"pincode": str})
    return df


# =============================================================================
# JSON ARTIFACT LOADERS
# =============================================================================

@st.cache_data(persist="disk", show_spinner=False)
def load_pop_activity_stats() -> Dict[str, Any]:
    """Load population vs activity statistics."""
    if not POP_ACTIVITY_STATS.exists():
        logger.warning(f"Pop activity stats not found: {POP_ACTIVITY_STATS}")
        return {}
    
    with open(POP_ACTIVITY_STATS, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(persist="disk", show_spinner=False)
def load_rural_urban_stats() -> Dict[str, Any]:
    """Load rural vs urban comparison statistics."""
    if not RURAL_URBAN_STATS.exists():
        logger.warning(f"Rural urban stats not found: {RURAL_URBAN_STATS}")
        return {}
    
    with open(RURAL_URBAN_STATS, "r", encoding="utf-8") as f:
        return json.load(f)


# =============================================================================
# VILLAGE SEARCH INDEX (Optimized Dictionary Lookup)
# =============================================================================

@st.cache_data(persist="disk", show_spinner=False)
def build_village_search_index() -> Tuple[Dict[str, Dict], Dict[str, List[str]]]:
    """
    Build optimized search index for instant village/pincode lookup.
    
    Returns:
        pincode_index: Dict[pincode] -> full record
        name_index: Dict[normalized_name] -> list of pincodes
    """
    df = load_pincode_aggregates(columns=PINCODE_SEARCH_COLS)
    
    if df.empty:
        return {}, {}
    
    # Build pincode -> record dictionary
    pincode_index = {}
    for _, row in df.iterrows():
        pincode = str(row["pincode"])
        pincode_index[pincode] = {
            "pincode": pincode,
            "district": str(row.get("district", "")),
            "state": str(row.get("state", "")),
            "population": float(row.get("population", 0)),
            "urban_flag": str(row.get("urban_flag", "unknown")),
            "total_activity": float(row.get("total_activity", 0)),
            "activity_per_100k": float(row.get("activity_per_100k", 0)),
            "is_service_desert": bool(row.get("is_service_desert", False)),
            "priority_score": float(row.get("priority_score", 0)),
            "priority_rank": int(row.get("priority_rank", 0)) if pd.notna(row.get("priority_rank")) else 0
        }
    
    # Build normalized district name -> pincode list (for fuzzy search)
    name_index = {}
    for _, row in df.iterrows():
        district = str(row.get("district", "")).lower().strip()
        pincode = str(row["pincode"])
        
        if district:
            if district not in name_index:
                name_index[district] = []
            name_index[district].append(pincode)
    
    logger.info(f"Village search index built: {len(pincode_index)} pincodes, {len(name_index)} districts")
    
    return pincode_index, name_index


def lookup_pincode(pincode: str) -> Optional[Dict]:
    """
    Instant pincode lookup from cached index.
    """
    pincode_index, _ = build_village_search_index()
    return pincode_index.get(str(pincode).strip())


def search_by_district(query: str, limit: int = 10) -> List[Dict]:
    """
    Search pincodes by district name.
    Returns list of matching records.
    """
    pincode_index, name_index = build_village_search_index()
    
    query_lower = query.lower().strip()
    results = []
    
    # Exact match first
    if query_lower in name_index:
        for pincode in name_index[query_lower][:limit]:
            if pincode in pincode_index:
                results.append(pincode_index[pincode])
    
    # Partial match
    if len(results) < limit:
        for district, pincodes in name_index.items():
            if query_lower in district and district != query_lower:
                for pincode in pincodes:
                    if pincode in pincode_index and len(results) < limit:
                        results.append(pincode_index[pincode])
    
    return results[:limit]


# =============================================================================
# AGGREGATED METRICS (For KPI Cards)
# =============================================================================

@st.cache_data(persist="disk", show_spinner=False)
def get_overview_metrics() -> Dict[str, Any]:
    """
    Get pre-aggregated metrics for the overview page.
    Single load, cached forever.
    """
    df = load_pincode_aggregates(columns=["pincode", "is_service_desert", "priority_score"])
    buckets = load_priority_buckets()
    districts = load_district_aggregates(columns=["district"])
    
    metrics = {
        "total_pincodes": len(df) if not df.empty else 0,
        "total_districts": len(districts) if not districts.empty else 0,
        "service_deserts": int(df["is_service_desert"].sum()) if not df.empty and "is_service_desert" in df.columns else 0,
        "critical_pincodes": 0,
        "high_pincodes": 0,
        "medium_pincodes": 0,
        "monitor_pincodes": 0
    }
    
    # Extract bucket counts
    if not buckets.empty:
        for _, row in buckets.iterrows():
            bucket = str(row.get("priority_bucket", "")).lower()
            count = int(row.get("pincodes", 0))
            if bucket == "critical":
                metrics["critical_pincodes"] = count
            elif bucket == "high":
                metrics["high_pincodes"] = count
            elif bucket == "medium":
                metrics["medium_pincodes"] = count
            elif bucket == "monitor":
                metrics["monitor_pincodes"] = count
    
    return metrics


@st.cache_data(persist="disk", show_spinner=False)
def get_urban_rural_split() -> Dict[str, int]:
    """Get urban vs rural pincode counts."""
    df = load_pincode_aggregates(columns=["pincode", "urban_flag"])
    
    if df.empty:
        return {"urban": 0, "rural": 0, "unknown": 0}
    
    counts = df["urban_flag"].value_counts().to_dict()
    
    return {
        "urban": int(counts.get("urban", 0)),
        "rural": int(counts.get("rural", 0)),
        "unknown": int(counts.get("unknown", 0))
    }


@st.cache_data(persist="disk", show_spinner=False)
def get_state_summary() -> pd.DataFrame:
    """Get state-level aggregated metrics."""
    df = load_district_aggregates(columns=DISTRICT_FULL_COLS)
    
    if df.empty:
        return pd.DataFrame()
    
    state_summary = df.groupby("state").agg({
        "population": "sum",
        "total_activity": "sum",
        "bio_count": "sum",
        "demo_count": "sum",
        "enroll_count": "sum"
    }).reset_index()
    
    state_summary["activity_per_100k"] = (
        state_summary["total_activity"] / (state_summary["population"] / 100000)
    )
    
    state_summary = state_summary.sort_values("population", ascending=False)
    
    return optimize_dtypes(state_summary)


# =============================================================================
# DATA VALIDATION
# =============================================================================

def validate_data_sources() -> Dict[str, bool]:
    """Check which data sources are available."""
    return {
        "pincode_aggregates": PINCODE_AGGREGATES.exists(),
        "district_aggregates": DISTRICT_AGGREGATES.exists(),
        "priority_buckets": PRIORITY_BUCKETS.exists(),
        "policy_recommendations": POLICY_RECOMMENDATIONS.exists(),
        "pop_activity_stats": POP_ACTIVITY_STATS.exists(),
        "rural_urban_stats": RURAL_URBAN_STATS.exists()
    }


def get_data_load_status() -> Tuple[bool, str]:
    """
    Check if critical data is loadable.
    Returns (success, message).
    """
    status = validate_data_sources()
    
    critical = ["pincode_aggregates", "district_aggregates"]
    missing = [k for k in critical if not status.get(k, False)]
    
    if missing:
        return False, f"Missing critical data: {', '.join(missing)}"
    
    return True, "All data sources available"


# =============================================================================
# PRELOAD FUNCTION (Call at app start)
# =============================================================================

def preload_all_data():
    """
    Preload all cached data at application startup.
    This triggers disk cache population.
    """
    logger.info("Preloading data...")
    
    # Load core datasets
    _ = load_pincode_aggregates(columns=PINCODE_SEARCH_COLS)
    _ = load_district_aggregates(columns=DISTRICT_CORE_COLS)
    _ = load_priority_buckets()
    _ = get_overview_metrics()
    
    # Build search index
    _ = build_village_search_index()
    
    logger.info("Data preload complete")
