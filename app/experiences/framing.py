"""
Experience Block 1: The Framing Moment
======================================
The opening thesis. Collapses complexity into one idea.
0-10 seconds of judge attention.
"""

import streamlit as st


def render_framing(total_pincodes: int = 19879):
    """
    Render the framing moment.
    One thesis. One context line. Nothing else.
    """
    
    st.markdown(f"""<div class="framing-container" style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 40vh; text-align: center; padding: 3rem 2rem; animation: fadeIn 1.2s ease-out;">
<h1 class="thesis-statement" style="font-size: 2.25rem; font-weight: 600; line-height: 1.4; color: #E6EDF3; max-width: 700px; margin: 0 0 1.5rem 0;">Aadhaar does not fail everywhere.<br><span style="background: linear-gradient(135deg, #1A73E8, #FF9933); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">It fails predictably, locally, and fixably.</span></h1>
<p class="context-line" style="font-size: 0.95rem; color: #8B949E; font-weight: 400; letter-spacing: 0.02em; margin: 0;">Derived from pincode-level analysis across {total_pincodes:,} locations.</p>
</div>
<style>
@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
</style>""", unsafe_allow_html=True)


def render_framing_minimal():
    """
    Minimal framing for page headers.
    Used when framing is not the primary focus.
    """
    
    st.markdown("""<div style="text-align: center; padding: 1rem 0 2rem 0; border-bottom: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 2rem;">
<p style="font-size: 1rem; color: #8B949E; margin: 0; font-style: italic;">Aadhaar fails predictably, locally, and fixably.</p>
</div>""", unsafe_allow_html=True)
