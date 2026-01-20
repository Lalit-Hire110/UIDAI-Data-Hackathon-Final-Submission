"""
Experience Block 3: The Case File
==================================
Pincode-level metrics display only.
No prescriptive language. No recommendations.
All values from notebook artifacts.
"""

import streamlit as st
from typing import Dict, Optional


def render_case_file(record: Optional[Dict] = None, policy_record: Optional[Dict] = None):
    """
    Render metrics for a single pincode.
    Notebook-bound: shows only what exists in artifacts.
    """
    
    if not record:
        render_case_file_placeholder()
        return
    
    pincode = record.get("pincode", "---")
    district = str(record.get("district", "Unknown")).replace("_", " ").title()
    state = str(record.get("state", "Unknown")).replace("_", " ").title()
    population = record.get("population", 0)
    urban_flag = str(record.get("urban_flag", "unknown")).title()
    activity_per_100k = record.get("activity_per_100k", 0)
    priority_score = record.get("priority_score", 0)
    is_desert = record.get("is_service_desert", False)
    
    # Policy details from policy_recommendations.csv if available
    composite_priority = None
    mismatch_type = None
    priority_rank = None
    
    if policy_record:
        composite_priority = policy_record.get("composite_priority")
        mismatch_type = str(policy_record.get("mismatch_type", "")).replace("_", " ")
        priority_rank = policy_record.get("priority_rank")
    
    # Service desert badge
    desert_badge = ""
    if is_desert:
        desert_badge = """<span style="background: rgba(248, 81, 73, 0.2); color: #F85149; padding: 4px 10px; border-radius: 4px; font-size: 0.7rem; font-weight: 600; letter-spacing: 0.05em; margin-left: 12px;">SERVICE DESERT</span>"""
    
    # Rank badge if in Top 100
    rank_badge = ""
    if priority_rank and priority_rank <= 100:
        rank_badge = f"""<span style="background: rgba(255, 153, 51, 0.2); color: #FF9933; padding: 4px 10px; border-radius: 4px; font-size: 0.7rem; font-weight: 600; letter-spacing: 0.05em; margin-left: 8px;">RANK #{int(priority_rank)}</span>"""
    
    st.markdown(f"""<div class="case-file" style="background: rgba(22, 27, 34, 0.9); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 0; overflow: hidden;">
<!-- Header -->
<div style="background: linear-gradient(135deg, rgba(26, 115, 232, 0.15), rgba(255, 153, 51, 0.1)); padding: 1.5rem; border-bottom: 1px solid rgba(255, 255, 255, 0.1);">
<div style="display: flex; align-items: center; flex-wrap: wrap;">
<span style="color: #1A73E8; font-size: 1.75rem; font-weight: 700; font-family: 'SF Mono', Consolas, monospace;">{pincode}</span>
{desert_badge}
{rank_badge}
</div>
<p style="color: #E6EDF3; font-size: 1rem; margin: 0.5rem 0 0 0;">{district}, {state}</p>
</div>
<!-- Metrics Grid (from pincode_aggregates.csv) -->
<div style="display: grid; grid-template-columns: repeat(3, 1fr); border-bottom: 1px solid rgba(255, 255, 255, 0.1);">
<div style="padding: 1rem; border-right: 1px solid rgba(255, 255, 255, 0.05);">
<p style="color: #8B949E; font-size: 0.7rem; margin: 0; text-transform: uppercase; letter-spacing: 0.05em;">Population</p>
<p style="color: #E6EDF3; font-size: 1.25rem; font-weight: 600; margin: 0.25rem 0 0 0;">{population:,.0f}</p>
</div>
<div style="padding: 1rem; border-right: 1px solid rgba(255, 255, 255, 0.05);">
<p style="color: #8B949E; font-size: 0.7rem; margin: 0; text-transform: uppercase; letter-spacing: 0.05em;">Activity / 100k</p>
<p style="color: #1A73E8; font-size: 1.25rem; font-weight: 600; margin: 0.25rem 0 0 0;">{activity_per_100k:.1f}</p>
</div>
<div style="padding: 1rem;">
<p style="color: #8B949E; font-size: 0.7rem; margin: 0; text-transform: uppercase; letter-spacing: 0.05em;">Classification</p>
<p style="color: #E6EDF3; font-size: 1.25rem; font-weight: 600; margin: 0.25rem 0 0 0;">{urban_flag}</p>
</div>
</div>
<!-- Notebook-derived classification (if available) -->
{"" if not mismatch_type else f'<div style="padding: 1rem 1.5rem; border-bottom: 1px solid rgba(255, 255, 255, 0.1); background: rgba(248, 81, 73, 0.03);"><p style="color: #8B949E; font-size: 0.7rem; margin: 0; text-transform: uppercase; letter-spacing: 0.05em;">Mismatch Type</p><p style="color: #E6EDF3; font-size: 0.95rem; margin: 0.25rem 0 0 0;">{mismatch_type}</p><p style="color: #6E7681; font-size: 0.7rem; margin: 0.25rem 0 0 0;">Source: policy_recommendations.csv</p></div>'}
<!-- Priority Score Footer -->
<div style="padding: 1rem 1.5rem; background: rgba(0, 0, 0, 0.2); display: flex; justify-content: space-between; align-items: center;">
<div>
<span style="color: #6E7681; font-size: 0.75rem;">Priority Score</span>
<p style="color: #6E7681; font-size: 0.65rem; margin: 0;">pincode_aggregates.csv</p>
</div>
<span style="color: #FF9933; font-size: 1.1rem; font-weight: 700; font-family: 'SF Mono', Consolas, monospace;">{priority_score:.3f}</span>
</div>
{"" if not composite_priority else f'<div style="padding: 0.75rem 1.5rem; background: rgba(0, 0, 0, 0.3); display: flex; justify-content: space-between; align-items: center; border-top: 1px solid rgba(255, 255, 255, 0.05);"><div><span style="color: #6E7681; font-size: 0.75rem;">Composite Priority</span><p style="color: #6E7681; font-size: 0.65rem; margin: 0;">policy_recommendations.csv</p></div><span style="color: #1A73E8; font-size: 1.1rem; font-weight: 700; font-family: \'SF Mono\', Consolas, monospace;">{composite_priority:.4f}</span></div>'}
</div>""", unsafe_allow_html=True)


def render_case_file_placeholder():
    """Placeholder when no pincode is selected."""
    
    st.markdown("""<div style="background: rgba(22, 27, 34, 0.6); border: 1px dashed rgba(255, 255, 255, 0.2); border-radius: 12px; padding: 3rem; text-align: center;">
<p style="color: #8B949E; font-size: 1rem; margin: 0 0 0.5rem 0;">Pincode Metrics</p>
<p style="color: #6E7681; font-size: 0.85rem; margin: 0;">Enter a 6-digit pincode in the sidebar to view artifact data</p>
</div>""", unsafe_allow_html=True)


def render_case_file_header():
    """Section header for case file area."""
    
    st.markdown("""<h2 style="color: #E6EDF3; font-size: 1.25rem; font-weight: 600; margin: 2rem 0 0.5rem 0;">Pincode Metrics</h2>
<p style="color: #8B949E; font-size: 0.85rem; margin: 0 0 1rem 0;">Data sourced from pincode_aggregates.csv and policy_recommendations.csv</p>""", unsafe_allow_html=True)
