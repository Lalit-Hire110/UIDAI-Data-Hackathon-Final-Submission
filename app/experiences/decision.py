"""
Experience Block 4: The Decision Layer
=======================================
Priority matrix from notebook artifacts.
No editorial language. Declarative closure only.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any

# Notebook-derived constants
NOTEBOOK_PRIORITY_BUCKETS = {
    "critical": {"count": 100, "avg_score": 0.5426, "timeline": "0-6 months"},
    "high": {"count": 400, "avg_score": 0.4397, "timeline": "6-12 months"},
    "medium": {"count": 1500, "avg_score": 0.3666, "timeline": "12-18 months"},
    "monitor": {"count": 17879, "avg_score": 0.2953, "timeline": "Ongoing"}
}


def render_decision(
    metrics: Dict[str, Any],
    policy_df: pd.DataFrame
):
    """
    Render the decision layer with notebook-bound values.
    Sources: priority_bucket_summary.csv, policy_recommendations.csv
    """
    
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
        ">Priority Intervention Framework</h2>
        <p style="
            color: #6E7681;
            font-size: 0.75rem;
            margin: 0;
        ">Source: final_decision_matrix/priority_bucket_summary.csv</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Priority tiers with notebook values
    tiers = [
        {
            "name": "Critical",
            "count": NOTEBOOK_PRIORITY_BUCKETS["critical"]["count"],
            "avg_score": NOTEBOOK_PRIORITY_BUCKETS["critical"]["avg_score"],
            "timeline": NOTEBOOK_PRIORITY_BUCKETS["critical"]["timeline"],
            "color": "#F85149"
        },
        {
            "name": "High",
            "count": NOTEBOOK_PRIORITY_BUCKETS["high"]["count"],
            "avg_score": NOTEBOOK_PRIORITY_BUCKETS["high"]["avg_score"],
            "timeline": NOTEBOOK_PRIORITY_BUCKETS["high"]["timeline"],
            "color": "#FF9933"
        },
        {
            "name": "Medium",
            "count": NOTEBOOK_PRIORITY_BUCKETS["medium"]["count"],
            "avg_score": NOTEBOOK_PRIORITY_BUCKETS["medium"]["avg_score"],
            "timeline": NOTEBOOK_PRIORITY_BUCKETS["medium"]["timeline"],
            "color": "#1A73E8"
        },
        {
            "name": "Monitor",
            "count": NOTEBOOK_PRIORITY_BUCKETS["monitor"]["count"],
            "avg_score": NOTEBOOK_PRIORITY_BUCKETS["monitor"]["avg_score"],
            "timeline": NOTEBOOK_PRIORITY_BUCKETS["monitor"]["timeline"],
            "color": "#3FB950"
        }
    ]
    
    for tier in tiers:
        st.markdown(f"""
        <div style="
            background: rgba(22, 27, 34, 0.8);
            border-left: 4px solid {tier["color"]};
            border-radius: 0 8px 8px 0;
            padding: 1rem 1.25rem;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        ">
            <div style="flex: 1;">
                <div style="display: flex; align-items: baseline; gap: 0.75rem;">
                    <span style="
                        color: {tier["color"]};
                        font-size: 1rem;
                        font-weight: 600;
                    ">{tier["name"]}</span>
                    <span style="
                        color: #6E7681;
                        font-size: 0.8rem;
                    ">{tier["timeline"]}</span>
                </div>
                <p style="
                    color: #8B949E;
                    font-size: 0.8rem;
                    margin: 0.25rem 0 0 0;
                ">Avg priority score: {tier["avg_score"]:.4f}</p>
            </div>
            <div style="
                text-align: right;
                padding-left: 1rem;
            ">
                <span style="
                    color: {tier["color"]};
                    font-size: 1.5rem;
                    font-weight: 700;
                ">{tier["count"]:,}</span>
                <p style="
                    color: #6E7681;
                    font-size: 0.7rem;
                    margin: 0;
                ">pincodes</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Top 100 table
    st.markdown("<br>", unsafe_allow_html=True)
    render_top_100_table(policy_df)


def render_html_table(df: pd.DataFrame, max_height: str = "400px"):
    """
    Render a custom HTML table with dark styling.
    Workaround for Streamlit dataframe white background issue.
    """
    
    # Build table HTML (no leading whitespace to prevent code block rendering)
    html = f"""<div style="background: rgba(22, 27, 34, 0.8); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; overflow: hidden; max-height: {max_height}; overflow-y: auto;">
<table style="width: 100%; border-collapse: collapse; font-size: 0.85rem;">
<thead style="position: sticky; top: 0; background: #0D1117; z-index: 10;">
<tr>"""
    
    # Add headers
    for col in df.columns:
        html += f"""<th style="padding: 0.75rem 1rem; text-align: left; color: #E6EDF3; font-weight: 600; border-bottom: 2px solid rgba(255, 255, 255, 0.2); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em;">{col}</th>"""
    
    html += """</tr></thead><tbody>"""
    
    # Add rows
    for idx, row in df.iterrows():
        # Alternate row colors for better readability
        bg_color = "rgba(22, 27, 34, 0.4)" if idx % 2 == 0 else "rgba(22, 27, 34, 0.6)"
        
        html += f"""<tr style="background: {bg_color}; transition: background 0.15s ease;" onmouseover="this.style.background='rgba(26, 115, 232, 0.1)'" onmouseout="this.style.background='{bg_color}'">"""
        
        for col_idx, (col, value) in enumerate(row.items()):
            # Special styling for rank column
            if col == "Rank":
                color = "#FF9933" if int(value) <= 100 else "#8B949E"
                font_weight = "700" if int(value) <= 100 else "400"
            else:
                color = "#C9D1D9"
                font_weight = "400"
            
            html += f"""<td style="padding: 0.75rem 1rem; color: {color}; border-bottom: 1px solid rgba(255, 255, 255, 0.05); font-weight: {font_weight};">{value}</td>"""
        
        html += """</tr>"""
    
    html += """</tbody></table></div>"""
    
    st.markdown(html, unsafe_allow_html=True)


def render_top_100_table(policy_df: pd.DataFrame):
    """
    Render the Top 100 priority pincodes table.
    Source: policy_recommendations.csv
    """
    
    st.markdown("""
    <h3 style="
        color: #E6EDF3;
        font-size: 1.1rem;
        font-weight: 600;
        margin: 1.5rem 0 0.5rem 0;
    ">Top 100 Priority Pincodes</h3>
    <p style="
        color: #6E7681;
        font-size: 0.75rem;
        margin: 0 0 1rem 0;
    ">Source: domains/policy_recommendations.csv</p>
    """, unsafe_allow_html=True)
    
    if policy_df.empty:
        st.markdown("""
        <div style="
            background: rgba(22, 27, 34, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 2rem;
            text-align: center;
            color: #8B949E;
        ">
            Loading artifact data...
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Prepare display dataframe
    display_df = policy_df.head(25).copy()
    
    # Format columns
    display_df["population"] = display_df["population"].apply(
        lambda x: f"{x/1000:.0f}K" if x < 1e6 else f"{x/1e6:.1f}M"
    )
    display_df["composite_priority"] = display_df["composite_priority"].apply(
        lambda x: f"{x:.4f}"
    )
    display_df["district"] = display_df["district"].apply(
        lambda x: str(x).replace("_", " ").title()
    )
    display_df["state"] = display_df["state"].apply(
        lambda x: str(x).replace("_", " ").title()
    )
    display_df["mismatch_type"] = display_df["mismatch_type"].apply(
        lambda x: str(x).replace("_", " ")
    )
    
    display_df = display_df.rename(columns={
        "priority_rank": "Rank",
        "pincode": "Pincode",
        "district": "District",
        "state": "State",
        "population": "Population",
        "mismatch_type": "Type",
        "composite_priority": "Priority"
    })
    
    # Use custom HTML table instead of st.dataframe
    render_html_table(
        display_df[["Rank", "Pincode", "District", "State", "Population", "Type", "Priority"]],
        max_height="500px"
    )
    
    # Expandable full list
    with st.expander("View Complete Priority List (100 Pincodes)"):
        full_df = policy_df.copy()
        full_df["population"] = full_df["population"].apply(
            lambda x: f"{x/1000:.0f}K" if x < 1e6 else f"{x/1e6:.1f}M"
        )
        full_df["composite_priority"] = full_df["composite_priority"].apply(
            lambda x: f"{x:.4f}"
        )
        full_df["district"] = full_df["district"].apply(
            lambda x: str(x).replace("_", " ").title()
        )
        full_df["state"] = full_df["state"].apply(
            lambda x: str(x).replace("_", " ").title()
        )
        full_df["mismatch_type"] = full_df["mismatch_type"].apply(
            lambda x: str(x).replace("_", " ")
        )
        
        full_df = full_df.rename(columns={
            "priority_rank": "Rank",
            "pincode": "Pincode",
            "district": "District",
            "state": "State",
            "population": "Population",
            "mismatch_type": "Type",
            "composite_priority": "Priority"
        })
        
        # Use custom HTML table for expandable list too
        render_html_table(
            full_df[["Rank", "Pincode", "District", "State", "Population", "Type", "Priority"]],
            max_height="600px"
        )
