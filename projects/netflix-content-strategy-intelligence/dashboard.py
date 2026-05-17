import os
import json
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="TMDB Content Intelligence", layout="wide")

# ── Load data ────────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent / "data"

@st.cache_data
def load_data():
    trending = pd.read_csv(DATA_DIR / "trending_movies_latest.csv")
    tv = pd.read_csv(DATA_DIR / "popular_tv_latest.csv")
    genres = pd.read_csv(DATA_DIR / "movie_genres_latest.csv")
    genre_pop = pd.read_csv(DATA_DIR / "genre_popularity_latest.csv")
    upcoming = pd.read_csv(DATA_DIR / "upcoming_movies_latest.csv")
    return trending, tv, genres, genre_pop, upcoming

def parse_genres(s):
    try:
        return json.loads(s) if isinstance(s, str) else []
    except:
        return []

trending, tv, genres, genre_pop, upcoming = load_data()
trending["genre_ids_list"] = trending["genre_ids"].apply(parse_genres)
tv["genre_ids_list"] = tv["genre_ids"].apply(parse_genres)
id_to_name = dict(zip(genres["genre_id"], genres["genre_name"]))

# ── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.title("🎬 TMDB Content Intelligence")
st.sidebar.markdown("Live entertainment industry data from The Movie Database API.")
view = st.sidebar.radio("Select View", [
    "📊 Executive Summary",
    "🎞️ Content Mix",
    "🌍 Genre Landscape",
    "⭐ Ratings & Quality",
    "📅 Release Timeline",
])

# ── Helper: genre counts ─────────────────────────────────────────────────────
genre_counts = {}
for glist in trending["genre_ids_list"]:
    for gid in glist:
        genre_counts[id_to_name.get(gid, "Unknown")] = genre_counts.get(id_to_name.get(gid, "Unknown"), 0) + 1
genre_df = pd.DataFrame(list(genre_counts.items()), columns=["genre", "count"]).sort_values("count", ascending=False)

# ── View 1: Executive Summary ────────────────────────────────────────────────
if view == "📊 Executive Summary":
    st.header("Executive Summary")
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
    top5 = trending.nlargest(5, "vote_average")[["title", "vote_average", "popularity", "release_date"]]
    st.dataframe(top5, use_container_width=True)

# ── View 2: Content Mix ──────────────────────────────────────────────────────
elif view == "🎞️ Content Mix":
    st.header("Content Mix Deep Dive")

    c1, c2 = st.columns(2)
    with c1:
        fig = px.treemap(genre_pop, path=["genre_name"], values="total_movies_in_genre",
                         color="top_movie_popularity", title="Genre Landscape",
                         color_continuous_scale="Greens")
        st.plotly_chart(fig, use_container_width=True)
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
    fig.add_trace(go.Histogram(x=trending["vote_average"], name="Movies", opacity=0.6, marker_color="steelblue"))
    fig.add_trace(go.Histogram(x=tv["vote_average"], name="TV Shows", opacity=0.6, marker_color="coral"))
    fig.update_layout(barmode="overlay", title="Rating Distribution: Movies vs. TV", xaxis_title="Vote Average")
    st.plotly_chart(fig, use_container_width=True)

# ── View 3: Genre Landscape ──────────────────────────────────────────────────
elif view == "🌍 Genre Landscape":
    st.header("Genre Landscape")

    st.subheader("Genre Popularity Matrix")
    fig = px.scatter(genre_pop, x="total_movies_in_genre", y="top_movie_popularity",
                     size="top_movie_popularity", color="genre_name",
                     title="Genre Volume vs. Peak Popularity", hover_name="genre_name",
                     labels={"total_movies_in_genre": "Titles in Genre", "top_movie_popularity": "Peak Popularity"})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Genre Ratings (Top 15)")
    avg_by_genre = {}
    counts_by_genre = {}
    for _, row in trending.iterrows():
        for gid in row["genre_ids_list"]:
            gname = id_to_name.get(gid, "Unknown")
            avg_by_genre[gname] = avg_by_genre.get(gname, 0) + row["vote_average"]
            counts_by_genre[gname] = counts_by_genre.get(gname, 0) + 1
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
        fig = px.histogram(trending, x="vote_average", nbins=40, title="Movie Rating Distribution",
                           color_discrete_sequence=["coral"])
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.scatter(trending.sample(min(2000, len(trending)), random_state=42),
                         x="popularity", y="vote_average", opacity=0.5, color="vote_average",
                         color_continuous_scale="Viridis", title="Popularity vs. Rating")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Quality Tiers")
    bins = [0, 6, 7, 8, 10]
    labels = ["Below Average", "Average", "Good", "Excellent"]
    tier_counts = pd.cut(trending["vote_average"], bins=bins, labels=labels).value_counts()
    fig = px.pie(names=tier_counts.index, values=tier_counts.values, title="Content Quality Tiers",
                 color_discrete_sequence=["#d62728", "#ff7f0e", "#2ca02c", "#1f77b4"])
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Hidden Gems (Rating ≥ 8, Popularity < Median)")
    median_pop = trending["popularity"].median()
    gems = trending[(trending["vote_average"] >= 8.0) & (trending["popularity"] < median_pop)].nlargest(10, "vote_average")
    st.dataframe(gems[["title", "vote_average", "popularity", "release_date"]], use_container_width=True)

# ── View 5: Release Timeline ─────────────────────────────────────────────────
elif view == "📅 Release Timeline":
    st.header("Release Timeline")

    trending["release_year"] = pd.to_datetime(trending["release_date"], errors="coerce").dt.year
    year_counts = trending["release_year"].value_counts().sort_index().loc[2000:2021]

    fig = px.line(x=year_counts.index, y=year_counts.values, markers=True,
                  title="Movie Release Year Trend (2000–2021)", labels={"x": "Year", "y": "Count"})
    st.plotly_chart(fig, use_container_width=True)

    upcoming["release_month"] = pd.to_datetime(upcoming["release_date"], errors="coerce").dt.month
    month_counts = upcoming["release_month"].value_counts().sort_index()
    fig = px.bar(x=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
                 y=[month_counts.get(i, 0) for i in range(1, 13)],
                 title="Upcoming Releases by Month", labels={"x": "Month", "y": "Count"},
                 color_discrete_sequence=["teal"])
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Upcoming Releases")
    st.dataframe(upcoming[["title", "release_date", "vote_average", "popularity"]].sort_values("release_date"), use_container_width=True)

# ── Footer ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.markdown("**Data Source:** TMDB API (live)  
**Fallback:** Netflix Kaggle Dataset (CC0)  
**Fetched:** see `data/manifest_latest.json`")
