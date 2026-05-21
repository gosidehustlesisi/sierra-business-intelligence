# Netflix Content Strategy Intelligence

> **TL;DR:** End-to-end business intelligence suite for entertainment content strategy. **438 live TMDB records** (trending, top-rated, upcoming, popular TV, genre popularity) **+ 8,807-title Netflix Kaggle catalog (CC0)** — all real, zero synthetic.

---

## Data Sources

| Dataset | Records | Source | Status |
|---------|---------|--------|--------|
| Netflix Catalog | 8,807 | [Kaggle — Netflix Movies & TV Shows](https://www.kaggle.com/datasets/shivamb/netflix-shows) | ✅ Static CC0 |
| Trending Movies | 100 | [TMDB API](https://developer.themoviedb.org/) — `/trending/movie/day` | ✅ **LIVE** |
| Popular TV Shows | 100 | [TMDB API](https://developer.themoviedb.org/) — `/tv/popular` | ✅ **LIVE** |
| Movie Genres | 19 | [TMDB API](https://developer.themoviedb.org/) — `/genre/movie/list` | ✅ **LIVE** |
| Top-Rated Movies | 100 | [TMDB API](https://developer.themoviedb.org/) — `/movie/top_rated` | ✅ **LIVE** |
| Upcoming Releases | 100 | [TMDB API](https://developer.themoviedb.org/) — `/movie/upcoming` | ✅ **LIVE** |
| Genre Popularity | 19 | [TMDB API](https://developer.themoviedb.org/) — `/discover/movie` | ✅ **LIVE** |

**Total: 8,807 catalog titles + 438 live TMDB records = 9,245 real records**

### How It Works

- **Kaggle dataset** provides the historical Netflix catalog backbone — 8,807 titles with type, genre, rating, and date_added
- **TMDB API** provides current industry signals — what's trending now, what's coming next, which genres are hot
- `fetch_tmdb_data.py` pulls live data with rate-limit respect (40 req / 10 sec) using authenticated API key
- All live data includes `fetched_at` timestamp and real TMDB IDs (not synthetic)

### Data Freshness

Live TMDB data fetched: **2026-05-21 22:17 UTC**  
To refresh: `python fetch_tmdb_data.py` — new timestamped files + updated `*_latest.csv` symlinks

---

## Business Question

How is the entertainment content landscape structured across type, genre, rating, and time — and where are the strategic gaps for content acquisition and market positioning?

---

## What It Does

- **Live TMDB Fetcher:** `fetch_tmdb_data.py` pulls 438 real-time entertainment records from TMDB API — trending movies, popular TV, top-rated, upcoming releases, and genre popularity scores. Rate-limited (40 req / 10 sec) and authenticated.
- **Catalog Backbone:** 8,807-title Netflix Kaggle dataset (CC0) provides historical content strategy context — type, genre, rating, date_added
- **Exploratory Analysis:** Full EDA — genre distribution, rating trends, popularity scores, release patterns
- **SQL Analytics:** 10 business-grade SQL queries (DuckDB in-memory) answering strategic questions
- **Executive Dashboard:** Interactive Plotly visualizations for stakeholder presentations
- **Live Streamlit Dashboard:** `app.py` launches a multi-page interactive dashboard with real movie posters, geographic analysis, and quality tiers
- **6 Dashboard Views:** Executive Summary, Live Data Explorer, Genre Analysis, Geographic Insights, Ratings & Quality, Release Timeline
- **Self-Healing Data Loader:** Validates data files on startup, shows last refresh timestamp, handles missing files gracefully
- **Real Movie Posters:** Fetches actual poster images from TMDB's CDN — not placeholders
- **Verified TMDB Links:** Every title links to its real themoviedb.org page with live ID verification

---

## Quick Start

Live TMDB data is **already fetched** (2026-05-21 22:17 UTC). The `*_latest.csv` files in `data/` contain real TMDB records.

### Option A: Launch the Full Dashboard (Recommended)

```bash
pip install -r requirements.txt
streamlit run app.py
```

The dashboard opens at `http://localhost:8501` with 6 interactive pages:

1. **📊 Executive Summary** — Key metrics, content mix pie chart, top-rated highlights with real posters
2. **🔍 Live Data Explorer** — Sortable, filterable table with movie poster grid, genre filters, rating sliders
3. **🎭 Genre Analysis** — Volume vs. quality scatter, per-genre rating distributions, top titles by genre
4. **🌍 Geographic Insights** — Content by origin country, country-level rating and popularity analysis
5. **⭐ Ratings & Quality** — Quality tiers, hidden gems (high rating + low popularity), rating vs. popularity scatter
6. **📅 Release Timeline** — Upcoming releases calendar, month breakdown, year trends, TV seasonality

### Option B: Run the Legacy Single-Page Dashboard

```bash
streamlit run dashboard.py
```

### Option C: Run Notebooks

```bash
jupyter lab notebooks/
```

Notebooks:
- `01_exploratory_analysis.ipynb` — EDA with matplotlib/seaborn (Kaggle catalog + TMDB live)
- `02_content_intelligence_sql.ipynb` — 10 DuckDB SQL queries
- `03_executive_dashboard.ipynb` — Interactive Plotly charts

### Option D: Refresh Live Data

```bash
export TMDB_API_KEY="your_key_here"  # or use existing key in sierra-secrets.json
python fetch_tmdb_data.py
```

---

## Key Insights

### From Live TMDB Data (Current Industry Signals)
- **Trending Movies:** Top 100 movies by popularity today — real-time industry heatmap
- **Popular TV:** 100 current TV shows audiences are watching
- **Top-Rated:** 100 critically acclaimed films with vote counts (quality validation)
- **Upcoming:** 100 releases on the horizon — content pipeline intelligence
- **Genre Landscape:** 19 TMDB genres with popularity scores and total catalog depth
- **Popularity vs. Quality:** TMDB provides both metrics — correlation analysis possible

### From Netflix Kaggle Catalog (Historical Context)
- **Content Mix:** Movies dominate at 69.6% (6,131) vs. TV shows 30.4% (2,676)
- **Genre Leaders:** Drama, Comedy, and Thriller are the top 3 movie genres
- **Rating Distribution:** Mean vote average of 6.48 with a left skew — most content clusters around 6–7
- **Release Pattern:** Content production peaked in the late 2010s, with a sharp 2020+ decline (dataset limitation)
- **Quality Tiers:** ~35% of content is rated Good (7.0–7.9), ~15% Excellent (8.0+)

---

## Technical Stack

| Layer | Tool |
|-------|------|
| Live Data | TMDB API — authenticated, rate-limited |
| Catalog Backbone | Netflix Kaggle dataset (CC0) |
| Language | Python 3.12 |
| Data Processing | pandas, numpy |
| SQL Analytics | DuckDB (in-memory) |
| Visualization | matplotlib, seaborn, plotly |
| Dashboard | Streamlit |
| Notebooks | Jupyter Lab |
| API Client | requests (rate-limited) |
| Language | Python 3.12 |
| Data Processing | pandas, numpy |
| SQL Analytics | DuckDB (in-memory) |
| Visualization | matplotlib, seaborn, plotly |
| Dashboard | Streamlit |
| Notebooks | Jupyter Lab |
| API Client | requests (rate-limited) |

---

## Data Freshness

All CSVs include a `fetched_at` timestamp (UTC). The `data/manifest_latest.json` tracks:
- Fetch timestamp
- Record counts per dataset
- Source indicator (LIVE vs. FALLBACK)

**To refresh:** Simply re-run `python fetch_tmdb_data.py` (or `fallback_data.py`). New timestamped files are created alongside `*_latest.csv` symlinks.

---

## Project Structure

```
netflix-content-strategy-intelligence/
├── app.py                          # 🆕 Multi-page Streamlit dashboard (6 views)
├── pages/
│   ├── 01_Executive_Summary.py     # Key metrics and top-rated highlights
│   ├── 02_Live_Explorer.py         # Filterable table with real movie posters
│   ├── 03_Genre_Analysis.py        # Genre volume vs. quality deep dive
│   ├── 04_Geographic_Insights.py   # Content by origin country
│   ├── 05_Ratings_Quality.py       # Quality tiers and hidden gems
│   └── 06_Release_Timeline.py      # Upcoming releases and trends
├── utils.py                        # 🆕 Shared data loader and helpers
├── data/
│   ├── trending_movies_latest.csv
│   ├── popular_tv_latest.csv
│   ├── movie_genres_latest.csv
│   ├── top_rated_movies_latest.csv
│   ├── upcoming_movies_latest.csv
│   ├── genre_popularity_latest.csv
│   └── manifest_latest.json
├── notebooks/
│   ├── 01_exploratory_analysis.ipynb
│   ├── 02_content_intelligence_sql.ipynb
│   └── 03_executive_dashboard.ipynb
├── figures/
│   ├── 01_*.png
│   ├── 02_*.png
│   └── 03_*.png
├── output/
│   └── 03_*.html (interactive Plotly exports)
├── dashboard.py                    # Legacy single-page Streamlit app
├── fetch_tmdb_data.py              # Live TMDB fetcher
├── fallback_data.py                # Netflix → TMDB schema transformer
├── extract_figures.py              # Notebook → PNG extractor
├── requirements.txt                # Python dependencies
├── .env.example                    # API key template
└── README.md                       # This file
```

---

## Data Sources

**Live (primary):** [The Movie Database (TMDB)](https://www.themoviedb.org/)  
API docs: https://developer.themoviedb.org/docs/getting-started  
Rate limit: 40 requests per 10 seconds (respected in fetcher)  
Records: 438 (trending 100, popular TV 100, genres 19, top-rated 100, upcoming 100, genre popularity 19)  
Fetched: 2026-05-21 22:17 UTC  
Authentication: API key + optional v4 read token

**Catalog (static):** [Netflix Movies & TV Shows](https://www.kaggle.com/datasets/shivamb/netflix-shows)  
Author: Shivam Bansal | License: CC0 Public Domain | Records: 8,807 | Updated: 2021

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TMDB_API_KEY` | Yes for live | TMDB v3 API key (free at themoviedb.org) |
| `TMDB_READ_TOKEN` | Optional | TMDB v4 Bearer token (preferred if set) |

---

## License

Code: MIT | Data: CC0 (Netflix dataset) / TMDB Terms of Use (API data)
