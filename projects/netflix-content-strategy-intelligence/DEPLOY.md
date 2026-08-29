# 🎬 Netflix Content Strategy Intelligence

**Streamlit Dashboard** — Entertainment data analysis with honest data source indicators.

## What's Actually Implemented

This table describes `dashboard.py` specifically — the separate multipage app (`app.py` + `pages/`) has a different, broader feature set (see its own page list further down in this repo's `README.md`), including a Content Simulator and geographic heatmap that `dashboard.py` does not have.

| Feature | Status | Notes |
|---------|--------|-------|
| Executive Summary (KPIs, charts) | ✅ Working | Uses the live TMDB snapshot (`data/*_latest.csv`) |
| Content Mix Analysis | ✅ Working | Pie charts, treemaps, bar charts |
| Genre Landscape | ✅ Working | Scatter plots, rating by genre |
| Ratings & Quality | ✅ Working | Histograms, scatter, quality tiers |
| Release Timeline | ✅ Working | Year trends, upcoming releases |
| **Trailers View** | ✅ **NEW** | YouTube embed via TMDB API or search fallback |
| Auto-Refresh Toggle | ✅ **NEW** | UI control (requires Streamlit Cloud for true auto-reload) |
| API Status Indicator | ✅ **NEW** | Shows whether TMDB key is valid — check this live rather than trusting a static claim here |
| Data Freshness Badge | ✅ **NEW** | Hours since last fetch |
| Settings Panel | ✅ **NEW** | Manifest viewer, cache clear, file check |
| Movie poster images | ❌ Not implemented in `dashboard.py` | Would need TMDB image CDN access (the separate `pages/` app does use poster URLs via `utils.py`) |
| Content Simulator | ❌ Not implemented in `dashboard.py` | Implemented separately in `pages/07_Content_Simulator.py`, part of the `app.py` multipage app |
| Geographic heatmap | ❌ Not implemented in `dashboard.py` | Implemented separately in `pages/04_Geographic_Insights.py` |

## Data Sources (Honest)

`dashboard.py` loads only the live TMDB snapshot layer — it does not load the self-extracted Netflix catalog CSVs at all (those power the standalone analysis scripts/notebooks and the GitHub Pages figures instead; see the project `README.md`'s "Data Sources" table).

| Source | Records | Type | Status |
|--------|---------|------|--------|
| TMDB Trending Movies | 100 | API snapshot | ✅ Refreshed daily via `.github/workflows/tmdb-refresh.yml` |
| TMDB Popular TV | 100 | API snapshot | ✅ Refreshed daily |
| TMDB Genres | 19 | API snapshot | ✅ Refreshed daily |
| TMDB Genre Popularity | 19 | API snapshot | ✅ Refreshed daily |
| TMDB Upcoming | 100 | API snapshot | ✅ Refreshed daily |

**Current data:** The dashboard loads CSV snapshots from the `data/` directory, refreshed automatically every day by the scheduled GitHub Actions workflow using a valid TMDB key (confirmed working — see `data/manifest_latest.json`'s `fetched_at` timestamp for the most recent successful run). That's separate from whether a Streamlit Cloud deployment of this app has its own `TMDB_API_KEY` secret configured — check this dashboard's own **Settings → API Status Indicator** for that, rather than trusting a static claim here.

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
