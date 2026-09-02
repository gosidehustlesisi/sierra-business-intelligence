import os
import json
from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).parent.parent / "data"

TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w185"

@st.cache_data(ttl=300)
def load_all_data():
    """Load all TMDB data with self-healing validation."""
    result = {}
    
    files_to_load = {
        "trending_movies": "trending_movies_latest.csv",
        "popular_tv": "popular_tv_latest.csv",
        "top_rated_movies": "top_rated_movies_latest.csv",
        "upcoming_movies": "upcoming_movies_latest.csv",
        "genres": "movie_genres_latest.csv",
        "genre_popularity": "genre_popularity_latest.csv",
    }
    
    for key, filename in files_to_load.items():
        filepath = DATA_DIR / filename
        if filepath.exists():
            try:
                df = pd.read_csv(filepath)
                result[key] = df
            except Exception as e:
                st.error(f"Failed to load {filename}: {e}")
                result[key] = pd.DataFrame()
        else:
            st.warning(f"Data file not found: {filename}")
            result[key] = pd.DataFrame()
    
    # Load manifest for provenance
    manifest_path = DATA_DIR / "manifest_latest.json"

    manifest = {}
    if manifest_path.exists():
        try:
            with open(manifest_path) as f:
                manifest = json.load(f)
        except Exception:
            pass
    
    return result, manifest

def parse_genres(s):
    """Parse genre_ids from JSON string."""
    try:
        return json.loads(s) if isinstance(s, str) and s.startswith("[") else []
    except (json.JSONDecodeError, ValueError):
        return []

def get_poster_url(poster_path, size="w185"):
    """Build TMDB poster URL from poster_path."""
    if pd.isna(poster_path) or not poster_path:
        return None
    path = str(poster_path).strip()
    if not path.startswith("/"):
        path = "/" + path
    return f"https://image.tmdb.org/t/p/{size}{path}"

def get_tmdb_url(tmdb_id, media_type="movie"):
    """Build TMDB detail page URL."""
    return f"https://www.themoviedb.org/{media_type}/{tmdb_id}"

def format_timestamp(ts_str):
    """Format ISO timestamp to readable string."""
    try:
        dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return ts_str
