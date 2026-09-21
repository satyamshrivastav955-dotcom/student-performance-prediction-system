"""
dashboard/app.py — Student Success entry point.
Registers application pages via Streamlit Navigation API and runs the selected view.
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DASH_DIR = Path(__file__).resolve().parent
for p in (str(PROJECT_ROOT), str(DASH_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

import streamlit as st

st.set_page_config(
    page_title="Student Success",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Configure pages
p_overview   = st.Page("pages/1_Overview.py",             title="Overview",             icon="🏠", default=True)
p_predictor  = st.Page("pages/2_Individual_Predictor.py", title="Student Check-In",     icon="👤")
p_whatif     = st.Page("pages/3_What_If_Simulator.py",    title="Explore Improvements", icon="📈")
p_cohort     = st.Page("pages/4_Cohort_Simulator.py",     title="Class Insights",       icon="👥")
p_analytics  = st.Page("pages/6_Analytics.py",            title="Cohort Analytics",     icon="📊")
p_fairness   = st.Page("pages/5_Model_and_Fairness.py",   title="Trust & Fairness",     icon="🛡️")
p_about      = st.Page("pages/7_About.py",                title="About Project",        icon="ℹ️")

pg = st.navigation({
    "Intelligence": [p_overview, p_predictor, p_whatif, p_cohort, p_analytics],
    "Governance & Trust": [p_fairness, p_about],
})

pg.run()
