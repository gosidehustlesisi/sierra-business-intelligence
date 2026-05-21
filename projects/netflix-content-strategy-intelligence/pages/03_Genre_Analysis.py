import pandas as pd
import streamlit as st
import plotly.express as px
from utils import load_all_data, parse_genres, get_poster_url, format_timestamp

st.set_page_config(page_title="Genre Analysis", page_icon="🎭", layout="wide")

data, manifest = load_all_data()

st.title("🎭 Genre Analysis")

fetched_at = manifest.get("fetched_at", "Unknown")
st.markdown(f'<span style="background:#E50914;color:white;padding:6px 14px;border-radius:20px;font-size:0.8rem;font-weight:600;">🔴 LIVE — Refreshed {format_timestamp(fetched_at)}</span>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

trending = data.get("trending_movies", pd.DataFrame())
tv = data.get("popular_tv", pd.DataFrame())
top_rated = data.get("top_rated_movies", pd.DataFrame())
upcoming = data.get("upcoming_movies", pd.DataFrame())
genres = data.get("genres", pd.DataFrame())
genre_pop = data.get("genre_popularity", pd.DataFrame())

id_to_name = dict(zip(genres["genre_id"], genres["genre_name"])) if not genres.empty else {}

# Combine for analysis
all_content = pd.concat([
    trending.assign(content_type="Trending Movie"),
    tv.assign(content_type="Popular TV"),
    top_rated.assign(content_type="Top Rated Movie"),
    upcoming.assign(content_type="Upcoming Movie")
], ignore_index=True)

all_content["genre_ids_list"] = all_content["genre_ids"].apply(parse_genres)

# Build genre stats
genre_stats = {}
for _, row in all_content.iterrows():
    for gid in row["genre_ids_list"]:
        name = id_to_name.get(gid, f"Genre {gid}")
        if name not in genre_stats:
            genre_stats[name] = {"count": 0, "total_rating": 0, "total_pop": 0, "types": set()}
        genre_stats[name]["count"] += 1
        genre_stats[name]["total_rating"] += row.get("vote_average", 0)
        genre_stats[name]["total_pop"] += row.get("popularity", 0)
        genre_stats[name]["types"].add(row.get("content_type", "Unknown"))

genre_df = pd.DataFrame([
    {
        "Genre": g,
        "Count": s["count"],
        "Avg Rating": s["total_rating"] / s["count"] if s["count"] > 0 else 0,
        "Avg Popularity": s["total_pop"] / s["count"] if s["count"] > 0 else 0,
        "Content Types": ", ".join(sorted(s["types"]))
    }
    for g, s in genre_stats.items()
]).sort_values("Count", ascending=False)

st.subheader("Genre Volume vs. Quality")
col1, col2 = st.columns(2)

with col1:
    fig = px.scatter(genre_df, x="Count", y="Avg Rating", size="Avg Popularity",
                     color="Avg Rating", hover_name="Genre",
                     color_continuous_scale="RdYlGn",
                     labels={"Count": "Number of Titles", "Avg Rating": "Average Vote Average"})
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.bar(genre_df.head(12), x="Count", y="Genre", orientation="h",
                 color="Avg Rating", color_continuous_scale="RdYlGn",
                 labels={"Count": "Titles Count"})
    fig.update_layout(yaxis_categoryorder="total ascending", height=450)
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Genre Ratings Breakdown")

# For each top genre, show rating distribution
top_genres = genre_df.head(6)["Genre"].tolist()

for genre in top_genres:
    genre_titles = []
    for _, row in all_content.iterrows():
        names = [id_to_name.get(g, f"Genre {g}") for g in row["genre_ids_list"]]
        if genre in names and pd.notna(row.get("vote_average")):
            genre_titles.append(row)
    
    if genre_titles:
        gdf = pd.DataFrame(genre_titles)
        avg = gdf["vote_average"].mean()
        count = len(gdf)
        
        with st.expander(f"{genre} — {count} titles, avg rating {avg:.2f}"):
            fig = px.histogram(gdf, x="vote_average", nbins=20,
                               color_discrete_sequence=["#E50914"],
                               labels={"vote_average": "Vote Average"})
            fig.update_layout(height=250, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # Top titles in this genre
            top_in_genre = gdf.nlargest(5, "vote_average")[["title" if "title" in gdf.columns else "name", "vote_average", "popularity", "content_type"]].fillna("Unknown")
            st.dataframe(top_in_genre, use_container_width=True)

st.caption(f"Data: TMDB API | {len(all_content)} records analyzed | Last refresh: {format_timestamp(fetched_at)}")
