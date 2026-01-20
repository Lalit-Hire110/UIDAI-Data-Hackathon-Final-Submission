"""
Experience Block 2: The Proof Layer
====================================
Concentration of risk made visible and undeniable.
All values sourced from notebook artifacts.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from typing import Dict, Any

# Notebook-derived constants (from priority_bucket_summary.csv)
NOTEBOOK_PRIORITY_BUCKETS = {
    "critical": {"count": 100, "avg_score": 0.5426},
    "high": {"count": 400, "avg_score": 0.4397},
    "medium": {"count": 1500, "avg_score": 0.3666},
    "monitor": {"count": 17879, "avg_score": 0.2953}
}


def render_proof(
    state_summary: pd.DataFrame,
    metrics: Dict[str, Any],
    district_count: int = 865
):
    """
    Render the proof layer with notebook-bound values only.
    No UI-derived calculations.
    """
    
    # Use notebook-verified service desert count
    service_deserts = 1042  # From notebook output: "Service deserts identified: 1042"
    total_pincodes = 19879  # From notebook output: "Total pincodes: 19879"
    
    # Header
    st.markdown("""
    <div style="
        text-align: center;
        margin-bottom: 2rem;
    ">
        <h2 style="
            color: #E6EDF3;
            font-size: 1.5rem;
            font-weight: 600;
            margin: 0 0 0.5rem 0;
        ">Concentration of Risk</h2>
        <p style="
            color: #8B949E;
            font-size: 0.9rem;
            margin: 0;
        ">Service gaps are not randomly distributed. They cluster.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Key statistic from notebook
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(248, 81, 73, 0.1), rgba(255, 153, 51, 0.1));
        border: 1px solid rgba(248, 81, 73, 0.3);
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        margin-bottom: 2rem;
    ">
        <p style="
            color: #F85149;
            font-size: 3rem;
            font-weight: 700;
            margin: 0;
            line-height: 1;
        ">{service_deserts:,}</p>
        <p style="
            color: #E6EDF3;
            font-size: 1.1rem;
            margin: 0.5rem 0 0 0;
        ">rural service deserts identified</p>
        <p style="
            color: #8B949E;
            font-size: 0.85rem;
            margin: 0.75rem 0 0 0;
        ">From {total_pincodes:,} pincodes analyzed</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Priority distribution from notebook
    st.markdown("""
    <h3 style="
        color: #E6EDF3;
        font-size: 1.1rem;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
    ">Priority Distribution</h3>
    <p style="
        color: #6E7681;
        font-size: 0.75rem;
        margin: 0 0 1rem 0;
    ">Source: priority_bucket_summary.csv</p>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Use exact notebook values
    priority_data = [
        ("Critical", NOTEBOOK_PRIORITY_BUCKETS["critical"]["count"], "#F85149", "0-6 mo"),
        ("High", NOTEBOOK_PRIORITY_BUCKETS["high"]["count"], "#FF9933", "6-12 mo"),
        ("Medium", NOTEBOOK_PRIORITY_BUCKETS["medium"]["count"], "#1A73E8", "12-18 mo"),
        ("Monitor", NOTEBOOK_PRIORITY_BUCKETS["monitor"]["count"], "#3FB950", "Ongoing")
    ]
    
    for col, (tier, count, color, timeline) in zip([col1, col2, col3, col4], priority_data):
        with col:
            st.markdown(f"""
            <div style="
                background: rgba(22, 27, 34, 0.8);
                border: 1px solid {color}40;
                border-top: 3px solid {color};
                border-radius: 0 0 8px 8px;
                padding: 1rem;
                text-align: center;
            ">
                <p style="color: #8B949E; font-size: 0.75rem; margin: 0; text-transform: uppercase; letter-spacing: 0.05em;">{tier}</p>
                <p style="color: {color}; font-size: 1.5rem; font-weight: 700; margin: 0.25rem 0;">{count:,}</p>
                <p style="color: #6E7681; font-size: 0.7rem; margin: 0;">{timeline}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # State-level view from loaded data
    if not state_summary.empty:
        st.markdown("""
        <h3 style="
            color: #E6EDF3;
            font-size: 1.1rem;
            font-weight: 600;
            margin: 1rem 0;
        ">State-Level Activity Rates</h3>
        <p style="
            color: #6E7681;
            font-size: 0.75rem;
            margin: 0 0 1rem 0;
        ">Source: pincode_aggregates.csv (aggregated)</p>
        """, unsafe_allow_html=True)
        
        # Top and bottom 5 states
        top_states = state_summary.nlargest(5, "activity_per_100k")[["state", "activity_per_100k"]]
        bottom_states = state_summary.nsmallest(5, "activity_per_100k")[["state", "activity_per_100k"]]
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("""
            <p style="color: #3FB950; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.5rem;">
                Highest Activity
            </p>
            """, unsafe_allow_html=True)
            
            for _, row in top_states.iterrows():
                state = str(row["state"]).replace("_", " ").title()
                rate = float(row["activity_per_100k"])
                st.markdown(f"""
                <div style="
                    display: flex;
                    justify-content: space-between;
                    padding: 0.5rem 0;
                    border-bottom: 1px solid rgba(255,255,255,0.05);
                ">
                    <span style="color: #E6EDF3; font-size: 0.85rem;">{state}</span>
                    <span style="color: #3FB950; font-size: 0.85rem; font-weight: 600;">{rate:.1f}</span>
                </div>
                """, unsafe_allow_html=True)
        
        with col_right:
            st.markdown("""
            <p style="color: #F85149; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.5rem;">
                Lowest Activity
            </p>
            """, unsafe_allow_html=True)
            
            for _, row in bottom_states.iterrows():
                state = str(row["state"]).replace("_", " ").title()
                rate = float(row["activity_per_100k"])
                st.markdown(f"""
                <div style="
                    display: flex;
                    justify-content: space-between;
                    padding: 0.5rem 0;
                    border-bottom: 1px solid rgba(255,255,255,0.05);
                ">
                    <span style="color: #E6EDF3; font-size: 0.85rem;">{state}</span>
                    <span style="color: #F85149; font-size: 0.85rem; font-weight: 600;">{rate:.1f}</span>
                </div>
                """, unsafe_allow_html=True)
