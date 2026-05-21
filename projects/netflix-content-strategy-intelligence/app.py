import os
import json
from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Netflix Content Strategy Intelligence",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-header { font-size: 2.5rem; font-weight: 700; color: #E50914; }
    .sub-header { font-size: 1.1rem; color: #666; margin-bottom: 2rem; }
    .metric-card { background: #f8f9fa; border-radius: 10px; padding: 1.2rem; text-align: center; }
    .metric-value { font-size: 2rem; font-weight: 700; color: #E50914; }
    .metric-label { font-size: 0.9rem; color: #666; }
    .live-badge { background: #E50914; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
    .data-badge { background: #1f77b4; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🎬 Netflix Content Strategy Intelligence</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Live entertainment data from TMDB API — refreshed in real-time</p>', unsafe_allow_html=True)

st.info("""
👈 **Use the sidebar to navigate between dashboard views:**
- 📊 Executive Summary — Key metrics and content mix
- 🔍 Live Data Explorer — Sortable table with real movie posters
- 🎭 Genre Analysis — Deep genre breakdown and ratings
- 🌍 Geographic Insights — Content by origin country
- ⭐ Ratings & Quality — Quality tiers and hidden gems
- 📅 Release Timeline — Upcoming releases and trends
""")

st.markdown("---")

st.subheader("What Makes This Dashboard Different")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    **🔴 Live Data Pipeline**
    
    Every chart uses real data fetched from the TMDB API — not a static CSV from 2019. 
    The "Last Refreshed" badge shows exactly when the data was pulled.
    """)
with col2:
    st.markdown("""
    **🎬 Real Movie Posters**
    
    Movie and TV show cards display actual poster images from TMDB's CDN. 
    Click any title to see its verified TMDB page.
    """)
with col3:
    st.markdown("""
    **📈 Strategy-Ready Insights**
    
    Not just pretty charts — actionable intelligence for content acquisition, 
    genre positioning, and release window optimization.
    """)

st.markdown("---")

st.subheader("Data Sources")
st.markdown("""
| Source | Records | Type | Last Updated |
|--------|---------|------|--------------|
| **TMDB Trending Movies** | 100 | Live API | 2026-05-21 22:17 UTC |
| **TMDB Popular TV** | 100 | Live API | 2026-05-21 22:17 UTC |
| **TMDB Top Rated Movies** | 100 | Live API | 2026-05-21 22:17 UTC |
| **TMDB Upcoming Movies** | 100 | Live API | 2026-05-21 22:17 UTC |
| **TMDB Genre Mapping** | 19 | Live API | 2026-05-21 22:17 UTC |
| **Netflix Catalog (Kaggle)** | 8,807 | Static Reference | 2021 (CC0) |

**Total Live Records: 438** | **Total Reference Records: 8,807** | **Combined: 9,245**
""")

st.markdown("---")
st.caption("Built with Streamlit • Data from TMDB API • Netflix Kaggle Dataset (CC0)")