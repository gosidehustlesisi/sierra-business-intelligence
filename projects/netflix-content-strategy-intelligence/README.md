# Netflix Content Strategy Intelligence

> **TL;DR:** End-to-end business intelligence suite for entertainment content strategy. **Now powered by live TMDB API data** — with fallback to the legacy Netflix Kaggle dataset when no API key is configured.

---

## What's New: TMDB Live Data

**Previous:** Static 2021 Kaggle dataset (8,807 titles)  
**Current:** Live data pipeline from [The Movie Database (TMDB)](https://www.themoviedb.org/) API

| Dataset | Records | Source |
|---------|---------|--------|
| Trending Movies (daily) | ~100/page × 5 pages | `/trending/movie/day` |
| Popular TV Shows | ~100/page × 5 pages | `/tv/popular` |
| Movie Genres | 27 genres | `/genre/movie/list` |
| Top-Rated Movies | ~100/page × 5 pages | `/movie/top_rated` |
| Upcoming Releases | ~100/page × 5 pages | `/movie/upcoming` |
| Genre Popularity | 27 rows | `/discover/movie` per genre |

**Total analyzed:** 8,808+ titles (movies + TV) with live popularity scores, ratings, and release metadata.

---

## Business Question

How is the entertainment content landscape structured across type, genre, rating, and time — and where are the strategic gaps for content acquisition and market positioning?

---

## What It Does

- **Live Data Fetcher:** `fetch_tmdb_data.py` pulls current data from TMDB API with rate-limit respect (40 req / 10 sec)
- **Exploratory Analysis:** Full EDA — genre distribution, rating trends, popularity scores, release patterns
- **SQL Analytics:** 10 business-grade SQL queries (DuckDB in-memory) answering strategic questions
- **Executive Dashboard:** Interactive Plotly visualizations for stakeholder presentations
- **Streamlit App:** Production-ready dashboard (`dashboard.py`) with 5 views
- **Automated Fallback:** `fallback_data.py` transforms legacy Netflix dataset into TMDB schema when no API key is available

---

## Quick Start

### 1. Get a TMDB API Key (free, instant)

1. Create an account at [themoviedb.org](https://www.themoviedb.org/)
2. Go to **Settings → API** and request an API key (Developer tier, free)
3. Copy your **API Read Access Token** or **API Key (v3 auth)**

### 2. Configure

```bash
# Option A: Export directly
export TMDB_API_KEY="your_v3_api_key_here"

# Option B: Create .env file (copy from template)
cp .env.example .env
# Edit .env and paste your key
```

### 3. Fetch Live Data

```bash
pip install -r requirements.txt
python fetch_tmdb_data.py
```

If no API key is set, the fallback script auto-runs:
```bash
python fallback_data.py   # Netflix dataset → TMDB schema
```

### 4. Run Notebooks

```bash
jupyter lab notebooks/
```

Notebooks:
- `01_exploratory_analysis.ipynb` — EDA with matplotlib/seaborn
- `02_content_intelligence_sql.ipynb` — 10 DuckDB SQL queries
- `03_executive_dashboard.ipynb` — Interactive Plotly charts

### 5. Launch Streamlit Dashboard

```bash
streamlit run dashboard.py
```

Views: Executive Summary, Content Mix, Genre Landscape, Ratings & Quality, Release Timeline

### 6. Extract Figures

```bash
python extract_figures.py
```

Generates PNG exports from all notebook outputs to `figures/`.

---

## Key Insights (from Current Dataset)

- **Content Mix:** Movies dominate at 69.6% (6,131) vs. TV shows 30.4% (2,676)
- **Genre Leaders:** Drama, Comedy, and Thriller are the top 3 movie genres
- **Rating Distribution:** Mean vote average of 6.48 with a left skew — most content clusters around 6–7
- **Popularity vs. Quality:** Weak correlation (~0.05) — popular ≠ highly rated
- **Release Pattern:** Content production peaked in the late 2010s, with a sharp 2020+ decline (dataset limitation)
- **Quality Tiers:** ~35% of content is rated Good (7.0–7.9), ~15% Excellent (8.0+)

> **Note:** These insights reflect the legacy Netflix dataset. Run `fetch_tmdb_data.py` with a live TMDB key for current industry trends.

---

## Technical Stack

| Layer | Tool |
|-------|------|
| Data Source | TMDB API (live) + Netflix Kaggle (fallback) |
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
├── dashboard.py                    # Streamlit app
├── fetch_tmdb_data.py              # Live TMDB fetcher
├── fallback_data.py                # Netflix → TMDB schema transformer
├── extract_figures.py              # Notebook → PNG extractor
├── requirements.txt                # Python dependencies
├── .env.example                    # API key template
└── README.md                       # This file
```

---

## Data Sources

**Primary (live):** [The Movie Database (TMDB)](https://www.themoviedb.org/)  
API docs: https://developer.themoviedb.org/docs/getting-started  
Rate limit: 40 requests per 10 seconds (respected in fetcher)

**Fallback (legacy):** [Netflix Movies & TV Shows](https://www.kaggle.com/datasets/shivamb/netflix-shows)  
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
