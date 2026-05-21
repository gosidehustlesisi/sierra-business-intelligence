import pandas as pd
import streamlit as st
import plotly.express as px
from utils import load_all_data, parse_genres, get_poster_url, get_tmdb_url, format_timestamp

st.set_page_config(page_title="Live Data Explorer", page_icon="🔍", layout="wide")

data, manifest = load_all_data()

st.title("🔍 Live Data Explorer")

fetched_at = manifest.get("fetched_at", "Unknown")
st.markdown(f'<span style="background:#E50914;color:white;padding:6px 14px;border-radius:20px;font-size:0.8rem;font-weight:600;">🔴 LIVE — Refreshed {format_timestamp(fetched_at)}</span>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Combine all content
trending = data.get("trending_movies", pd.DataFrame())
tv = data.get("popular_tv", pd.DataFrame())
top_rated = data.get("top_rated_movies", pd.DataFrame())
upcoming = data.get("upcoming_movies", pd.DataFrame())
genres = data.get("genres", pd.DataFrame())

all_dfs = []
if not trending.empty:
    df = trending.copy()
    df["content_type"] = "🎬 Trending Movie"
    df["display_title"] = df.get("title", "Unknown")
    all_dfs.append(df)
if not tv.empty:
    df = tv.copy()
    df["content_type"] = "📺 Popular TV"
    df["display_title"] = df.get("name", "Unknown")
    all_dfs.append(df)
if not top_rated.empty:
    df = top_rated.copy()
    df["content_type"] = "⭐ Top Rated Movie"
    df["display_title"] = df.get("title", "Unknown")
    all_dfs.append(df)
if not upcoming.empty:
    df = upcoming.copy()
    df["content_type"] = "🆕 Upcoming Movie"
    df["display_title"] = df.get("title", "Unknown")
    all_dfs.append(df)

if not all_dfs:
    st.error("No data loaded. Check data files in the data/ directory.")
    st.stop()

all_content = pd.concat(all_dfs, ignore_index=True)
all_content["genre_ids_list"] = all_content["genre_ids"].apply(parse_genres)
id_to_name = dict(zip(genres["genre_id"], genres["genre_name"])) if not genres.empty else {}

# Sidebar filters
st.sidebar.header("Filters")

content_types = st.sidebar.multiselect("Content Type", all_content["content_type"].unique().tolist(), default=all_content["content_type"].unique().tolist())

# Genre filter
all_genre_names = set()
for glist in all_content["genre_ids_list"]:
    for gid in glist:
        all_genre_names.add(id_to_name.get(gid, f"Genre {gid}"))
genre_options = sorted(list(all_genre_names))
selected_genres = st.sidebar.multiselect("Genres", genre_options)

# Rating range
min_rating, max_rating = st.sidebar.slider("Rating Range", 0.0, 10.0, (0.0, 10.0), 0.5)

# Popularity range
min_pop = float(all_content["popularity"].min()) if "popularity" in all_content.columns else 0
max_pop = float(all_content["popularity"].max()) if "popularity" in all_content.columns else 1000
pop_range = st.sidebar.slider("Popularity Range", min_pop, max_pop, (min_pop, max_pop))

# Search
search = st.sidebar.text_input("Search Titles", "").lower()

# Apply filters
filtered = all_content[all_content["content_type"].isin(content_types)]

if selected_genres:
    def has_genre(glist):
        names = [id_to_name.get(g, f"Genre {g}") for g in glist]
        return any(g in names for g in selected_genres)
    filtered = filtered[filtered["genre_ids_list"].apply(has_genre)]

if "vote_average" in filtered.columns:
    filtered = filtered[(filtered["vote_average"] >= min_rating) & (filtered["vote_average"] <= max_rating)]

if "popularity" in filtered.columns:
    filtered = filtered[(filtered["popularity"] >= pop_range[0]) & (filtered["popularity"] <= pop_range[1])]

if search:
    filtered = filtered[filtered["display_title"].str.lower().str.contains(search, na=False)]

st.subheader(f"Showing {len(filtered)} of {len(all_content)} titles")

# Display as cards
cols_per_row = 4
rows = [filtered.iloc[i:i+cols_per_row] for i in range(0, len(filtered), cols_per_row)]

for row_df in rows:
    cols = st.columns(cols_per_row)
    for idx, (_, row) in enumerate(row_df.iterrows()):
        with cols[idx]:
            poster = get_poster_url(row.get("poster_path"), "w185")
            title = row.get("display_title", "Unknown")
            rating = row.get("vote_average", 0)
            votes = row.get("vote_count", 0)
            pop = row.get("popularity", 0)
            tmdb_id = row.get("tmdb_id", "")
            ctype = row.get("content_type", "")
            
            # Poster
            if poster:
                st.image(poster, use_container_width=True)
            else:
                st.markdown(f"<div style='height:200px;background:#1a1a1a;display:flex;align-items:center;justify-content:center;border-radius:8px;'><span style='color:#666;font-size:0.8rem;'>🎬 No Poster</span></div>", unsafe_allow_html=True)
            
            # Title
            st.markdown(f"<p style='font-weight:600;margin:4px 0;font-size:0.95rem;'>🎬 {title[:35]}{'...' if len(title) > 35 else ''}</p>", unsafe_allow_html=True)
            
            # Meta
            st.markdown(f"<p style='color:#888;font-size:0.8rem;margin:2px 0;'>⭐ {rating:.2f} ({votes:,} votes) | 📈 {pop:.1f}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#aaa;font-size:0.75rem;margin:2px 0;'>{ctype}</p>", unsafe_allow_html=True)
            
            # Genres
            genre_names = [id_to_name.get(g, f"Genre {g}") for g in row.get("genre_ids_list", [])]
            if genre_names:
                st.markdown(f"<p style='color:#E50914;font-size:0.7rem;margin:2px 0;'>🏷️ {', '.join(genre_names[:3])}</p>", unsafe_allow_html=True)
            
            # Expandable details
            with st.expander("Details", expanded=False):
                overview = row.get("overview", "")
                release_date = row.get("release_date") or row.get("first_air_date", "")
                original_language = row.get("original_language", "")
                origin_country = row.get("origin_country", "")
                
                if overview:
                    st.markdown(f"**Overview:** {overview[:200]}{'...' if len(overview) > 200 else ''}")
                if release_date:
                    st.markdown(f"**Release:** {release_date}")
                if original_language:
                    st.markdown(f"**Language:** {original_language}")
                if origin_country and isinstance(origin_country, str):
                    st.markdown(f"**Origin:** {origin_country}")
                
                # Full TMDB link
                if tmdb_id:
                    st.markdown(f"[View on TMDB →]({get_tmdb_url(tmdb_id)})")
            
            st.markdown("<hr style='margin:8px 0;border-color:#333;'>", unsafe_allow_html=True)

st.caption(f"Data: TMDB API | {len(all_content)} total records | Filtered to {len(filtered)} | Last refresh: {format_timestamp(fetched_at)}")
