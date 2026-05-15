"""
Amazon Product Customer Intelligence — Streamlit Dashboard
Real data from UCSD Amazon Review Dataset (Electronics, 5-core subset)
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Amazon Electronics Intelligence", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("data/amazon_reviews_electronics_5core.csv")
    df["reviewDate"] = pd.to_datetime(df["unixReviewTime"], unit="s")
    df["reviewYear"] = df["reviewDate"].dt.year
    df["reviewMonth"] = df["reviewDate"].dt.month
    df["reviewYearMonth"] = df["reviewDate"].dt.to_period("M").astype(str)
    df["reviewLength"] = df["reviewText"].fillna("").str.len()
    df["helpfulnessRatio"] = np.where(
        df["helpful_total"] > 0,
        df["helpful_upvotes"] / df["helpful_total"],
        np.nan,
    )
    return df


df = load_data()

# ── Sidebar ──
st.sidebar.title("🔧 Filters")
year_range = st.sidebar.slider("Year Range", int(df.reviewYear.min()), int(df.reviewYear.max()), (2008, 2014))
min_reviews = st.sidebar.slider("Min Reviews per Product", 1, 100, 10)

st.sidebar.markdown("---")
st.sidebar.markdown("**Data Source:**")
st.sidebar.markdown("[UCSD Amazon Review Data](http://jmcauley.ucsd.edu/data/amazon/)")
st.sidebar.markdown("Julian McAuley, UCSD")

# Filter data
mask = (df["reviewYear"] >= year_range[0]) & (df["reviewYear"] <= year_range[1])
df_f = df[mask].copy()

# ── Header ──
st.title("📦 Amazon Electronics — Customer Intelligence Dashboard")
st.caption(f"**{len(df_f):,} reviews** | {df_f.asin.nunique():,} products | {df_f.reviewerID.nunique():,} reviewers | {df_f.reviewDate.min().date()} → {df_f.reviewDate.max().date()}")

# ── KPI Row ──
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Avg Rating", f"{df_f.overall.mean():.2f} ★")
col2.metric("Helpfulness Rate", f"{(df_f[df_f.helpful_total > 0].helpful_upvotes.sum() / df_f[df_f.helpful_total > 0].helpful_total.sum() * 100):.1f}%")
col3.metric("Reviews w/ Text", f"{(df_f.reviewText.notna().sum() / len(df_f) * 100):.0f}%")
col4.metric("Peak Year", f"{df_f.groupby('reviewYear').size().idxmax()}")
col5.metric("Unique Products", f"{df_f.asin.nunique():,}")

st.markdown("---")

# ── Row 1: Product Leaderboard + Rating Distribution ──
left, right = st.columns([2, 1])

with left:
    st.subheader("🏆 Product Performance Leaderboard")
    product_stats = (
        df_f.groupby("asin")
        .agg(
            review_volume=("overall", "size"),
            avg_rating=("overall", "mean"),
            helpful_total=("helpful_total", "sum"),
            helpful_upvotes=("helpful_upvotes", "sum"),
        )
        .reset_index()
    )
    product_stats["helpfulness_rate"] = np.where(
        product_stats["helpful_total"] > 0,
        product_stats["helpful_upvotes"] / product_stats["helpful_total"],
        0,
    )
    product_stats["engagement_score"] = (
        product_stats["avg_rating"] * 0.4
        + np.log1p(product_stats["review_volume"]) * 0.4
        + product_stats["helpfulness_rate"] * 0.2
    )
    qualified = product_stats[product_stats["review_volume"] >= min_reviews].copy()
    qualified = qualified.sort_values("engagement_score", ascending=False).head(15)

    fig = go.Figure(
        go.Bar(
            y=[f"{a[:10]}..." for a in qualified["asin"]],
            x=qualified["engagement_score"],
            orientation="h",
            marker_color=qualified["avg_rating"],
            marker_colorscale="RdYlGn",
            marker_colorbar=dict(title="Avg Rating"),
            text=[f"⭐{r:.1f} | {int(v)} rev" for r, v in zip(qualified["avg_rating"], qualified["review_volume"])],
            textposition="outside",
        )
    )
    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        xaxis_title="Engagement Score",
        height=500,
        margin=dict(l=10, r=10, t=30, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("⭐ Rating Distribution")
    rating_dist = df_f["overall"].value_counts().sort_index().reset_index()
    rating_dist.columns = ["rating", "count"]
    colors = ["#d32f2f", "#f57c00", "#fbc02d", "#689f38", "#388e3c"]
    fig2 = px.bar(
        rating_dist,
        x="rating",
        y="count",
        color="rating",
        color_discrete_sequence=colors,
        text="count",
    )
    fig2.update_traces(texttemplate="%{text:,}", textposition="outside")
    fig2.update_layout(showlegend=False, height=500)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ── Row 2: Monthly Trends ──
st.subheader("📈 Monthly Review Volume & Rating Trend")
monthly = (
    df_f.groupby("reviewYearMonth")
    .agg(volume=("overall", "size"), avg_rating=("overall", "mean"))
    .reset_index()
)
monthly["reviewYearMonth"] = pd.to_datetime(monthly["reviewYearMonth"])
monthly["rating_3mo"] = monthly["avg_rating"].rolling(3, min_periods=1).mean()

fig3 = make_subplots(
    rows=2,
    cols=1,
    shared_xaxes=True,
    subplot_titles=("Reviews per Month", "Average Rating (3-month rolling)"),
    vertical_spacing=0.12,
)

fig3.add_trace(
    go.Scatter(
        x=monthly["reviewYearMonth"],
        y=monthly["volume"],
        mode="lines",
        fill="tozeroy",
        line=dict(color="steelblue"),
        name="Volume",
    ),
    row=1,
    col=1,
)

fig3.add_trace(
    go.Scatter(
        x=monthly["reviewYearMonth"],
        y=monthly["avg_rating"],
        mode="lines",
        line=dict(color="lightgray"),
        name="Monthly",
        opacity=0.5,
    ),
    row=2,
    col=1,
)

fig3.add_trace(
    go.Scatter(
        x=monthly["reviewYearMonth"],
        y=monthly["rating_3mo"],
        mode="lines",
        line=dict(color="darkgreen", width=3),
        name="3-month avg",
    ),
    row=2,
    col=1,
)

fig3.add_hline(
    y=df_f["overall"].mean(),
    line_dash="dash",
    line_color="red",
    annotation_text=f"Mean: {df_f['overall'].mean():.2f}",
    row=2,
    col=1,
)

fig3.update_layout(height=600, showlegend=True, margin=dict(l=10, r=10, t=40, b=10))
fig3.update_yaxes(title_text="Reviews", row=1, col=1)
fig3.update_yaxes(title_text="Rating", range=[3.5, 5.0], row=2, col=1)
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ── Row 3: Seasonal + Helpfulness ──
left2, right2 = st.columns(2)

with left2:
    st.subheader("🗓️ Seasonal Patterns")
    seasonal = (
        df_f.groupby(["reviewYear", "reviewMonth"])
        .size()
        .reset_index(name="volume")
        .pivot(index="reviewYear", columns="reviewMonth", values="volume")
        .fillna(0)
    )
    fig4 = px.imshow(
        seasonal,
        labels=dict(x="Month", y="Year", color="Reviews"),
        color_continuous_scale="YlOrRd",
        aspect="auto",
    )
    fig4.update_layout(height=400)
    st.plotly_chart(fig4, use_container_width=True)

with right2:
    st.subheader("👍 Helpfulness by Review Length")
    df_f["length_tier"] = pd.cut(
        df_f["reviewLength"],
        bins=[0, 100, 500, float("inf")],
        labels=["Short (<100)", "Medium (100-500)", "Long (500+)"],
    )
    helpful_by_len = (
        df_f[df_f["helpful_total"] > 0]
        .groupby("length_tier")
        .agg(
            avg_helpfulness=("helpfulnessRatio", "mean"),
            count=("asin", "size"),
        )
        .reset_index()
    )
    fig5 = px.bar(
        helpful_by_len,
        x="length_tier",
        y="avg_helpfulness",
        color="length_tier",
        text=[f"{a:.0%}\n({int(c):,})" for a, c in zip(helpful_by_len["avg_helpfulness"], helpful_by_len["count"])],
    )
    fig5.update_traces(textposition="outside")
    fig5.update_layout(showlegend=False, height=400, yaxis=dict(tickformat=".0%"))
    st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")

# ── Footer ──
st.caption(
    "Built with real Amazon review data. Source: Ni, Jianmo, Jiacheng Li, and Julian McAuley. 'Justifying recommendations using distantly-labeled reviews and fine-grained aspects.' EMNLP 2019."
)
