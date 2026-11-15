"""SustainTour India — main Streamlit application entry point."""
import streamlit as st
import plotly.io as pio

from src.constants import NAV_SECTIONS, NAV_ICONS
from src.styles import get_custom_css
from src.views.tourism_intelligence import render_tourism_intelligence
from src.views.sustainability_intelligence import render_sustainability_intelligence
from src.views.state_comparison import render_state_comparison
from src.views.ml_intelligence import render_ml_intelligence
from src.views.planning_studio import render_planning_studio
from src.views.ai_policy_assistant import render_ai_policy_assistant

st.set_page_config(
    page_title="SustainTour India — Sustainable Tourism Intelligence",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(get_custom_css(), unsafe_allow_html=True)
pio.templates.default = "plotly_dark"

with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <span style="font-size:1.6rem;">🌿</span>
        <div class="sidebar-logo-text">SustainTour India</div>
    </div>
    <div class="sidebar-subtitle">Sustainable Tourism Intelligence</div>
    """, unsafe_allow_html=True)

    st.markdown('<hr style="border-color:#244553; margin: 0.5rem 0 0.75rem 0;">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-nav-label">Navigation</div>', unsafe_allow_html=True)

    nav_options = [f"{NAV_ICONS[sec]}  {sec}" for sec in NAV_SECTIONS]
    selected_nav_str = st.radio(
        label="Module", options=nav_options, index=0, label_visibility="collapsed"
    )
    selected_section = selected_nav_str.split("  ", 1)[1]

    st.markdown('<hr style="border-color:#2A4D49; margin: 1rem 0 0.75rem 0;">', unsafe_allow_html=True)
    st.markdown("""
    <div class="sidebar-info-box">
        <b>Coverage</b><br>
        36 States &amp; UTs · 2011–2025<br>
        <b>Environment</b><br>
        Forest · Groundwater · SDG<br>
        <b>Sources</b><br>
        MoT · RBI · FSI · CGWB · NITI Aayog<br>
    </div>
    """, unsafe_allow_html=True)

if selected_section == "Tourism Intelligence":
    render_tourism_intelligence()
elif selected_section == "Sustainability Intelligence":
    render_sustainability_intelligence()
elif selected_section == "State Comparison":
    render_state_comparison()
elif selected_section == "Machine Learning Intelligence":
    render_ml_intelligence()
elif selected_section == "Sustainable Planning Studio":
    render_planning_studio()
elif selected_section == "AI Policy Assistant":
    render_ai_policy_assistant()
else:
    st.error(f"Unknown module: {selected_section}")

st.markdown("""
<div class="app-footer">
    <b>SustainTour India</b> &nbsp;·&nbsp; Data-Driven Sustainable Tourism Planning and Visualization<br>
</div>
""", unsafe_allow_html=True)
