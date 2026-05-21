import json
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils import load_all_data, parse_genres, get_poster_url, get_tmdb_url, format_timestamp

st.set_page_config(page_title="Executive Summary", page_icon="📊", layout="wide")

data, manifest = load_all_data()

st.markdown("""
<style>
.metric-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; padding: 1.5rem; text-align: center; color: white; }
.metric-value { font-size: 2.5rem; font-weight: 800; }
.metric-label { font-size: 0.9rem; opacity: 0.9; }
.live-pulse { animation: pulse 2s infinite; }
@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
</style>
""", unsafe_allow_html=True)

st.title("📊 Executive Summary")

# Data freshness badge
fetched_at = manifest.get("fetched_at", "Unknown")
if fetched_at != "Unknown":
    st.markdown(f'<span style="background:#E50914;color:white;padding:6px 14px;border-radius:20px;font-size:0.8rem;font-weight:600;">🔴 LIVE DATA — Refreshed {format_timestamp(fetched_at)}</span>', unsafe_allow_html=True)
else:
    st.markdown('<span style="background:#666;color:white;padding:6px 14px;border-radius:20px;font-size:0.8rem;font-weight:600;">⚪ Static Data</span>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Key metrics
trending = data.get("trending_movies", pd.DataFrame())
tv = data.get("popular_tv", pd.DataFrame())
genres = data.get("genres", pd.DataFrame())
upcoming = data.get("upcoming_movies", pd.DataFrame())
top_rated = data.get("top_rated_movies", pd.DataFrame())

live_total = len(trending) + len(tv) + len(top_rated) + len(upcoming)

m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{len(trending)}</div><div class="metric-label">Trending Movies</div></div>', unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{len(tv)}</div><div class="metric-label">Popular TV Shows</div></div>', unsafe_allow_html=True)
with m3:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{len(top_rated)}</div><div class="metric-label">Top Rated</div></div>', unsafe_allow_html=True)
with m4:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{len(upcoming)}</div><div class="metric-label">Upcoming</div></div>', unsafe_allow_html=True)
with m5:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{len(genres)}</div><div class="metric-label">Genres Mapped</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Content mix
col1, col2 = st.columns(2)

with col1:
    st.subheader("Content Type Distribution")
    content_mix = pd.DataFrame({
        "Type": ["Trending Movies", "Popular TV", "Top Rated Movies", "Upcoming Movies"],
        "Count": [len(trending), len(tv), len(top_rated), len(upcoming)]
    })
    fig = px.pie(content_mix, names="Type", values="Count", 
                 color_discrete_sequence=["#E50914", "#564d4d", "#221f1f", "#b20710"],
                 hole=0.4)
    fig.update_traces(textinfo="percent+label", textposition="outside")
    fig.update_layout(showlegend=True, height=400)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Top 10 Genres by Volume")
    all_content = pd.concat([
        trending.assign(content_type="Trending Movie"),
        tv.assign(content_type="Popular TV"),
        top_rated.assign(content_type="Top Rated Movie"),
        upcoming.assign(content_type="Upcoming Movie")
    ], ignore_index=True)
    
    all_content["genre_ids_list"] = all_content["genre_ids"].apply(parse_genres)
    id_to_name = dict(zip(genres["genre_id"], genres["genre_name"])) if not genres.empty else {}
    
    genre_counts = {}
    for glist in all_content["genre_ids_list"]:
        for gid in glist:
            name = id_to_name.get(gid, f"Genre {gid}")
            genre_counts[name] = genre_counts.get(name, 0) + 1
    
    genre_df = pd.DataFrame(list(genre_counts.items()), columns=["Genre", "Count"]).sort_values("Count", ascending=False).head(10)
    
    fig = px.bar(genre_df, x="Count", y="Genre", orientation="h",
                 color="Count", color_continuous_scale="Reds")
    fig.update_layout(yaxis_categoryorder="total ascending", height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# Top rated titles
st.subheader("🏆 Highest Rated Content (Vote Average ≥ 8.5)")
rated_content = []

for df, label, id_col in [(trending, "Trending", "tmdb_id"), (tv, "TV", "tmdb_id"), (top_rated, "Top Rated", "tmdb_id")]:
    if not df.empty and "vote_average" in df.columns:
        high_rated = df[df["vote_average"] >= 8.5].copy()
        if not high_rated.empty:
            high_rated["source"] = label
            rated_content.append(high_rated)

if rated_content:
    top_all = pd.concat(rated_content, ignore_index=True).nlargest(10, "vote_average")
    
    cols = st.columns(5)
    for idx, (_, row) in enumerate(top_all.iterrows()):
        with cols[idx % 5]:
            poster = get_poster_url(row.get("poster_path"), "w185")
            title = row.get("title") or row.get("name", "Unknown")
            rating = row.get("vote_average", 0)
            tmdb_id = row.get("tmdb_id", "")
            
            if poster:
                st.image(poster, width=120)
            else:
                st.markdown(f"<div style='width:120px;height:180px;background:#333;display:flex;align-items:center;justify-content:center;color:#999;font-size:0.7rem;'>No Poster</div>", unsafe_allow_html=True)
            
            st.markdown(f"**{title[:25]}{'...' if len(title) > 25 else ''}**")
            st.markdown(f"⭐ {rating:.2f} | {row.get('source', '')}")
            if tmdb_id:
                st.markdown(f"<a href='{get_tmdb_url(tmdb_id)}' target='_blank' style='font-size:0.75rem;'>View on TMDB →</a>", unsafe_allow_html=True)
else:
    st.info("No content with rating ≥ 8.5 in current dataset.")

# Quality overview
st.subheader("Quality Distribution")
qcol1, qcol2 = st.columns(2)

with qcol1:
    all_rated = pd.concat([trending, top_rated], ignore_index=True) if not trending.empty and not top_rated.empty else trending if not trending.empty else pd.DataFrame()
    if not all_rated.empty and "vote_average" in all_rated.columns:
        fig = px.histogram(all_rated, x="vote_average", nbins=30,
                           color_discrete_sequence=["#E50914"],
                           labels={"vote_average": "Vote Average", "count": "Number of Titles"})
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

with qcol2:
    if not all_rated.empty and "vote_average" in all_rated.columns:
        bins = [0, 6, 7, 8, 10]
        labels = ["Below 6 ⭐", "6–7 ⭐", "7–8 ⭐", "8+ ⭐"]
        tier_counts = pd.cut(all_rated["vote_average"], bins=bins, labels=labels).value_counts().sort_index()
        fig = px.bar(x=tier_counts.index, y=tier_counts.values,
                     color=tier_counts.values, color_continuous_scale="RdYlGn",
                     labels={"x": "Quality Tier", "y": "Count"})
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

st.caption(f"Data provenance: TMDB API live fetch | {live_total} records | Last updated: {format_timestamp(fetched_at)}")
