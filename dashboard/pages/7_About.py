"""
About Project page — project overview, dataset, tech stack, modules, timeline, deliverables.

Matches the reference design: clean, card-based, with educational mission context.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DASH_DIR     = Path(__file__).resolve().parents[1]
for p in (str(PROJECT_ROOT), str(DASH_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

import streamlit as st

from theme import (
    inject_theme, section_heading, kpi_hero_row, footnote,
    icon, FOREST, BRASS, CLAY, INK, INK_SEC, INK_MUTED, LINE, SURFACE, PAPER,
)

st.set_page_config(
    page_title="About — Student Performance Prediction System",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_theme(active_page="about")

# ---------------------------------------------------------------------------
# Page hero
# ---------------------------------------------------------------------------
col_hero, col_img = st.columns([3, 1])
with col_hero:
    st.markdown(
        f"""
<div class="spps-page-hero anim-fade-up" style="min-height:unset;">
  <p class="spps-eyebrow">About the Project</p>
  <p class="spps-page-title">Student Performance<br>Prediction System</p>
  <p class="spps-page-desc" style="font-size:1.05rem;max-width:560px;">
    Turning data into opportunities for every learner.
  </p>
  <p style="font-size:0.9rem;color:var(--ink-muted);margin:0.75rem 0 0;max-width:560px;line-height:1.65;">
    A production-grade, ethically audited machine learning platform designed to predict
    student academic performance, explain the factors behind it, and suggest actionable
    steps for improvement — built for a brighter, more inclusive educational future.
  </p>
</div>
""",
        unsafe_allow_html=True,
    )

with col_img:
    st.markdown(
        f"""
<div style="display:flex;flex-direction:column;gap:0.5rem;align-items:flex-end;padding-top:1.5rem;">
  <div style="background:rgba(35,68,52,.08);border:1px solid rgba(35,68,52,.2);
       border-radius:12px;padding:1rem 1.25rem;text-align:center;">
    <div style="font-family:var(--font-display);font-size:0.75rem;font-weight:600;
         color:var(--brass);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.35rem;">
      Education is not just about what we learn,
    </div>
    <div style="font-family:var(--font-display);font-size:0.8rem;color:var(--ink-muted);">
      but who we become.
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

# Capability pills row
st.markdown(
    f"""
<div style="display:flex;gap:1rem;margin:1.25rem 0 0.5rem;flex-wrap:wrap;">
  <div style="display:flex;align-items:center;gap:0.5rem;background:var(--surface);
       border:1px solid var(--line);border-radius:8px;padding:0.6rem 1rem;">
    {icon('chart', 16, FOREST)}
    <div>
      <div style="font-family:var(--font-display);font-size:0.9rem;font-weight:600;color:var(--ink);">Predict Performance</div>
    </div>
  </div>
  <div style="display:flex;align-items:center;gap:0.5rem;background:var(--surface);
       border:1px solid var(--line);border-radius:8px;padding:0.6rem 1rem;">
    {icon('lightbulb', 16, BRASS)}
    <div>
      <div style="font-family:var(--font-display);font-size:0.9rem;font-weight:600;color:var(--ink);">Explain What Matters</div>
    </div>
  </div>
  <div style="display:flex;align-items:center;gap:0.5rem;background:var(--surface);
       border:1px solid var(--line);border-radius:8px;padding:0.6rem 1rem;">
    {icon('arrow', 16, CLAY)}
    <div>
      <div style="font-family:var(--font-display);font-size:0.9rem;font-weight:600;color:var(--ink);">Recommend Actions</div>
    </div>
  </div>
  <div style="display:flex;align-items:center;gap:0.5rem;background:var(--surface);
       border:1px solid var(--line);border-radius:8px;padding:0.6rem 1rem;">
    {icon('users', 16, FOREST)}
    <div>
      <div style="font-family:var(--font-display);font-size:0.9rem;font-weight:600;color:var(--ink);">Support Every Learner</div>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.divider()

# ---------------------------------------------------------------------------
# Row 1: Project Objective | Dataset | Tech Stack
# ---------------------------------------------------------------------------
col_obj, col_ds, col_tech = st.columns([1.1, 1, 1.3])

with col_obj:
    st.markdown(
        f"""
<div class="spps-ledger-card" style="height:100%;">
  <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.75rem;">
    {icon('target', 18, FOREST)}
    <p style="font-family:var(--font-display);font-size:1.15rem;font-weight:600;color:var(--ink);margin:0;">
      Project Objective
    </p>
  </div>
  <p style="font-size:0.82rem;color:var(--ink-muted);margin:0 0 0.75rem;line-height:1.5;">
    Develop a machine learning application that can:
  </p>
  <ul style="list-style:none;padding:0;margin:0;">
    {''.join(
        f'<li style="display:flex;align-items:flex-start;gap:0.5rem;padding:0.3rem 0;font-size:0.84rem;color:var(--ink-sec);">'
        f'<span style="flex-shrink:0;margin-top:2px;">{icon("check", 14, FOREST)}</span>'
        f'<span>{t}</span></li>'
        for t in [
            "Analyse student academic & behavioural data",
            "Predict performance bands (High / Medium / Low)",
            "Identify key factors affecting performance",
            "Generate personalised insights and recommendations",
            "Visualise analytics through an interactive dashboard",
        ]
    )}
  </ul>
</div>
""",
        unsafe_allow_html=True,
    )

with col_ds:
    st.markdown(
        f"""
<div class="spps-ledger-card" style="height:100%;">
  <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.75rem;">
    {icon('database', 18, BRASS)}
    <div>
      <p style="font-family:var(--font-display);font-size:1.15rem;font-weight:600;color:var(--ink);margin:0;">
        Dataset
      </p>
      <p style="font-family:var(--font-mono);font-size:0.65rem;color:var(--brass);margin:0;text-transform:uppercase;letter-spacing:0.1em;">
        xAPI-Edu-Data
      </p>
    </div>
  </div>
  <p style="font-size:0.82rem;color:var(--ink-muted);margin:0 0 0.75rem;line-height:1.5;">
    Open educational dataset from Kaggle
  </p>
  <ul style="list-style:none;padding:0;margin:0;">
    {''.join(
        f'<li style="display:flex;align-items:flex-start;gap:0.5rem;padding:0.3rem 0;font-size:0.84rem;color:var(--ink-sec);">'
        f'<span style="flex-shrink:0;margin-top:2px;">{icon("check", 14, FOREST)}</span>'
        f'<span>{t}</span></li>'
        for t in [
            "478 student records",
            "Behavioural, engagement, and academic features",
            "Predefined target: High / Medium / Low",
            "Realistic and well-structured educational data",
        ]
    )}
  </ul>
  <a href="https://www.kaggle.com/datasets/aljarah/xAPI-Edu-Data" target="_blank"
     style="display:inline-flex;align-items:center;gap:0.4rem;margin-top:0.9rem;
     font-family:var(--font-body);font-size:0.82rem;color:var(--forest);
     text-decoration:none;border:1px solid var(--line);border-radius:6px;
     padding:0.4rem 0.75rem;transition:all .2s ease;">
    {icon('arrow', 13, FOREST)} View Dataset on Kaggle
  </a>
</div>
""",
        unsafe_allow_html=True,
    )

with col_tech:
    tech_stack = [
        ("Python", "Core language"),
        ("Pandas", "Data wrangling"),
        ("NumPy", "Numerical ops"),
        ("Scikit-learn", "ML models"),
        ("Matplotlib", "Charting"),
        ("Seaborn", "Viz library"),
        ("Streamlit", "Dashboard"),
        ("FastAPI", "REST API"),
        ("SHAP", "Explainability"),
        ("DiCE", "Counterfactuals"),
        ("Fairlearn", "Fairness audit"),
        ("GitHub Actions", "CI/CD"),
    ]
    tech_html = "".join(
        f'<div class="spps-tech-card">'
        f'<div style="font-size:1.4rem;">{e}</div>'
        f'<p class="spps-tech-card-name">{n}</p>'
        f'<p class="spps-tech-card-desc">{d}</p>'
        f'</div>'
        for n, d, e in [
            ("Python", "Core language", "🐍"),
            ("Pandas", "Data wrangling", "🐼"),
            ("NumPy", "Numerical ops", "📐"),
            ("Scikit-learn", "ML models", "🤖"),
            ("Matplotlib", "Charting", "📊"),
            ("Seaborn", "Viz library", "🎨"),
            ("Streamlit", "Dashboard", "⚡"),
            ("FastAPI", "REST API", "🚀"),
            ("SHAP", "Explainability", "🔍"),
            ("DiCE", "Counterfactuals", "🎲"),
            ("Fairlearn", "Fairness audit", "⚖️"),
            ("GitHub Actions", "CI/CD", "🔄"),
        ]
    )
    st.markdown(
        f"""
<div class="spps-ledger-card" style="height:100%;">
  <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.75rem;">
    {icon('code', 18, FOREST)}
    <p style="font-family:var(--font-display);font-size:1.15rem;font-weight:600;color:var(--ink);margin:0;">
      Tech Stack
    </p>
  </div>
  <div class="spps-tech-grid" style="grid-template-columns:repeat(3,1fr);gap:0.5rem;">
    {tech_html}
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

st.divider()

# ---------------------------------------------------------------------------
# Row 2: Project Modules | Timeline | Deliverables
# ---------------------------------------------------------------------------
col_mod, col_tl, col_del = st.columns([1, 1.1, 1])

with col_mod:
    modules = [
        ("#234434", "1", "Data Collection & Preprocessing", "Clean, encode, and prepare the dataset"),
        ("#9A7B2E", "2", "Exploratory Data Analysis", "Discover patterns and key insights"),
        ("#1B2A4A", "3", "Performance Prediction Model", "Train and evaluate classical ML models"),
        ("#234434", "4", "Performance Dashboard", "Interactive and insightful visualisations"),
        ("#9A7B2E", "5", "Recommendation System", "Personalised and actionable improvement suggestions"),
    ]
    mod_items = "".join(
        f'<div style="display:flex;align-items:flex-start;gap:0.75rem;padding:0.6rem 0;'
        f'border-bottom:1px solid var(--line);">'
        f'<span style="flex-shrink:0;width:1.6rem;height:1.6rem;border-radius:50%;'
        f'background:{color};color:#FAF8F3;font-family:var(--font-display);font-size:0.8rem;'
        f'font-weight:700;display:inline-flex;align-items:center;justify-content:center;">{num}</span>'
        f'<div><p style="font-family:var(--font-display);font-size:0.9rem;font-weight:600;'
        f'color:var(--ink);margin:0;">{title}</p>'
        f'<p style="font-size:0.78rem;color:var(--ink-muted);margin:0;">{desc}</p></div>'
        f'</div>'
        for color, num, title, desc in modules
    )
    st.markdown(
        f"""
<div class="spps-ledger-card" style="height:100%;">
  <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.5rem;">
    {icon('grid', 18, FOREST)}
    <p style="font-family:var(--font-display);font-size:1.15rem;font-weight:600;color:var(--ink);margin:0;">
      Project Modules
    </p>
  </div>
  {mod_items}
</div>
""",
        unsafe_allow_html=True,
    )

with col_tl:
    timeline_items = [
        ("Day 1–3",  "Requirement Analysis & Dataset Collection"),
        ("Day 4–7",  "Data Cleaning & Preprocessing"),
        ("Day 8–12", "Exploratory Data Analysis"),
        ("Day 13–17","Machine Learning Model Development"),
        ("Day 18–21","Dashboard Development"),
        ("Day 22–23","Recommendation System"),
        ("Day 24",   "Testing & Bug Fixing"),
        ("Day 25",   "Deployment & Final Presentation"),
    ]
    tl_items = "".join(
        f'<div class="spps-timeline-item">'
        f'<div class="spps-timeline-dot"></div>'
        f'<p class="spps-timeline-date">{date}</p>'
        f'<p class="spps-timeline-desc">{desc}</p>'
        f'</div>'
        for date, desc in timeline_items
    )
    st.markdown(
        f"""
<div class="spps-ledger-card" style="height:100%;">
  <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.75rem;">
    {icon('clock', 18, BRASS)}
    <p style="font-family:var(--font-display);font-size:1.15rem;font-weight:600;color:var(--ink);margin:0;">
      Project Timeline (25 Days)
    </p>
  </div>
  <div class="spps-timeline">
    {tl_items}
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

with col_del:
    deliverables = [
        "Source Code (GitHub Repository)",
        "Project Report (PDF)",
        "PPT Presentation",
        "Dashboard Screenshots",
        "Deployment Link",
        "Demo Video",
    ]
    del_items = "".join(
        f'<li style="display:flex;align-items:center;gap:0.5rem;padding:0.35rem 0;'
        f'font-size:0.875rem;color:var(--ink-sec);">'
        f'{icon("check", 14, FOREST)}<span>{item}</span></li>'
        for item in deliverables
    )
    st.markdown(
        f"""
<div class="spps-ledger-card" style="height:100%;">
  <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.75rem;">
    {icon('ledger', 18, FOREST)}
    <p style="font-family:var(--font-display);font-size:1.15rem;font-weight:600;color:var(--ink);margin:0;">
      Deliverables
    </p>
  </div>
  <ul style="list-style:none;padding:0;margin:0;">
    {del_items}
  </ul>
  <div style="margin-top:1.25rem;background:rgba(35,68,52,.06);border:1px solid rgba(35,68,52,.18);
       border-radius:8px;padding:0.85rem 1rem;">
    <div style="display:flex;align-items:center;gap:0.4rem;margin-bottom:0.3rem;">
      {icon('star', 14, BRASS)}
      <p style="font-family:var(--font-display);font-size:0.9rem;font-weight:600;color:var(--ink);margin:0;">
        Built for Impact
      </p>
    </div>
    <p style="font-size:0.78rem;color:var(--ink-muted);margin:0;line-height:1.5;">
      This project is part of the SkillOrbit Machine Learning Capstone Program.
    </p>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

st.divider()

# ---------------------------------------------------------------------------
# Mission statement
# ---------------------------------------------------------------------------
st.markdown(
    f"""
<div style="background:var(--surface);border:1px solid var(--line);border-top:3px solid var(--brass);
     border-radius:12px;padding:2rem 2.25rem;text-align:center;box-shadow:var(--shadow-card);">
  <p style="font-family:var(--font-display);font-size:0.75rem;font-weight:600;color:var(--brass);
     text-transform:uppercase;letter-spacing:0.14em;margin:0 0 0.75rem;">Our Commitment</p>
  <p style="font-family:var(--font-display);font-size:1.85rem;font-weight:600;color:var(--ink);
     max-width:640px;margin:0 auto 0.75rem;line-height:1.2;">
    "Better insights for brighter futures."
  </p>
  <p style="font-size:0.9rem;color:var(--ink-muted);max-width:520px;margin:0 auto;line-height:1.65;">
    We believe in using data and AI to create more inclusive, supportive, and equitable educational
    environments — where every student has the opportunity to succeed. These predictions are decision
    support, not verdicts. Always combine with teacher judgement and local context.
  </p>
  <div style="display:flex;gap:1.5rem;justify-content:center;margin-top:1.25rem;flex-wrap:wrap;">
    <span style="font-family:var(--font-mono);font-size:0.72rem;color:var(--brass);">Students First · Always</span>
    <span style="font-family:var(--font-mono);font-size:0.72rem;color:var(--ink-muted);">Classical ML Only · No Deep Learning</span>
    <span style="font-family:var(--font-mono);font-size:0.72rem;color:var(--ink-muted);">Ethically Audited · Fairlearn</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    footnote(
        "Student Performance Prediction System · xAPI-Edu-Data · "
        "Python · Scikit-learn · SHAP · DiCE · Fairlearn · Streamlit · FastAPI"
    ),
    unsafe_allow_html=True,
)
