import pandas as pd
import streamlit as st
import plotly.express as px
from utils import load_all_data, parse_genres, get_poster_url, get_tmdb_url, format_timestamp

st.set_page_config(page_title="Ratings & Quality", page_icon="⭐", layout="wide")

data, manifest = load_all_data()

st.title("⭐ Ratings & Quality Analysis")

fetched_at = manifest.get("fetched_at", "Unknown")
st.markdown(f'<span style="background:#E50914;color:white;padding:6px 14px;border-radius:20px;font-size:0.8rem;font-weight:600;">🔴 LIVE — Refreshed {format_timestamp(fetched_at)}</span>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

trending = data.get("trending_movies", pd.DataFrame())
tv = data.get("popular_tv", pd.DataFrame())
top_rated = data.get("top_rated_movies", pd.DataFrame())
upcoming = data.get("upcoming_movies", pd.DataFrame())

# Combine movies and TV
all_content = pd.concat([
    trending.assign(content_type="Trending Movie"),
    tv.assign(content_type="Popular TV"),
    top_rated.assign(content_type="Top Rated Movie"),
    upcoming.assign(content_type="Upcoming Movie")
], ignore_index=True)

# Rating distribution
st.subheader("Rating Distribution by Content Type")

fig = px.histogram(all_content, x="vote_average", color="content_type",
                   nbins=30, barmode="overlay",
                   opacity=0.7,
                   color_discrete_sequence=["#E50914", "#564d4d", "#221f1f", "#b20710"],
                   labels={"vote_average": "Vote Average", "count": "Number of Titles"})
fig.update_layout(height=400)
st.plotly_chart(fig, use_container_width=True)

# Quality tiers
st.subheader("Quality Tiers")

tier_defs = [
    ("🔴 Below Average", 0, 6.0, "#d62728"),
    ("🟡 Average", 6.0, 7.0, "#ff7f0e"),
    ("🟢 Good", 7.0, 8.0, "#2ca02c"),
    ("🔵 Excellent", 8.0, 10.0, "#1f77b4")
]

tier_data = []
for label, min_r, max_r, color in tier_defs:
    count = len(all_content[(all_content["vote_average"] >= min_r) & (all_content["vote_average"] < max_r)])
    pct = count / len(all_content) * 100 if len(all_content) > 0 else 0
    avg_pop = all_content[(all_content["vote_average"] >= min_r) & (all_content["vote_average"] < max_r)]["popularity"].mean() if count > 0 else 0
    tier_data.append({"Tier": label, "Count": count, "Percent": pct, "Avg Popularity": avg_pop, "Color": color})

tier_df = pd.DataFrame(tier_data)

col1, col2 = st.columns(2)

with col1:
    fig = px.pie(tier_df, names="Tier", values="Count", color="Tier",
                 color_discrete_map={row["Tier"]: row["Color"] for _, row in tier_df.iterrows()})
    fig.update_traces(textinfo="percent+label")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.bar(tier_df, x="Tier", y="Count", color="Tier",
                 color_discrete_map={row["Tier"]: row["Color"] for _, row in tier_df.iterrows()},
                 labels={"Count": "Number of Titles"})
    fig.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# Hidden gems
st.subheader("💎 Hidden Gems (Rating ≥ 8.0, Below-Median Popularity)")

median_pop = all_content["popularity"].median()
gems = all_content[(all_content["vote_average"] >= 8.0) & (all_content["popularity"] < median_pop)].sort_values("vote_average", ascending=False)

if not gems.empty:
    st.write(f"Found **{len(gems)}** hidden gems (median popularity: {median_pop:.1f})")
    
    cols = st.columns(4)
    for idx, (_, row) in enumerate(gems.head(8).iterrows()):
        with cols[idx % 4]:
            poster = get_poster_url(row.get("poster_path"), "w185")
            title = row.get("title") or row.get("name", "Unknown")
            rating = row.get("vote_average", 0)
            pop = row.get("popularity", 0)
            tmdb_id = row.get("tmdb_id", "")
            
            if poster:
                st.image(poster, width=150)
            else:
                st.markdown(f"<div style='width:150px;height:225px;background:#1a1a1a;display:flex;align-items:center;justify-content:center;border-radius:8px;'><span style='color:#666;font-size:0.7rem;'>No Poster</span></div>", unsafe_allow_html=True)
            
            st.markdown(f"**{title[:25]}{'...' if len(title) > 25 else ''}**")
            st.markdown(f"⭐ {rating:.2f} | 📈 {pop:.1f}")
            if tmdb_id:
                st.markdown(f"<a href='{get_tmdb_url(tmdb_id)}' target='_blank' style='font-size:0.7rem;'>TMDB →</a>", unsafe_allow_html=True)
            st.markdown("---")
else:
    st.info("No hidden gems found in current dataset (rating ≥ 8.0 with below-median popularity).")

# Rating vs Popularity
st.subheader("Rating vs. Popularity Scatter")

fig = px.scatter(all_content, x="popularity", y="vote_average",
                 color="content_type", hover_name="title" if "title" in all_content.columns else "name",
                 opacity=0.7, size="vote_count" if "vote_count" in all_content.columns else None,
                 labels={"popularity": "Popularity Score", "vote_average": "Vote Average"})
fig.update_layout(height=500)
st.plotly_chart(fig, use_container_width=True)

st.caption(f"Data: TMDB API | {len(all_content)} titles analyzed | Last refresh: {format_timestamp(fetched_at)}")
