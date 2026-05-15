import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.linear_model import LinearRegression
import streamlit as st

st.set_page_config(page_title="Google Trends Market Intelligence", layout="wide")

st.title("🔍 Google Search Trends — Market Intelligence Dashboard")
st.markdown("*Real data via pytrends | 14 keywords | 5 years | Worldwide + US*")

# Load data
@st.cache_data
def load_data():
    df_ww = pd.read_csv("data/interest_over_time_worldwide.csv", index_col=0, parse_dates=True)
    df_region = pd.read_csv("data/interest_by_region_us.csv")
    rising = pd.read_csv("data/related_queries_rising.csv")
    return df_ww, df_region, rising

df_ww, df_region, rising = load_data()

# Sidebar
st.sidebar.header("Controls")
selected_keywords = st.sidebar.multiselect("Select Topics", df_ww.columns.tolist(), default=["AI", "ChatGPT", "inflation", "crypto"])
view_mode = st.sidebar.radio("View", ["Trend Explorer", "Regional Map", "Breakout Alerts", "Forecast", "Category Scorecard"])

if view_mode == "Trend Explorer":
    st.subheader("📈 Trend Explorer")
    if selected_keywords:
        fig = go.Figure()
        for kw in selected_keywords:
            fig.add_trace(go.Scatter(x=df_ww.index, y=df_ww[kw], name=kw, mode="lines", line=dict(width=2)))
        fig.update_layout(height=500, hovermode="x unified", template="plotly_white",
                          xaxis_title="Date", yaxis_title="Interest (0–100)")
        st.plotly_chart(fig, use_container_width=True)

        # Stats table
        stats = df_ww[selected_keywords].describe().T[["mean", "std", "min", "max"]].round(1)
        st.dataframe(stats, use_container_width=True)
    else:
        st.info("Select keywords from the sidebar.")

elif view_mode == "Regional Map":
    st.subheader("🗺️ Regional Interest by State")
    kw = st.selectbox("Keyword", df_ww.columns)
    sub = df_region[df_region["keyword"] == kw]
    fig = px.choropleth(sub, locations="geoCode", color="interest", hover_name="geoName",
                        scope="usa", color_continuous_scale="Viridis",
                        title=f'Regional Interest: "{kw}"')
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(sub.sort_values("interest", ascending=False).head(10), use_container_width=True)

elif view_mode == "Breakout Alerts":
    st.subheader("🔥 Breakout Alerts — Rising Queries")
    for kw in rising["keyword"].unique()[:10]:
        sub = rising[rising["keyword"] == kw].head(3)
        if not sub.empty:
            with st.expander(f"{kw}"):
                for _, row in sub.iterrows():
                    st.write(f"• **{row['query']}** — +{row['value']}%")

elif view_mode == "Forecast":
    st.subheader("📊 1-Year Linear Forecast")
    forecast = []
    for kw in df_ww.columns:
        y = df_ww[kw].values
        X = np.arange(len(y)).reshape(-1, 1)
        model = LinearRegression().fit(X, y)
        future = np.array([[len(y) + i] for i in range(1, 53)])
        preds = model.predict(future)
        trend = "↗ Up" if model.coef_[0] > 0.05 else ("↘ Down" if model.coef_[0] < -0.05 else "→ Flat")
        forecast.append({"Keyword": kw, "Current": round(y[-4:].mean(), 1),
                         "Forecast Avg": round(preds.mean(), 1), "Trend": trend})
    forecast_df = pd.DataFrame(forecast).sort_values("Forecast Avg", ascending=False)
    st.dataframe(forecast_df, use_container_width=True)

    # Chart top 5 trending up
    up_trends = forecast_df[forecast_df["Trend"] == "↗ Up"].head(5)
    if not up_trends.empty:
        fig = px.bar(up_trends, x="Keyword", y="Forecast Avg", color="Forecast Avg",
                     title="Top 5 Upward-Trending Topics")
        st.plotly_chart(fig, use_container_width=True)

elif view_mode == "Category Scorecard":
    st.subheader("🏆 Category Performance Scorecard")
    cats = {
        "Tech": ["AI", "machine learning", "ChatGPT", "Bitcoin", "Tesla", "Netflix", "Amazon"],
        "Health": ["telehealth", "mental health", "fitness"],
        "Finance": ["inflation", "recession", "stock market", "crypto"]
    }
    scorecard = []
    for cat, kws in cats.items():
        valid = [k for k in kws if k in df_ww.columns]
        avg = df_ww[valid].mean().mean()
        peak = df_ww[valid].max().max()
        recent = df_ww[valid].iloc[-52:].mean().mean()
        prior = df_ww[valid].iloc[-104:-52].mean().mean() if len(df_ww) >= 104 else df_ww[valid].iloc[:52].mean().mean()
        growth = ((recent - prior) / prior * 100) if prior > 0 else 0
        scorecard.append({"Category": cat, "Avg Interest": round(avg, 1), "Peak": int(peak),
                          "Recent Avg": round(recent, 1), "YoY Growth %": round(growth, 1)})
    scorecard_df = pd.DataFrame(scorecard)
    st.dataframe(scorecard_df, use_container_width=True)
    fig = px.bar(scorecard_df, x="Category", y="YoY Growth %", color="YoY Growth %",
                 text="YoY Growth %", title="Category YoY Growth %")
    st.plotly_chart(fig, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.caption("Built by Sierra Napier | e3-ai.com")
