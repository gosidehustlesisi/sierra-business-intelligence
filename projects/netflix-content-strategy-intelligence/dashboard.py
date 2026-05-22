import os
import json
import time
from pathlib import Path
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests

# ── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Netflix Content Intelligence", layout="wide")

# ── Auto-Refresh ──────────────────────────────────────────────────────────────
REFRESH_INTERVAL_MINUTES = 30
st_autorefresh = st.empty()

# ── Load Data ─────────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent / "data"
MANIFEST_PATH = DATA_DIR / "manifest_latest.json"

@st.cache_data(ttl=300)
def load_data():
    files = {
        "trending": DATA_DIR / "trending_movies_latest.csv",
        "tv": DATA_DIR / "popular_tv_latest.csv",
        "genres": DATA_DIR / "movie_genres_latest.csv",
        "genre_pop": DATA_DIR / "genre_popularity_latest.csv",
        "upcoming": DATA_DIR / "upcoming_movies_latest.csv",
    }
    data = {}
    for key, path in files.items():
        if path.exists():
            data[key] = pd.read_csv(path)
        else:
            data[key] = pd.DataFrame()
    return data

def load_manifest():
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH) as f:
            return json.load(f)
    return {}

def parse_genres(s):
    try:
        return json.loads(s) if isinstance(s, str) else []
    except:
        return []

data = load_data()
manifest = load_manifest()
trending = data.get("trending", pd.DataFrame())
tv = data.get("tv", pd.DataFrame())
genres = data.get("genres", pd.DataFrame())
genre_pop = data.get("genre_pop", pd.DataFrame())
upcoming = data.get("upcoming", pd.DataFrame())

# Parse genre IDs
trending["genre_ids_list"] = trending["genre_ids"].apply(parse_genres) if "genre_ids" in trending.columns else trending.apply(lambda x: [], axis=1)
tv["genre_ids_list"] = tv["genre_ids"].apply(parse_genres) if "genre_ids" in tv.columns else tv.apply(lambda x: [], axis=1)
id_to_name = dict(zip(genres["genre_id"], genres["genre_name"])) if len(genres) > 0 else {}

# Data freshness
fetched_at = manifest.get("fetched_at", "Unknown")
data_age_hours = None
if fetched_at != "Unknown":
    try:
        fetch_time = datetime.fromisoformat(fetched_at.replace("Z", "+00:00"))
        data_age_hours = (datetime.now().astimezone() - fetch_time).total_seconds() / 3600
    except:
        pass

# ── TMDB API Check ──────────────────────────────────────────────────────────
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "")
TMDB_READ_TOKEN = os.environ.get("TMDB_READ_TOKEN", "")
api_key_valid = False
api_status_message = "No API key configured"

if TMDB_API_KEY:
    try:
        test_resp = requests.get(
            "https://api.themoviedb.org/3/movie/550",
            params={"api_key": TMDB_API_KEY},
            timeout=5
        )
        if test_resp.status_code == 200:
            api_key_valid = True
            api_status_message = "✅ API key valid"
        elif test_resp.status_code == 401:
            api_status_message = "❌ API key invalid (401)"
        else:
            api_status_message = f"⚠️ API status {test_resp.status_code}"
    except Exception as e:
        api_status_message = f"⚠️ API unreachable ({str(e)[:50]})"

# ── Trailer Fetch Function ──────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_trailers(movie_id, api_key):
    """Fetch YouTube trailer keys from TMDB for a given movie ID."""
    if not api_key or not api_key_valid:
        return []
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos"
        resp = requests.get(url, params={"api_key": api_key}, timeout=10)
        if resp.status_code == 200:
            videos = resp.json().get("results", [])
            trailers = [v for v in videos if v.get("type") == "Trailer" and v.get("site") == "YouTube"]
            return trailers[:3]  # Return top 3 trailers
    except Exception as e:
        st.error(f"Trailer fetch error: {e}")
    return []

def get_youtube_embed_url(key):
    return f"https://www.youtube.com/embed/{key}"

# ── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.title("🎬 Netflix Content Intelligence")

# Data status indicator
if data_age_hours is not None:
    freshness_color = "🟢" if data_age_hours < 24 else "🟡" if data_age_hours < 72 else "🔴"
    st.sidebar.markdown(f"{freshness_color} **Data age:** {data_age_hours:.1f}h")
else:
    st.sidebar.markdown("⚪ **Data age:** Unknown")

st.sidebar.markdown(f"**API Status:** {api_status_message}")
st.sidebar.markdown("---")

view = st.sidebar.radio("Select View", [
    "📊 Executive Summary",
    "🎞️ Content Mix",
    "🌍 Genre Landscape",
    "⭐ Ratings & Quality",
    "📅 Release Timeline",
    "🎬 Trailers",
    "⚙️ Settings",
])

# Auto-refresh control
st.sidebar.markdown("---")
st.sidebar.subheader("Auto-Refresh")
auto_refresh = st.sidebar.toggle("Enable auto-refresh", value=False)
if auto_refresh:
    refresh_interval = st.sidebar.slider("Interval (minutes)", 5, 120, 30)
    st_autorefresh.info(f"⏱️ Auto-refresh every {refresh_interval} min (manual refresh needed for now)")
    # Note: True auto-refresh requires st.rerun() in a loop or JavaScript injection
    # Streamlit Cloud handles this via page reload

# ── Helper: genre counts ─────────────────────────────────────────────────────
genre_counts = {}
for glist in trending["genre_ids_list"]:
    for gid in glist:
        genre_counts[id_to_name.get(gid, "Unknown")] = genre_counts.get(id_to_name.get(gid, "Unknown"), 0) + 1
genre_df = pd.DataFrame(list(genre_counts.items()), columns=["genre", "count"]).sort_values("count", ascending=False)

# ── View 1: Executive Summary ────────────────────────────────────────────────
if view == "📊 Executive Summary":
    st.header("Executive Summary")
    
    # Honest data source banner
    source_type = "🔴 Static Kaggle Dataset" if not api_key_valid else "🟢 Live TMDB API"
    st.info(f"{source_type} — Last refresh: {fetched_at}")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Movies", f"{len(trending):,}")
    col2.metric("Total TV Shows", f"{len(tv):,}")
    col3.metric("Genres", f"{len(genres):,}")
    col4.metric("Upcoming Releases", f"{len(upcoming):,}")

    c1, c2 = st.columns(2)
    with c1:
        fig = px.pie(names=["Movies", "TV Shows"], values=[len(trending), len(tv)],
                     title="Content Mix", color_discrete_sequence=["steelblue", "coral"])
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.bar(genre_df.head(10), x="count", y="genre", orientation="h",
                     title="Top 10 Genres", color="count", color_continuous_scale="Blues")
        fig.update_layout(yaxis_categoryorder="total ascending", height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top 5 Highest-Rated Movies")
    if "vote_average" in trending.columns:
        top5 = trending.nlargest(5, "vote_average")[["title", "vote_average", "popularity", "release_date"]]
        st.dataframe(top5, use_container_width=True)
    else:
        st.warning("Rating data not available")

# ── View 2: Content Mix ──────────────────────────────────────────────────────
elif view == "🎞️ Content Mix":
    st.header("Content Mix Deep Dive")

    c1, c2 = st.columns(2)
    with c1:
        if len(genre_pop) > 0 and "total_movies_in_genre" in genre_pop.columns:
            fig = px.treemap(genre_pop, path=["genre_name"], values="total_movies_in_genre",
                             color="top_movie_popularity", title="Genre Landscape",
                             color_continuous_scale="Greens")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Genre popularity data not available")
    with c2:
        tv_genre_counts = {}
        for glist in tv["genre_ids_list"]:
            for gid in glist:
                tv_genre_counts[id_to_name.get(gid, "Unknown")] = tv_genre_counts.get(id_to_name.get(gid, "Unknown"), 0) + 1
        tv_genre_df = pd.DataFrame(list(tv_genre_counts.items()), columns=["genre", "count"]).sort_values("count", ascending=False)
        fig = px.bar(tv_genre_df.head(10), x="count", y="genre", orientation="h",
                     title="Top 10 TV Genres", color="count", color_continuous_scale="Oranges")
        fig.update_layout(yaxis_categoryorder="total ascending", height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Movies vs. TV by Vote Average")
    fig = go.Figure()
    if "vote_average" in trending.columns:
        fig.add_trace(go.Histogram(x=trending["vote_average"], name="Movies", opacity=0.6, marker_color="steelblue"))
    if "vote_average" in tv.columns:
        fig.add_trace(go.Histogram(x=tv["vote_average"], name="TV Shows", opacity=0.6, marker_color="coral"))
    fig.update_layout(barmode="overlay", title="Rating Distribution: Movies vs. TV", xaxis_title="Vote Average")
    st.plotly_chart(fig, use_container_width=True)

# ── View 3: Genre Landscape ────────────────────────────────────────────────────
elif view == "🌍 Genre Landscape":
    st.header("Genre Landscape")

    st.subheader("Genre Popularity Matrix")
    if len(genre_pop) > 0 and "total_movies_in_genre" in genre_pop.columns:
        fig = px.scatter(genre_pop, x="total_movies_in_genre", y="top_movie_popularity",
                         size="top_movie_popularity", color="genre_name",
                         title="Genre Volume vs. Peak Popularity", hover_name="genre_name",
                         labels={"total_movies_in_genre": "Titles in Genre", "top_movie_popularity": "Peak Popularity"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Genre popularity data not available")

    st.subheader("Genre Ratings (Top 15)")
    avg_by_genre = {}
    counts_by_genre = {}
    for _, row in trending.iterrows():
        for gid in row["genre_ids_list"]:
            gname = id_to_name.get(gid, "Unknown")
            if "vote_average" in row:
                avg_by_genre[gname] = avg_by_genre.get(gname, 0) + row["vote_average"]
                counts_by_genre[gname] = counts_by_genre.get(gname, 0) + 1
    if avg_by_genre:
        avg_df = pd.DataFrame([
            {"genre": g, "avg_rating": avg_by_genre[g] / counts_by_genre[g], "count": counts_by_genre[g]}
            for g in avg_by_genre if counts_by_genre[g] >= 20
        ]).sort_values("avg_rating", ascending=False).head(15)
        fig = px.bar(avg_df, x="avg_rating", y="genre", orientation="h", color="count",
                     title="Avg Rating by Genre (min 20 titles)", color_continuous_scale="RdYlGn")
        fig.update_layout(yaxis_categoryorder="total ascending")
        st.plotly_chart(fig, use_container_width=True)

# ── View 4: Ratings & Quality ────────────────────────────────────────────────
elif view == "⭐ Ratings & Quality":
    st.header("Ratings & Quality Analysis")

    c1, c2 = st.columns(2)
    with c1:
        if "vote_average" in trending.columns:
            fig = px.histogram(trending, x="vote_average", nbins=40, title="Movie Rating Distribution",
                               color_discrete_sequence=["coral"])
            st.plotly_chart(fig, use_container_width=True)
    with c2:
        if "vote_average" in trending.columns and "popularity" in trending.columns:
            fig = px.scatter(trending.sample(min(2000, len(trending)), random_state=42),
                             x="popularity", y="vote_average", opacity=0.5, color="vote_average",
                             color_continuous_scale="Viridis", title="Popularity vs. Rating")
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Quality Tiers")
    if "vote_average" in trending.columns:
        bins = [0, 6, 7, 8, 10]
        labels = ["Below Average", "Average", "Good", "Excellent"]
        tier_counts = pd.cut(trending["vote_average"], bins=bins, labels=labels).value_counts()
        fig = px.pie(names=tier_counts.index, values=tier_counts.values, title="Content Quality Tiers",
                     color_discrete_sequence=["#d62728", "#ff7f0e", "#2ca02c", "#1f77b4"])
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Hidden Gems (Rating ≥ 8, Popularity < Median)")
    if "vote_average" in trending.columns and "popularity" in trending.columns:
        median_pop = trending["popularity"].median()
        gems = trending[(trending["vote_average"] >= 8.0) & (trending["popularity"] < median_pop)].nlargest(10, "vote_average")
        st.dataframe(gems[["title", "vote_average", "popularity", "release_date"]], use_container_width=True)

# ── View 5: Release Timeline ─────────────────────────────────────────────────
elif view == "📅 Release Timeline":
    st.header("Release Timeline")

    if "release_date" in trending.columns:
        trending["release_year"] = pd.to_datetime(trending["release_date"], errors="coerce").dt.year
        year_counts = trending["release_year"].value_counts().sort_index().loc[2000:2021]

        fig = px.line(x=year_counts.index, y=year_counts.values, markers=True,
                      title="Movie Release Year Trend (2000–2021)", labels={"x": "Year", "y": "Count"})
        st.plotly_chart(fig, use_container_width=True)

    if "release_date" in upcoming.columns:
        upcoming["release_month"] = pd.to_datetime(upcoming["release_date"], errors="coerce").dt.month
        month_counts = upcoming["release_month"].value_counts().sort_index()
        fig = px.bar(x=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
                     y=[month_counts.get(i, 0) for i in range(1, 13)],
                     title="Upcoming Releases by Month", labels={"x": "Month", "y": "Count"},
                     color_discrete_sequence=["teal"])
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Upcoming Releases")
        st.dataframe(upcoming[["title", "release_date", "vote_average", "popularity"]].sort_values("release_date"), use_container_width=True)

# ── View 6: Trailers ──────────────────────────────────────────────────────────
elif view == "🎬 Trailers":
    st.header("🎬 Movie Trailers")
    
    if not api_key_valid:
        st.warning("⚠️ TMDB API key is not valid. Trailers cannot be fetched from TMDB.")
        st.info("To enable trailers: set TMDB_API_KEY environment variable with a valid API key.")
        
        # Show fallback: top movies with YouTube search links
        st.subheader("Top Movies (YouTube Search Links)")
        if "title" in trending.columns:
            top_movies = trending.nlargest(10, "popularity")[["title", "vote_average", "popularity", "release_date"]]
            for _, row in top_movies.iterrows():
                with st.expander(f"🎬 {row['title']} ({row.get('release_date', 'N/A')}) — ⭐{row['vote_average']:.1f}"):
                    search_query = f"{row['title']} trailer"
                    youtube_url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
                    st.markdown(f"[🔍 Search YouTube for '{search_query}']({youtube_url})")
                    st.markdown("*Trailer embed requires valid TMDB API key*")
    else:
        st.success("✅ TMDB API key valid — fetching trailers...")
        
        # Fetch trailers for top movies
        st.subheader("Latest Trailers")
        if "id" in trending.columns and "title" in trending.columns:
            top_movies = trending.nlargest(5, "popularity")
            
            for _, row in top_movies.iterrows():
                movie_id = row["id"]
                trailers = fetch_trailers(movie_id, TMDB_API_KEY)
                
                with st.expander(f"🎬 {row['title']} — ⭐{row.get('vote_average', 'N/A')}"):
                    if trailers:
                        for trailer in trailers:
                            trailer_key = trailer.get("key", "")
                            trailer_name = trailer.get("name", "Trailer")
                            if trailer_key:
                                embed_url = get_youtube_embed_url(trailer_key)
                                st.markdown(f"**{trailer_name}**")
                                st.markdown(f'<iframe width="100%" height="315" src="{embed_url}" frameborder="0" allowfullscreen></iframe>', unsafe_allow_html=True)
                    else:
                        st.info("No trailers available for this title")
                        # Fallback to YouTube search
                        search_query = f"{row['title']} trailer"
                        youtube_url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
                        st.markdown(f"[🔍 Search on YouTube]({youtube_url})")
        else:
            st.info("Movie IDs not available in dataset — cannot fetch trailers")

    # Manual trailer search
    st.markdown("---")
    st.subheader("Search Any Movie Trailer")
    search_title = st.text_input("Enter movie title:", "")
    if search_title:
        youtube_search = f"https://www.youtube.com/results?search_query={search_title.replace(' ', '+')}+trailer"
        st.markdown(f"[🔍 Search YouTube for '{search_title} trailer']({youtube_search})")

# ── View 7: Settings ──────────────────────────────────────────────────────────
elif view == "⚙️ Settings":
    st.header("⚙️ Dashboard Settings")
    
    st.subheader("Data Source")
    st.json(manifest)
    
    st.subheader("API Configuration")
    st.markdown(f"- **TMDB_API_KEY:** {'✅ Set' if TMDB_API_KEY else '❌ Not set'}")
    st.markdown(f"- **TMDB_READ_TOKEN:** {'✅ Set' if TMDB_READ_TOKEN else '❌ Not set'}")
    st.markdown(f"- **API Status:** {api_status_message}")
    
    if TMDB_API_KEY and not api_key_valid:
        st.error("API key is set but invalid. Get a new key at https://www.themoviedb.org/settings/api")
    
    st.subheader("Data Files")
    for fname in ["trending_movies_latest.csv", "popular_tv_latest.csv", "movie_genres_latest.csv", 
                  "genre_popularity_latest.csv", "upcoming_movies_latest.csv"]:
        fpath = DATA_DIR / fname
        if fpath.exists():
            size_kb = fpath.stat().st_size / 1024
            st.markdown(f"✅ {fname} ({size_kb:.1f} KB)")
        else:
            st.markdown(f"❌ {fname} — NOT FOUND")
    
    st.subheader("Manual Refresh")
    if st.button("🔄 Clear Cache & Reload"):
        st.cache_data.clear()
        st.rerun()

# ── Footer ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("---")
source_badge = "🟢 Live TMDB" if api_key_valid else "🔴 Static Kaggle (CC0)"
st.sidebar.markdown(f"**Source:** {source_badge}")
st.sidebar.markdown(f"**Last Fetch:** {fetched_at}")
if data_age_hours is not None:
    st.sidebar.markdown(f"**Data Age:** {data_age_hours:.1f} hours")
st.sidebar.markdown("---")
st.sidebar.markdown("Built by [Sierra Napier](https://github.com/gosidehustlesisi)")
