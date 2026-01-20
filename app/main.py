"""
UIDAI Insight Command Center - Main Application
================================================
Experience-first architecture for judge memory.
90-second flow: Framing -> Proof -> Case File -> Decision -> Trust
"""

import streamlit as st
from pathlib import Path

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="UIDAI Insight Command Center",
    page_icon="assets/favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "UIDAI Insight Command Center - Hackathon 2026"
    }
)

# =============================================================================
# IMPORTS
# =============================================================================
from config import (
    AADHAAR_BLUE, 
    SAFFRON, 
    STATIC_DIR,
    COLOR_CRITICAL,
    COLOR_SUCCESS,
    TEXT_SECONDARY
)

from data_handler import (
    preload_all_data,
    get_overview_metrics,
    get_state_summary,
    lookup_pincode,
    load_policy_recommendations,
    validate_data_sources
)

from experiences.framing import render_framing, render_framing_minimal
from experiences.proof import render_proof
from experiences.case_file import render_case_file, render_case_file_header
from experiences.decision import render_decision
from experiences.trust import render_trust, render_trust_footer
from experiences.insights import render_insights

# =============================================================================
# LOAD CSS
# =============================================================================
def load_css():
    css_file = STATIC_DIR / "style.css"
    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# =============================================================================
# SESSION STATE
# =============================================================================
def init_session_state():
    if "data_loaded" not in st.session_state:
        st.session_state.data_loaded = False
    if "search_query" not in st.session_state:
        st.session_state.search_query = ""
    if "selected_pincode" not in st.session_state:
        st.session_state.selected_pincode = None
    if "selected_record" not in st.session_state:
        st.session_state.selected_record = None
    if "current_view" not in st.session_state:
        st.session_state.current_view = "overview"

init_session_state()

# =============================================================================
# LOADING
# =============================================================================
def show_loading():
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("""
        <div style="
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 60vh;
            text-align: center;
        ">
            <h1 style="
                background: linear-gradient(135deg, #1A73E8, #FF9933);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-size: 2rem;
                font-weight: 700;
                margin-bottom: 1rem;
            ">UIDAI Insight Command Center</h1>
            <p style="color: #8B949E; font-size: 0.9rem;">Initializing...</p>
        </div>
        """, unsafe_allow_html=True)
    return placeholder

if not st.session_state.data_loaded:
    loading = show_loading()
    preload_all_data()
    st.session_state.data_loaded = True
    loading.empty()
    st.rerun()

# =============================================================================
# URL PARAMS
# =============================================================================
def handle_url_params():
    params = st.query_params
    if "pincode" in params:
        pincode = params["pincode"]
        if pincode and pincode != st.session_state.selected_pincode:
            st.session_state.selected_pincode = pincode
            st.session_state.search_query = pincode
            record = lookup_pincode(pincode)
            if record:
                st.session_state.selected_record = record
    if "view" in params:
        view = params["view"]
        if view in ["overview", "analysis", "action", "insights"]:
            st.session_state.current_view = view

handle_url_params()

# =============================================================================
# SIDEBAR
# =============================================================================
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="padding: 0.5rem 0 1rem 0;">
            <h1 style="
                background: linear-gradient(135deg, #1A73E8, #FF9933);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-size: 1.4rem;
                font-weight: 700;
                margin: 0;
            ">UIDAI Insight Center</h1>
            <p style="color: #8B949E; font-size: 0.8rem; margin-top: 0.25rem;">
                Decision Support System
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation
        views = {
            "overview": "Overview",
            "analysis": "Analysis",
            "action": "Action Plan",
            "insights": "Insights"
        }
        
        for key, label in views.items():
            is_selected = st.session_state.current_view == key
            if st.button(
                label,
                key=f"nav_{key}",
                use_container_width=True,
                type="primary" if is_selected else "secondary"
            ):
                st.session_state.current_view = key
                st.query_params["view"] = key
                st.rerun()
        
        st.markdown("---")
        
        # Pincode Search
        st.markdown("""
        <p style="color: #E6EDF3; font-size: 0.85rem; font-weight: 500; margin-bottom: 0.5rem;">
            Pincode Lookup
        </p>
        """, unsafe_allow_html=True)
        
        search = st.text_input(
            "Search",
            value=st.session_state.search_query,
            placeholder="Enter 6-digit pincode",
            key="search_input",
            label_visibility="collapsed"
        )
        
        if search != st.session_state.search_query:
            st.session_state.search_query = search
            if search.isdigit() and len(search) == 6:
                record = lookup_pincode(search)
                if record:
                    st.session_state.selected_pincode = search
                    st.session_state.selected_record = record
                    st.query_params["pincode"] = search
        
        if st.session_state.selected_record:
            rec = st.session_state.selected_record
            desert_badge = ""
            if rec.get("is_service_desert"):
                desert_badge = '<span style="background: #F8514930; color: #F85149; padding: 2px 6px; border-radius: 3px; font-size: 0.65rem; margin-left: 6px;">DESERT</span>'
            
            st.markdown(f"""<div style="background: rgba(26, 115, 232, 0.1); border: 1px solid rgba(26, 115, 232, 0.3); border-radius: 8px; padding: 0.75rem; margin-top: 0.5rem;">
<div style="display: flex; align-items: center;">
<span style="color: #1A73E8; font-size: 1.2rem; font-weight: 700;">{rec.get('pincode', '')}</span>
{desert_badge}
</div>
<p style="color: #E6EDF3; font-size: 0.8rem; margin: 0.25rem 0 0 0;">{str(rec.get('district', '')).replace('_', ' ').title()}</p>
<p style="color: #8B949E; font-size: 0.75rem; margin: 0.25rem 0 0 0;">{str(rec.get('state', '')).replace('_', ' ').title()}</p>
</div>""", unsafe_allow_html=True)
            
            if st.button("Clear", use_container_width=True, type="secondary"):
                st.session_state.selected_pincode = None
                st.session_state.selected_record = None
                st.session_state.search_query = ""
                if "pincode" in st.query_params:
                    del st.query_params["pincode"]
                st.rerun()
        
        st.markdown("---")
        
        # Status
        status = validate_data_sources()
        healthy = all(status.values())
        color = "#3FB950" if healthy else "#F85149"
        text = "Systems operational" if healthy else "Data incomplete"
        
        st.markdown(f"""
        <div style="text-align: center; padding: 0.5rem 0;">
            <span style="display: inline-block; width: 6px; height: 6px; background: {color}; border-radius: 50%; margin-right: 6px;"></span>
            <span style="color: #6E7681; font-size: 0.7rem;">{text}</span>
        </div>
        """, unsafe_allow_html=True)

render_sidebar()

# =============================================================================
# MAIN CONTENT
# =============================================================================
def render_main():
    metrics = get_overview_metrics()
    state_summary = get_state_summary()
    policy_df = load_policy_recommendations(top_n=100)
    data_status = validate_data_sources()
    
    view = st.session_state.current_view
    
    if view == "overview":
        # OVERVIEW: Framing + Proof
        render_framing(total_pincodes=metrics.get("total_pincodes", 19879))
        st.markdown("---")
        render_proof(
            state_summary=state_summary,
            metrics=metrics,
            district_count=metrics.get("total_districts", 865)
        )
        render_trust_footer()
    
    elif view == "analysis":
        # ANALYSIS: Framing minimal + Case File
        render_framing_minimal()
        
        render_case_file_header()
        
        # Get policy record for selected pincode if available
        policy_record = None
        if st.session_state.selected_pincode and not policy_df.empty:
            match = policy_df[policy_df["pincode"] == st.session_state.selected_pincode]
            if not match.empty:
                policy_record = match.iloc[0].to_dict()
        
        render_case_file(
            record=st.session_state.selected_record,
            policy_record=policy_record
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        render_trust(data_status)
        render_trust_footer()
    
    elif view == "action":
        # ACTION: Decision + Trust
        render_framing_minimal()
        
        render_decision(
            metrics=metrics,
            policy_df=policy_df
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        render_trust(data_status)
        render_trust_footer()
    
    elif view == "insights":
        # INSIGHTS: Full analytical insights from notebook
        render_insights()
        render_trust_footer()

render_main()
