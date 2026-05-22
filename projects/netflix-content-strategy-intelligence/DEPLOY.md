# 🎬 Netflix Content Strategy Intelligence

**Streamlit Dashboard** — Entertainment data analysis with honest data source indicators.

## What's Actually Implemented

| Feature | Status | Notes |
|---------|--------|-------|
| Executive Summary (KPIs, charts) | ✅ Working | Uses Kaggle dataset or TMDB data |
| Content Mix Analysis | ✅ Working | Pie charts, treemaps, bar charts |
| Genre Landscape | ✅ Working | Scatter plots, rating by genre |
| Ratings & Quality | ✅ Working | Histograms, scatter, quality tiers |
| Release Timeline | ✅ Working | Year trends, upcoming releases |
| **Trailers View** | ✅ **NEW** | YouTube embed via TMDB API or search fallback |
| Auto-Refresh Toggle | ✅ **NEW** | UI control (requires Streamlit Cloud for true auto-reload) |
| API Status Indicator | ✅ **NEW** | Shows whether TMDB key is valid |
| Data Freshness Badge | ✅ **NEW** | Hours since last fetch |
| Settings Panel | ✅ **NEW** | Manifest viewer, cache clear, file check |
| **Real-time API streaming** | ❌ **Not working** | TMDB API key invalid (status_code: 7) |
| Movie poster images | ❌ Not implemented | Would need TMDB image CDN access |
| Content Simulator | ❌ Not implemented | "What-if" tool described in DEPLOY.md but not built |
| Geographic heatmap | ❌ Not implemented | Would need country-level data |

## Data Sources (Honest)

| Source | Records | Type | Status |
|--------|---------|------|--------|
| Netflix Catalog (Kaggle CC0) | 8,807 | Static | ✅ Always available |
| TMDB Trending Movies | Variable | API | ❌ Key invalid |
| TMDB Popular TV | Variable | API | ❌ Key invalid |
| TMDB Top Rated | Variable | API | ❌ Key invalid |
| TMDB Upcoming | Variable | API | ❌ Key invalid |

**Current fallback:** The dashboard loads CSV snapshots from `data/` directory. These were generated from TMDB on May 17, 2026 but cannot be refreshed without a valid API key.

## Local Development

```bash
cd projects/netflix-content-strategy-intelligence
pip install -r requirements.txt
streamlit run dashboard.py
```

Optional: set TMDB key for live data + trailers:
```bash
export TMDB_API_KEY="your_key_here"
streamlit run dashboard.py
```

## Streamlit Cloud Deployment

1. Fork/connect repo at [share.streamlit.io](https://share.streamlit.io)
2. Set **Main file path**: `projects/netflix-content-strategy-intelligence/dashboard.py`
3. Add secrets (Settings → Secrets):
```toml
TMDB_API_KEY = "YOUR_KEY_HERE"
```
4. Deploy

## Trailer Feature

The new **Trailers** view (view 6) does two things:

1. **With valid TMDB API key:** Fetches actual YouTube trailer embeds via `/movie/{id}/videos` endpoint
2. **Without API key:** Shows top movies with YouTube search links + manual search box

This means trailers work even without a TMDB key — just with slightly more friction.

## Auto-Refresh

The dashboard includes an **auto-refresh toggle** in the sidebar. On Streamlit Cloud, this works best with:
- GitHub Actions scheduled workflow to re-fetch data
- Streamlit Cloud's native auto-redeploy on git push
- Or manual "Clear Cache & Reload" button in Settings

## Pages

| # | Page | What It Shows |
|---|------|---------------|
| 1 | 📊 Executive Summary | KPIs, content mix pie, genre bar chart, top 5 rated |
| 2 | 🎞️ Content Mix | Treemap, TV genres, rating distribution overlay |
| 3 | 🌍 Genre Landscape | Volume vs popularity scatter, avg rating by genre |
| 4 | ⭐ Ratings & Quality | Histogram, popularity scatter, quality tiers, hidden gems |
| 5 | 📅 Release Timeline | Year trend line, upcoming by month, upcoming table |
| 6 | 🎬 Trailers | **NEW** — YouTube embeds or search links |
| 7 | ⚙️ Settings | **NEW** — API status, data file check, cache clear |

---

**Built by Sierra Napier** — [GitHub](https://github.com/gosidehustlesisi) | [Portfolio](https://gosidehustlesisi.github.io/)
