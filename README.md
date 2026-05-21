<div align="center">

<img src="https://raw.githubusercontent.com/gosidehustlesisi/sierra-business-intelligence/main/avatar.png" width="120" style="border-radius: 50%;" alt="Sierra Napier avatar">

<h1>SIERRA BUSINESS INTELLIGENCE</h1>

> **Real Netflix catalog data (Kaggle + TMDB Live), real Amazon reviews, real Google Trends — zero synthetic records.**

<p>
  <b>78,055+ real records · 3 projects · 9 notebooks · 49+ charts</b>
</p>

<p>
  <a href="https://github.com/gosidehustlesisi/sierra-business-intelligence">
    <img src="https://img.shields.io/badge/GitHub-Repo-181717?logo=github" alt="GitHub">
  </a>
  <img src="https://img.shields.io/badge/Data-Real%20Records-2ea44f" alt="Real Data">
  <img src="https://img.shields.io/badge/Synthetic-Zero-red" alt="Zero Synthetic">
  <img src="https://img.shields.io/badge/Notebooks-9-blue" alt="9 Notebooks">
  <img src="https://img.shields.io/badge/Charts-49+-orange" alt="49+ Charts">
</p>

</div>

---

I analyze complex data at scale, architect AI systems that automate it, and visualize the story so stakeholders act on it.

---

## Verified Data Sources

| Source | Verification | Records |
|---|---|---|
| **Kaggle** — Netflix Movies & TV Shows | Direct CSV download, SHA-verified | 8,807 titles |
| **TMDB** — Trending, Top-Rated, Upcoming + Genre Popularity | Live API via `fetch_tmdb_data.py` | 438 live records |
| **UCSD** — Amazon Reviews (Electronics 5-core) | Direct CSV download | 67,325 reviews |
| **Google Trends** — pytrends API + BigQuery | Live API extraction, weekly granularity | 1,923 trend records |

These aren't toy models. Every number below came from running real code on real data.

---

## At a Glance

| Project | Domain | Records | Source | Notebooks | Charts | Status |
|---|---|---|---|---|---|---|
| **Netflix Content Strategy** | Media & Entertainment | 9,245 titles | Kaggle Netflix (CC0) + TMDB Live | 3 | 17+ | ✅ Complete |
| **Amazon Review Intelligence** | E-commerce & Retail | 67,325 reviews | UCSD Amazon 5-core | 3 | 21+ | ✅ Complete |
| **Google Search Trends** | Market Intelligence | 1,923 records | pytrends live API | 3 | 11+ | ✅ Complete |

**Total: 78,055+ real records · 9 notebooks · 49+ production charts · 0 synthetic data**

---

## About This Work

This portfolio bridges three high-value business domains — **content strategy**, **review intelligence**, and **market trends** — using the same end-to-end pattern: ingest real data, run business-grade SQL analytics, and ship stakeholder-ready dashboards.

The arc: **data → insight → action**. Every project starts with a real public or live API dataset, progresses through exploratory analysis and 10+ business SQL queries, and ends with an interactive Streamlit dashboard that a VP could open in a meeting.

I built this because hiring managers in BI and analytics roles don't need toy models — they need proof that a candidate can work with messy real data, write clean SQL, and communicate findings to decision-makers. This is that proof.

---

## Project 1: Netflix Content Strategy Intelligence

<p>
  <img src="https://img.shields.io/badge/Source-Kaggle%20Netflix-CC0-brightgreen" alt="Kaggle">
  <img src="https://img.shields.io/badge/Source-TMDB%20Live-01b4e4" alt="TMDB">
  <img src="https://img.shields.io/badge/SQL-DuckDB-yellow" alt="DuckDB">
  <img src="https://img.shields.io/badge/Dashboard-Streamlit-ff4b4b" alt="Streamlit">
</p>

### What This Means for Business

Content acquisition and portfolio management decisions backed by SQL-driven lifecycle analysis on 8,807-title Kaggle catalog **plus 438 live records from TMDB API** (trending, top-rated, upcoming, genre popularity). I quantified that TV shows reach Netflix 2.5× faster than movies (2.1 vs. 5.3 years), identified US concentration at 36.8% of the catalog, and flagged International Movies as the top genre opportunity at 14.2% share. Live TMDB data adds current genre popularity scores and upcoming release pipeline visibility.

### Why This Matters to Hiring Managers

I wrote 10 business-facing SQL queries in DuckDB against a real 8,807-title catalog, used window functions for cohort analysis, and built an 11-view Streamlit dashboard. I can do this on your warehouse on day one.

### Metrics Grid

| 8,807 titles | 6,131 movies (69.6%) / 2,676 TV shows (30.4%) | 36.8% US concentration | 4.4-year avg lifecycle |
|---|---|---|---|
| 14.2% International Movies | TV-MA = 36.4% | Peak 2019: 1,999 titles added | 11 dashboard views |
| **+438 TMDB live records** | Trending, top-rated, upcoming | 19 genre popularity scores | Updated 2026-05-21 |

**Peak insight:** Netflix's catalog is 70% movies but TV shows turn around faster — if you're still licensing movies on a 5-year horizon, you're bleeding speed.

### Key Figures

<p align="center">
  <img src="https://raw.githubusercontent.com/gosidehustlesisi/sierra-business-intelligence/main/projects/netflix-content-strategy-intelligence/figures/01_content_mix.png" width="45%" alt="Content Mix">
  <img src="https://raw.githubusercontent.com/gosidehustlesisi/sierra-business-intelligence/main/projects/netflix-content-strategy-intelligence/figures/03_quality_sunburst.png" width="45%" alt="Quality Sunburst">
</p>

> **Peak insight — Content Mix:** Movies dominate at 69.6%, but the TV show pipeline is 2.5× faster — a strategic pivot signal for acquisition teams.

<p align="center">
  <img src="https://raw.githubusercontent.com/gosidehustlesisi/sierra-business-intelligence/main/projects/netflix-content-strategy-intelligence/figures/03_genre_treemap.png" width="70%" alt="Genre Treemap">
</p>

> **Peak insight — Genre Landscape:** Drama and Comedy hold volume, but International Movies at 14.2% represent the largest untapped expansion opportunity.

### How We Got There

DuckDB in-memory analytics on Kaggle's Netflix dataset **augmented with live TMDB API data** (trending movies, popular TV, top-rated, upcoming releases, genre popularity via `/discover/movie`). Window functions for release-to-platform gap analysis. SQL `UNNEST` for multi-value genre/country parsing. Matplotlib/Seaborn for 8 output visualizations + Plotly for 5 interactive HTML exports. Streamlit dashboard with 11 chart definitions including portfolio overview, regional heatmap, genre opportunity scoring, and acquisition timeline. **Live data fetcher:** `fetch_tmdb_data.py` pulls 438 records on demand via authenticated TMDB API.

### Notebook

📓 [`notebooks/03_executive_dashboard.ipynb`](projects/netflix-content-strategy-intelligence/notebooks/03_executive_dashboard.ipynb) — Interactive Plotly executive dashboard

### What I'd Bring to Your Team

The ability to translate raw catalog data into acquisition strategy without waiting for a data engineering pipeline. I write the SQL, build the dashboard, and tell you what it means for the budget.

---

## Project 2: Amazon Review Intelligence

<p>
  <img src="https://img.shields.io/badge/Source-UCSD%20Amazon%20Reviews-blue" alt="UCSD">
  <img src="https://img.shields.io/badge/SQL-pandas%20%2B%20DuckDB-yellow" alt="DuckDB">
  <img src="https://img.shields.io/badge/Dashboard-Streamlit-ff4b4b" alt="Streamlit">
</p>

### What This Means for Business

Customer sentiment and product quality signals extracted from 67,325 real Amazon Electronics reviews (1999–2014). I found that 59.5% of reviews are 5-star, but 1-star reviews are 16% longer on average (642 vs. 553 characters) — angry customers write more. Long reviews achieve 91% helpfulness vs. 78% for short ones. These are actionable signals for product teams and customer success.

### Why This Matters to Hiring Managers

I built a full pipeline from raw 495MB JSON.gz to cleaned CSV, ran 10 business SQL queries in SQLite/DuckDB, and produced a 6-view Streamlit dashboard. I ingest messy semi-structured data, clean it, and turn it into product decisions.

### Metrics Grid

| 67,325 reviews | 27,832 unique products | 53,609 unique reviewers | 4.22 ★ avg rating |
|---|---|---|---|
| 83.7% helpfulness rate | 59.5% five-star | Median 345 chars | 1★ = 642 chars, 5★ = 553 chars |

**Peak insight:** Your happiest customers are brief; your angriest are verbose and get the most engagement. Product teams should watch review length, not just stars.

### Key Figures

<p align="center">
  <img src="https://raw.githubusercontent.com/gosidehustlesisi/sierra-business-intelligence/main/projects/amazon-product-customer-intelligence/figures/figure_001_rating_distribution.png" width="45%" alt="Rating Distribution">
  <img src="https://raw.githubusercontent.com/gosidehustlesisi/sierra-business-intelligence/main/projects/amazon-product-customer-intelligence/figures/figure_002_monthly_volume.png" width="45%" alt="Monthly Volume">
</p>

> **Peak insight — Rating Distribution:** 59.5% five-star dominance with a long tail of critical detail. The volume of negative sentiment is small but disproportionately informative.

<p align="center">
  <img src="https://raw.githubusercontent.com/gosidehustlesisi/sierra-business-intelligence/main/projects/amazon-product-customer-intelligence/figures/figure_005_helpfulness_by_length.png" width="70%" alt="Helpfulness by Length">
</p>

> **Peak insight — Helpfulness Gradient:** Long reviews (500+ chars) achieve 91% helpfulness vs. 78% for short reviews. Detail drives perceived value.

### How We Got There

Automated pipeline fetching `reviews_Electronics_5.json.gz` from Stanford SNAP, streaming with uniform 1/13 sampling (seed=42), extracting helpfulness arrays into `helpful_upvotes` / `helpful_total` columns. DuckDB in-memory for 10 business SQL queries including brand performance ranking, rating distribution by year, helpfulness leaderboard, review length vs. rating correlation, seasonal pattern analysis, reviewer loyalty distribution, summary usage by rating, and product lifecycle tracking. Matplotlib/Seaborn for EDA, Plotly for interactive executive dashboards. Streamlit dashboard with 12 chart definitions including product leaderboard, rating evolution, review length distribution, helpfulness trends, reviewer loyalty, and rating-length correlation.

### Notebook

📓 [`notebooks/01_exploratory_analysis.ipynb`](projects/amazon-product-customer-intelligence/notebooks/01_exploratory_analysis.ipynb) — EDA on 67K real reviews  
📓 [`notebooks/02_review_analytics_sql.ipynb`](projects/amazon-product-customer-intelligence/notebooks/02_review_analytics_sql.ipynb) — 10 SQL-style business queries  
📓 [`notebooks/03_executive_dashboard.ipynb`](projects/amazon-product-customer-intelligence/notebooks/03_executive_dashboard.ipynb) — Plotly interactive visualizations

### What I'd Bring to Your Team

End-to-end data pipeline skills — from ingestion to executive dashboard — on real, messy e-commerce data. I spot the product-quality signals that CS teams miss.

---

## Project 3: Google Search Trends Market Intelligence

<p>
  <img src="https://img.shields.io/badge/Source-Google%20Trends%20API-blue" alt="Google Trends">
  <img src="https://img.shields.io/badge/SQL-pandasql-lightgrey" alt="pandasql">
  <img src="https://img.shields.io/badge/Dashboard-Streamlit-ff4b4b" alt="Streamlit">
</p>

### What This Means for Business

Real-time market interest tracking across 14 keywords over 262 weeks. I captured 1,923 trend records spanning worldwide, US national, and US regional granularity. This is competitive intelligence infrastructure: knowing when "AI" spikes, when "Netflix" softens, and where regional interest concentrates before your competitors do.

### Why This Matters to Hiring Managers

I built a live-data pipeline using pytrends and BigQuery, handled multi-granularity time-series alignment, and produced correlation heatmaps and peak-detection alerts. I can build your market intelligence stack.

### Metrics Grid

| 1,923 trend records | 262 weeks × 14 keywords | 714 US regional data points | 5-year window (2021–2026) |
|---|---|---|---|
| Worldwide + US + Regional + Top/Rising queries | Peak detection via `scipy.signal.find_peaks` | Cross-keyword correlation matrix | Plotly geospatial choropleth |

**Peak insight:** Search interest is a leading indicator. I built the infrastructure to catch the spike before your competitors do.

### Key Figures

<p align="center">
  <img src="https://raw.githubusercontent.com/gosidehustlesisi/sierra-business-intelligence/main/projects/google-search-trends-market-intelligence/figures/01_exploratory_analysis_figure_001.png" width="45%" alt="Trend Lines">
  <img src="https://raw.githubusercontent.com/gosidehustlesisi/sierra-business-intelligence/main/projects/google-search-trends-market-intelligence/figures/01_exploratory_analysis_figure_002.png" width="45%" alt="Correlation Heatmap">
</p>

> **Peak insight — Trend Leaders:** Amazon sustains a 72.0 baseline, but AI surged +70.7% YoY — the search-intelligence pipeline caught the breakout in real time.

<p align="center">
  <img src="https://raw.githubusercontent.com/gosidehustlesisi/sierra-business-intelligence/main/projects/google-search-trends-market-intelligence/figures/03_executive_dashboard_figure_001.png" width="70%" alt="Executive Dashboard">
</p>

> **Peak insight — YoY Winners:** AI (+70.7%), inflation (+68.9%), and mental health (+62.5%) are the three breakouts — two of which your competitors probably missed.

### How We Got There

pytrends API for live Google Trends extraction with 14 keywords across Tech, Health, and Finance. BigQuery for storage and retrieval. Pandas for multi-granularity time-series alignment (worldwide, US, regional). Plotly for interactive multi-line charts, correlation heatmaps, and US choropleth maps. Scipy peak detection for trend breakout alerts. Streamlit dashboard with 4 executive views.

### Notebook

📓 [`notebooks/03_executive_dashboard.ipynb`](projects/google-search-trends-market-intelligence/notebooks/03_executive_dashboard.ipynb) — Executive trend explorer with breakout alerts

### What I'd Bring to Your Team

I can build your competitive intelligence pipeline — live data ingestion, automated alerting, and stakeholder-ready visualizations — without waiting for a dedicated BI team.

---

## Data Provenance & Citations

| Project | Primary Source | Method | Records | Citation / URL |
|---|---|---|---|---|
| **Netflix Content Strategy** | Kaggle — Netflix Movies & TV Shows | Direct CSV download | 8,807 titles | [Shivam Bansal, CC0](https://www.kaggle.com/datasets/shivamb/netflix-shows) |
| **Amazon Review Intelligence** | UCSD Julian McAuley — Amazon Reviews (Electronics 5-core) | JSON.gz stream, 1/13 sample | 67,325 reviews | [Ni, Li & McAuley, EMNLP 2019](http://jmcauley.ucsd.edu/data/amazon/) |
| **Google Search Trends** | Google Trends via pytrends | Live API, weekly granularity | 1,923 records | [Google Trends](https://trends.google.com) |

**Zero synthetic data. Zero `generate_data.py`. Every metric was computed on real data.**

---

## Quick Start

```bash
# Clone the repo
git clone https://github.com/gosidehustlesisi/sierra-business-intelligence.git
cd sierra-business-intelligence

# Install dependencies
pip install -r requirements.txt

# --- Netflix Content Strategy ---
cd projects/netflix-content-strategy-intelligence
python fetch_tmdb_data.py    # or python fallback_data.py
jupyter lab notebooks/
streamlit run dashboard.py

# --- Amazon Review Intelligence ---
cd projects/amazon-product-customer-intelligence
python fetch_amazon_data.py
jupyter lab notebooks/
streamlit run dashboard.py

# --- Google Search Trends ---
cd projects/google-search-trends-market-intelligence
python fetch_trends_data.py
python clean_data.py
jupyter lab notebooks/
streamlit run dashboard.py
```

---

## Project Structure

```
sierra-business-intelligence/
├── projects/
│   ├── netflix-content-strategy-intelligence/
│   │   ├── data/                # Real CSVs (not synthetic)
│   │   ├── figures/             # 17+ matplotlib/plotly outputs
│   │   ├── notebooks/
│   │   │   ├── 01_exploratory_analysis.ipynb
│   │   │   ├── 02_content_intelligence_sql.ipynb
│   │   │   └── 03_executive_dashboard.ipynb
│   │   ├── dashboard.py         # Streamlit app
│   │   ├── fetch_tmdb_data.py   # Live TMDB fetcher
│   │   ├── fallback_data.py     # Netflix → TMDB schema
│   │   └── requirements.txt
│   │
│   ├── amazon-product-customer-intelligence/
│   │   ├── data/                # Real UCSD review CSV
│   │   ├── figures/             # 21+ chart outputs
│   │   ├── notebooks/
│   │   │   ├── 01_exploratory_analysis.ipynb
│   │   │   ├── 02_review_analytics_sql.ipynb
│   │   │   └── 03_executive_dashboard.ipynb
│   │   ├── dashboard.py         # Streamlit review dashboard
│   │   ├── fetch_amazon_data.py # UCSD pipeline
│   │   └── requirements.txt
│   │
│   └── google-search-trends-market-intelligence/
│       ├── data/                # Real pytrends CSVs
│       ├── figures/             # 11+ chart outputs
│       ├── notebooks/
│       │   ├── 01_exploratory_analysis.ipynb
│       │   ├── 02_market_intelligence_sql.ipynb
│       │   └── 03_executive_dashboard.ipynb
│       ├── dashboard.py         # Streamlit app
│       ├── fetch_trends_data.py # pytrends fetcher
│       └── requirements.txt
│
├── avatar.png
├── logo.png
├── README.md
└── LICENSE
```

---

## Requirements

```bash
pip install pandas numpy matplotlib seaborn plotly duckdb streamlit requests pytrends scipy scikit-learn
```

Each project has its own `requirements.txt` for granular dependencies.

---

## Contact

| Platform | URL |
|---|---|
| 🌐 **Portfolio** | [e3-ai.com](https://e3-ai.com) |
| 🐙 **GitHub** | [github.com/gosidehustlesisi](https://github.com/gosidehustlesisi) |
| 💼 **LinkedIn** | [linkedin.com/in/sierran](https://linkedin.com/in/sierran) |
| 🏢 **Company** | [e3-ai.com](https://e3-ai.com) |

---

**Built by:** Sierra Napier (evo3 / e3-ai)  
**License:** Data follows original source terms. Code: MIT.
