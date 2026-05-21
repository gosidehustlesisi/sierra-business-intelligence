import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils import load_all_data, parse_genres, get_poster_url, get_tmdb_url, format_timestamp

st.set_page_config(page_title="Content Strategy Simulator", page_icon="🎯", layout="wide")

data, manifest = load_all_data()

st.title("🎯 Content Strategy Simulator")

fetched_at = manifest.get("fetched_at", "Unknown")
st.markdown(f'<span style="background:#E50914;color:white;padding:6px 14px;border-radius:20px;font-size:0.8rem;font-weight:600;">🔴 LIVE — Refreshed {format_timestamp(fetched_at)}</span>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
**Simulate content launch outcomes based on 438 live TMDB records.**

Select a genre, content type, target rating, and release window — get data-backed projections 
for similar titles, audience overlap, and competitive risk.
""")

# Load data
all_content = pd.concat([
    data.get("trending_movies", pd.DataFrame()).assign(content_type="Trending Movie"),
    data.get("popular_tv", pd.DataFrame()).assign(content_type="Popular TV"),
    data.get("top_rated_movies", pd.DataFrame()).assign(content_type="Top Rated Movie"),
    data.get("upcoming_movies", pd.DataFrame()).assign(content_type="Upcoming Movie")
], ignore_index=True)

all_content["genre_ids_list"] = all_content["genre_ids"].apply(parse_genres)
genres = data.get("genres", pd.DataFrame())
id_to_name = dict(zip(genres["genre_id"], genres["genre_name"])) if not genres.empty else {}

# Build simulator inputs
col1, col2, col3 = st.columns(3)

with col1:
    all_genre_names = sorted(set(id_to_name.values()))
    selected_genre = st.selectbox("🎭 Target Genre", all_genre_names, index=0 if all_genre_names else None)
    
    content_type = st.selectbox("📺 Content Type", ["Movie", "TV Series", "Limited Series"])

with col2:
    target_rating = st.slider("⭐ Target Rating", 5.0, 9.5, 7.5, 0.1)
    budget_tier = st.selectbox("💰 Budget Tier", ["Low (<$10M)", "Mid ($10-50M)", "High ($50-100M)", "Blockbuster ($100M+)"])

with col3:
    release_quarter = st.selectbox("📅 Release Window", ["Q1 (Jan-Mar)", "Q2 (Apr-Jun)", "Q3 (Jul-Sep)", "Q4 (Oct-Dec)"])
    target_audience = st.selectbox("👥 Target Audience", ["General", "Young Adult (18-34)", "Family", "Mature (35+)"])

# Run simulation
if st.button("🚀 Simulate Launch", type="primary", use_container_width=True):
    st.markdown("---")
    
    # Find similar titles in dataset
    genre_id = None
    for gid, name in id_to_name.items():
        if name == selected_genre:
            genre_id = gid
            break
    
    similar = all_content[all_content["genre_ids_list"].apply(lambda x: genre_id in x if genre_id else False)]
    
    if similar.empty:
        st.warning(f"No titles found for genre '{selected_genre}' in current dataset.")
        st.stop()
    
    # Calculate statistics
    avg_rating = similar["vote_average"].mean()
    avg_pop = similar["popularity"].mean()
    median_votes = similar["vote_count"].median()
    count = len(similar)
    
    # Rating comparison
    rating_diff = target_rating - avg_rating
    
    # Quality tier analysis
    excellent = len(similar[similar["vote_average"] >= 8.0])
    good = len(similar[(similar["vote_average"] >= 7.0) & (similar["vote_average"] < 8.0)])
    
    # Display results
    st.subheader("📊 Simulation Results")
    
    # Metrics row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Similar Titles", f"{count}", f"in {selected_genre}")
    with m2:
        st.metric("Avg Rating", f"{avg_rating:.2f}", f"{rating_diff:+.2f} vs target" if rating_diff != 0 else "On target")
    with m3:
        st.metric("Avg Popularity", f"{avg_pop:.1f}")
    with m4:
        st.metric("Excellent Titles", f"{excellent}", f"{excellent/count*100:.1f}%" if count > 0 else "0%")
    
    # Competitive landscape
    st.subheader("🏆 Competitive Landscape")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("**Top Performers in This Genre**")
        top = similar.nlargest(5, "vote_average")[["title" if "title" in similar.columns else "name", "vote_average", "popularity", "vote_count", "content_type"]]
        top.columns = ["Title", "Rating", "Popularity", "Votes", "Type"]
        st.dataframe(top, use_container_width=True)
    
    with col_b:
        st.markdown("**Rating Distribution vs. Target**")
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=similar["vote_average"], name="Genre Titles", nbinsx=20, marker_color="#E50914"))
        fig.add_vline(x=target_rating, line_dash="dash", line_color="gold", annotation_text=f"Target: {target_rating}", annotation_position="top")
        fig.update_layout(height=300, showlegend=False, xaxis_title="Vote Average", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)
    
    # Strategic recommendations
    st.subheader("💡 Strategic Recommendations")
    
    rec_col1, rec_col2, rec_col3 = st.columns(3)
    
    with rec_col1:
        st.markdown("**📈 Opportunity Assessment**")
        if excellent / count < 0.1 if count > 0 else True:
            st.success("🟢 **Blue Ocean** — Few excellent titles. High chance to stand out.")
        elif excellent / count < 0.3 if count > 0 else True:
            st.warning("🟡 **Moderate Competition** — Some quality titles exist. Differentiation needed.")
        else:
            st.error("🔴 **Red Ocean** — Many excellent titles. Must be exceptional to compete.")
        
        st.markdown(f"**Market Saturation:** {count} titles in genre")
        st.markdown(f"**Quality Threshold:** {avg_rating:.2f} average rating")
    
    with rec_col2:
        st.markdown("**🎯 Audience Overlap**")
        # Find co-occurring genres
        co_genres = {}
        for glist in similar["genre_ids_list"]:
            for gid in glist:
                if gid != genre_id:
                    name = id_to_name.get(gid, f"Genre {gid}")
                    co_genres[name] = co_genres.get(name, 0) + 1
        
        co_df = pd.DataFrame(list(co_genres.items()), columns=["Genre", "Count"]).sort_values("Count", ascending=False).head(5)
        
        st.markdown("Top co-occurring genres:")
        for _, row in co_df.iterrows():
            pct = row["Count"] / count * 100 if count > 0 else 0
            st.markdown(f"• {row['Genre']}: **{pct:.0f}%** overlap")
    
    with rec_col3:
        st.markdown("**📅 Release Timing**")
        quarter_map = {"Q1 (Jan-Mar)": [1, 2, 3], "Q2 (Apr-Jun)": [4, 5, 6], "Q3 (Jul-Sep)": [7, 8, 9], "Q4 (Oct-Dec)": [10, 11, 12]}
        target_months = quarter_map.get(release_quarter, [])
        
        # Analyze upcoming releases in target quarter
        upcoming_genre = similar[similar["content_type"] == "Upcoming Movie"] if "content_type" in similar.columns else pd.DataFrame()
        
        if not upcoming_genre.empty and "release_date" in upcoming_genre.columns:
            upcoming_genre["month"] = pd.to_datetime(upcoming_genre["release_date"], errors="coerce").dt.month
            quarter_upcoming = upcoming_genre[upcoming_genre["month"].isin(target_months)]
            
            if len(quarter_upcoming) > 0:
                st.warning(f"⚠️ **{len(quarter_upcoming)}** upcoming releases in {release_quarter}")
                st.markdown("Competitive window is crowded.")
            else:
                st.success(f"✅ **Clear quarter** — no upcoming competition in {release_quarter}")
        else:
            st.info("No upcoming release data for timing analysis.")
        
        st.markdown(f"**Recommended:** {'Q4' if selected_genre in ['Horror', 'Thriller'] else 'Q2/Q3'} for {selected_genre}")
    
    # Similar titles with posters
    st.subheader("🎬 Reference Titles (Similar to Your Concept)")
    
    ref_cols = st.columns(5)
    for idx, (_, row) in enumerate(similar.nlargest(10, "vote_average").iterrows()):
        with ref_cols[idx % 5]:
            poster = get_poster_url(row.get("poster_path"), "w185")
            title = row.get("title") or row.get("name", "Unknown")
            rating = row.get("vote_average", 0)
            tmdb_id = row.get("tmdb_id", "")
            
            if poster:
                st.image(poster, width=120)
            else:
                st.markdown(f"<div style='width:120px;height:180px;background:#1a1a1a;display:flex;align-items:center;justify-content:center;border-radius:8px;'><span style='color:#666;font-size:0.7rem;'>No Poster</span></div>", unsafe_allow_html=True)
            
            st.markdown(f"**{title[:20]}{'...' if len(title) > 20 else ''}**")
            st.markdown(f"⭐ {rating:.2f}")
            if tmdb_id:
                st.markdown(f"<a href='{get_tmdb_url(tmdb_id)}' target='_blank' style='font-size:0.7rem;'>TMDB →</a>", unsafe_allow_html=True)
            st.markdown("---")

st.caption(f"Data: TMDB API | {len(all_content)} records analyzed | Simulator uses live patterns from real data | Last refresh: {format_timestamp(fetched_at)}")
