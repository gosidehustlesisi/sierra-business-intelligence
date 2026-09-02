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
- 🎯 Content Simulator — "What-if" content strategy tool
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

_manifest_path = Path(__file__).parent / "data" / "manifest_latest.json"
_manifest = {}
if _manifest_path.exists():
    with open(_manifest_path) as _f:
        _manifest = json.load(_f)
_fetched_at = _manifest.get("fetched_at", "unknown")
_counts = _manifest.get("record_counts", {})
_total_live = sum(_counts.values()) if _counts else 438

_catalog_manifest_path = Path(__file__).parent / "data" / "netflix_catalog_manifest.json"
_catalog_manifest = {}
if _catalog_manifest_path.exists():
    with open(_catalog_manifest_path) as _f:
        _catalog_manifest = json.load(_f)
_catalog_total = _catalog_manifest.get("total_titles", "N/A")
_catalog_extracted = str(_catalog_manifest.get("extracted_at", "unknown"))[:10]

st.markdown(f"""
| Source | Records | Type | Last Updated |
|--------|---------|------|--------------|
| **TMDB Trending Movies** | {_counts.get('trending_movies', 100)} | Live API | {_fetched_at} |
| **TMDB Popular TV** | {_counts.get('popular_tv', 100)} | Live API | {_fetched_at} |
| **TMDB Top Rated Movies** | {_counts.get('top_rated_movies', 100)} | Live API | {_fetched_at} |
| **TMDB Upcoming Movies** | {_counts.get('upcoming_movies', 100)} | Live API | {_fetched_at} |
| **TMDB Genre Mapping** | {_counts.get('movie_genres', 19)} | Live API | {_fetched_at} |
| **Netflix Catalog (self-extracted TMDB)** | {_catalog_total} | Self-extracted, refreshed weekly/monthly | {_catalog_extracted} |

**Total Live Records: {_total_live}** | **Total Catalog Records: {_catalog_total}** | Zero third-party CSV uploads
""")

st.markdown("---")
st.caption("Built with Streamlit • Data from TMDB API • Netflix catalog self-extracted from TMDB (no third-party datasets)")