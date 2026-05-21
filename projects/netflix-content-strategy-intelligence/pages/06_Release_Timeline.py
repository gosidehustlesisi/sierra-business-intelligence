import pandas as pd
import streamlit as st
import plotly.express as px
from utils import load_all_data, parse_genres, get_poster_url, get_tmdb_url, format_timestamp

st.set_page_config(page_title="Release Timeline", page_icon="📅", layout="wide")

data, manifest = load_all_data()

st.title("📅 Release Timeline")

fetched_at = manifest.get("fetched_at", "Unknown")
st.markdown(f'<span style="background:#E50914;color:white;padding:6px 14px;border-radius:20px;font-size:0.8rem;font-weight:600;">🔴 LIVE — Refreshed {format_timestamp(fetched_at)}</span>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

trending = data.get("trending_movies", pd.DataFrame())
tv = data.get("popular_tv", pd.DataFrame())
top_rated = data.get("top_rated_movies", pd.DataFrame())
upcoming = data.get("upcoming_movies", pd.DataFrame())

# Parse dates
def safe_date(val):
    try:
        return pd.to_datetime(val)
    except Exception:
        return pd.NaT

for df, col in [(trending, "release_date"), (top_rated, "release_date"), (upcoming, "release_date"), (tv, "first_air_date")]:
    if not df.empty and col in df.columns:
        df[col + "_dt"] = df[col].apply(safe_date)
        df["year"] = df[col + "_dt"].dt.year
        df["month"] = df[col + "_dt"].dt.month
        df["month_name"] = df[col + "_dt"].dt.strftime("%b")

st.subheader("Upcoming Releases Calendar")

if not upcoming.empty and "release_date_dt" in upcoming.columns:
    upcoming_sorted = upcoming.sort_values("release_date_dt").dropna(subset=["release_date_dt"])
    
    st.write(f"**{len(upcoming_sorted)}** upcoming movies in the pipeline")
    
    # Month breakdown
    month_counts = upcoming_sorted["month_name"].value_counts()
    month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    month_counts = month_counts.reindex([m for m in month_order if m in month_counts.index])
    
    fig = px.bar(x=month_counts.index, y=month_counts.values,
                 color=month_counts.values, color_continuous_scale="Reds",
                 labels={"x": "Month", "y": "Upcoming Releases"})
    fig.update_layout(height=350, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Show upcoming titles
    st.subheader("Upcoming Titles")
    cols = st.columns(4)
    for idx, (_, row) in enumerate(upcoming_sorted.head(12).iterrows()):
        with cols[idx % 4]:
            poster = get_poster_url(row.get("poster_path"), "w185")
            title = row.get("title", "Unknown")
            rating = row.get("vote_average", 0)
            pop = row.get("popularity", 0)
            release = row.get("release_date", "Unknown")
            tmdb_id = row.get("tmdb_id", "")
            
            if poster:
                st.image(poster, width=150)
            else:
                st.markdown(f"<div style='width:150px;height:225px;background:#1a1a1a;display:flex;align-items:center;justify-content:center;border-radius:8px;'><span style='color:#666;font-size:0.7rem;'>No Poster</span></div>", unsafe_allow_html=True)
            
            st.markdown(f"**{title[:25]}{'...' if len(title) > 25 else ''}**")
            st.markdown(f"📅 {release}")
            st.markdown(f"⭐ {rating:.2f} | 📈 {pop:.1f}")
            if tmdb_id:
                st.markdown(f"<a href='{get_tmdb_url(tmdb_id)}' target='_blank' style='font-size:0.7rem;'>TMDB →</a>", unsafe_allow_html=True)
            st.markdown("---")
else:
    st.info("No upcoming release data available.")

# Release year trends
st.subheader("Release Year Trends")

year_data = []
for df, label in [(trending, "Trending"), (top_rated, "Top Rated"), (tv, "TV")]:
    if not df.empty and "year" in df.columns:
        yc = df["year"].value_counts().sort_index()
        for year, count in yc.items():
            if pd.notna(year):
                year_data.append({"Year": int(year), "Count": count, "Type": label})

if year_data:
    year_df = pd.DataFrame(year_data)
    
    fig = px.line(year_df, x="Year", y="Count", color="Type",
                  markers=True,
                  color_discrete_sequence=["#E50914", "#564d4d", "#221f1f"])
    fig.update_layout(height=400, xaxis_title="Release Year", yaxis_title="Number of Titles")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No release year data available for trend analysis.")

# Seasonal analysis for TV
st.subheader("TV Show Seasonality")

if not tv.empty and "month" in tv.columns:
    tv_months = tv["month"].value_counts().sort_index()
    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    fig = px.bar(x=[month_labels[int(m)-1] for m in tv_months.index if pd.notna(m)], 
                 y=tv_months.values,
                 color=tv_months.values, color_continuous_scale="Blues",
                 labels={"x": "First Air Month", "y": "Number of Shows"})
    fig.update_layout(height=350, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No TV air date data available for seasonal analysis.")

st.caption(f"Data: TMDB API | Last refresh: {format_timestamp(fetched_at)}")
