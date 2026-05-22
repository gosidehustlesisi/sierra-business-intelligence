# 🎬 Netflix Content Strategy Intelligence

**Live Streamlit Dashboard** — Real-time entertainment data from TMDB API.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](DEPLOYMENT_URL_PLACEHOLDER)

## What's Inside

- **7-page interactive dashboard** with real TMDB data
- **438 live records** (trending movies, popular TV, top-rated, upcoming, genres)
- **Real movie posters** from TMDB CDN
- **YouTube trailers** embedded for each title
- **Content Strategy Simulator** — "what-if" launch planning tool

## Data Sources

| Source | Records | Type |
|--------|---------|------|
| TMDB Trending Movies | 100 | Live API |
| TMDB Popular TV | 100 | Live API |
| TMDB Top Rated Movies | 100 | Live API |
| TMDB Upcoming Movies | 100 | Live API |
| TMDB Genre Mapping | 19 | Live API |
| Netflix Catalog (Kaggle) | 8,807 | Static Reference |

**Total: 9,245 records** (438 live + 8,807 reference)

## Local Development

```bash
pip install -r requirements.txt
streamlit run app.py
```

Set environment variables:
```bash
export TMDB_API_KEY="your_key"
export TMDB_READ_TOKEN="your_token"
```

## Streamlit Cloud Deployment

### Step 1: Fork/Connect Repo
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select `gosidehustlesisi/sierra-business-intelligence`
5. Set **Main file path**: `projects/netflix-content-strategy-intelligence/app.py`

### Step 2: Add Secrets
In Streamlit Cloud dashboard:
1. Click your app → "Settings" → "Secrets"
2. Add:
```toml
TMDB_API_KEY = "YOUR_TMDB_API_KEY_HERE"
TMDB_READ_TOKEN = "YOUR_TMDB_READ_TOKEN_HERE"
```

### Step 3: Deploy
Click "Deploy" — Streamlit Cloud will:
- Install dependencies from `requirements.txt`
- Launch the multi-page app
- Auto-redeploy on every git push

## Auto-Refresh

GitHub Actions runs daily at 06:00 UTC to re-fetch TMDB data:
- Workflow: `.github/workflows/tmdb-refresh.yml`
- Commits updated CSVs to repo
- Streamlit Cloud auto-redeploys on commit

## Pages

| Page | What It Shows |
|------|--------------|
| 📊 Executive Summary | KPIs, content mix, quality tiers |
| 🔍 Live Data Explorer | Sortable cards with posters & trailers |
| 🎭 Genre Analysis | Genre breakdown, ratings distribution |
| 🌍 Geographic Insights | Content by origin country |
| ⭐ Ratings & Quality | Quality tiers, hidden gems |
| 📅 Release Timeline | Upcoming releases, seasonal patterns |
| 🎯 Content Simulator | "What-if" launch planning tool |

## Trailer Integration

TMDB's `/movie/{id}/videos` endpoint returns YouTube trailer keys. The dashboard:
- Auto-fetches trailers during data refresh
- Embeds YouTube player in each movie's "Details" expander
- Shows official trailer when available, fallback to any trailer

---

**Built by Sierra Napier** — [GitHub](https://github.com/gosidehustlesisi) | [Portfolio](https://gosidehustlesisi.github.io/)
