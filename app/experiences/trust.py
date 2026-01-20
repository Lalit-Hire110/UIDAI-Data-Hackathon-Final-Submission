"""
Experience Block 5: The Trust Layer
====================================
Provenance, artifact names, limitations.
No editorial justification.
"""

import streamlit as st
from datetime import datetime
from typing import Dict


# Artifact paths for provenance
ARTIFACT_MANIFEST = {
    "pincode_aggregates": "data/outputs/streamlit/pincode_aggregates.csv",
    "district_aggregates": "data/outputs/streamlit/district_aggregates.csv",
    "priority_bucket_summary": "data/outputs/final_decision_matrix/priority_bucket_summary.csv",
    "policy_recommendations": "data/outputs/domains/policy_recommendations.csv",
    "demand_behavior": "data/outputs/domains/demand_behavior/demand_behavior_summary.csv",
    "capacity_mismatch": "data/outputs/domains/capacity_mismatch/capacity_mismatch_summary.csv",
    "service_quality": "data/outputs/domains/service_quality/service_quality_summary.csv",
    "temporal": "data/outputs/domains/temporal/temporal_summary.csv"
}


def render_trust(data_status: Dict[str, bool]):
    """
    Render the trust layer with artifact provenance.
    No editorial justification text.
    """
    
    # Current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    with st.expander("Data Provenance", expanded=False):
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <h4 style="color: #E6EDF3; font-size: 0.95rem; margin: 0 0 0.75rem 0;">Source Artifacts</h4>
            """, unsafe_allow_html=True)
            
            for name, path in list(ARTIFACT_MANIFEST.items())[:4]:
                available = data_status.get(name.split("/")[-1].replace("_summary", "").replace("_aggregates", ""), True)
                status_color = "#3FB950" if available else "#F85149"
                
                st.markdown(f"""
                <div style="
                    margin-bottom: 0.5rem;
                    padding: 0.5rem;
                    background: rgba(22, 27, 34, 0.5);
                    border-radius: 4px;
                ">
                    <p style="color: #E6EDF3; font-size: 0.8rem; margin: 0; font-family: monospace;">{path.split('/')[-1]}</p>
                    <p style="color: #6E7681; font-size: 0.7rem; margin: 0.25rem 0 0 0;">{path}</p>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <h4 style="color: #E6EDF3; font-size: 0.95rem; margin: 0 0 0.75rem 0;">Domain Artifacts</h4>
            """, unsafe_allow_html=True)
            
            for name, path in list(ARTIFACT_MANIFEST.items())[4:]:
                st.markdown(f"""
                <div style="
                    margin-bottom: 0.5rem;
                    padding: 0.5rem;
                    background: rgba(22, 27, 34, 0.5);
                    border-radius: 4px;
                ">
                    <p style="color: #E6EDF3; font-size: 0.8rem; margin: 0; font-family: monospace;">{path.split('/')[-1]}</p>
                    <p style="color: #6E7681; font-size: 0.7rem; margin: 0.25rem 0 0 0;">{path}</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Data coverage from notebook
        st.markdown("""
        <h4 style="color: #E6EDF3; font-size: 0.95rem; margin: 0 0 0.75rem 0;">Coverage Statistics</h4>
        """, unsafe_allow_html=True)
        
        # These are exact notebook output values
        coverage_stats = [
            ("Total pincodes", "19,879"),
            ("Service deserts identified", "1,042"),
            ("Districts", "865"),
            ("Valid population coverage", "76.18%"),
            ("Under-served pincodes", "1,636")
        ]
        
        for label, value in coverage_stats:
            st.markdown(f"""
            <div style="
                display: flex;
                justify-content: space-between;
                padding: 0.4rem 0;
                border-bottom: 1px solid rgba(255,255,255,0.05);
            ">
                <span style="color: #8B949E; font-size: 0.8rem;">{label}</span>
                <span style="color: #E6EDF3; font-size: 0.8rem; font-weight: 600;">{value}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Limitations from notebook
        st.markdown("""
        <h4 style="color: #E6EDF3; font-size: 0.95rem; margin: 0 0 0.75rem 0;">Known Limitations</h4>
        """, unsafe_allow_html=True)
        
        # From notebook markdown cells
        limitations = [
            "Activity data is aggregated monthly; daily patterns not captured",
            "Population projections based on 2011 Census with CAGR",
            "Service desert threshold: below 50% of district average",
            "Urban/rural classification available for ~76% of records"
        ]
        
        for lim in limitations:
            st.markdown(f"""
            <div style="
                display: flex;
                align-items: flex-start;
                margin-bottom: 0.5rem;
            ">
                <span style="color: #6E7681; margin-right: 0.5rem;">-</span>
                <span style="color: #8B949E; font-size: 0.8rem; line-height: 1.4;">{lim}</span>
            </div>
            """, unsafe_allow_html=True)
        
        # Timestamp
        st.markdown(f"""
        <div style="
            text-align: right;
            margin-top: 1rem;
            padding-top: 0.75rem;
            border-top: 1px solid rgba(255,255,255,0.05);
        ">
            <span style="color: #6E7681; font-size: 0.7rem;">
                Rendered: {timestamp}
            </span>
        </div>
        """, unsafe_allow_html=True)


def render_trust_footer():
    """
    Minimal trust footer for persistent display.
    """
    
    st.markdown("""
    <div style="
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
    ">
        <p style="color: #6E7681; font-size: 0.75rem; margin: 0;">
            UIDAI Insight Center | Data from UIDAI_Master_Analysis.ipynb | 
            19,879 pincodes
        </p>
        <p style="color: #4A5568; font-size: 0.7rem; margin: 0.25rem 0 0 0;">
            Hackathon 2026
        </p>
    </div>
    """, unsafe_allow_html=True)
