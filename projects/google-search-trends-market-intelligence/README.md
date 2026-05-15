# Google Search Trends — Market Intelligence

> **Real-world search-intelligence pipeline** using live Google Trends data (pytrends).  
> 14 keywords · 5 years · worldwide + US regional · zero synthetic data.

---

## 🏗️ 5-Layer Project Card

| Layer | What It Is | Key Files |
|-------|-----------|-----------|
| **L1 — Data** | Raw fetched CSVs + data dictionary | `data/*.csv`, `data/data_dictionary.md` |
| **L2 — Ingestion** | Automated pytrends fetcher with rate-limiting | `fetch_trends_data.py` |
| **L3 — Analytics** | 3 executed notebooks: EDA, 10 SQL queries, executive dashboard | `notebooks/01_*`, `02_*`, `03_*` |
| **L4 — App** | Streamlit interactive dashboard | `dashboard.py` |
| **L5 — Narrative** | README + data dictionary (this file) | `README.md`, `data_dictionary.md` |

---

## 📊 Real Findings (from live data, May 2021 – May 2026)

### Search-Interest Leaders (5-Year Average)
1. **Amazon** — 75.0 (sustained baseline leader)
2. **crypto** — 34.4 (volatile but persistently high)
3. **Netflix** — 31.4 (steady entertainment demand)
4. **AI** — 28.1 (accelerating since 2023)
5. **ChatGPT** — 25.9 (explosive entry in 2023, stabilizing)

### YoY Growth Winners (Last 52 Weeks vs Prior)
| Topic | YoY Growth |
|-------|-----------|
| **inflation** | +96.3% |
| **AI** | +91.9% |
| **ChatGPT** | +81.5% |
| **mental health** | +68.3% |
| **crypto** | +44.9% |

### Key Trend Patterns
- **AI search interest grew ~400% since 2022**, peaking in Q1 2023 coinciding with ChatGPT launch. It has since stabilized at a permanently elevated plateau (~80–100) vs pre-2023 baseline (~5–15).
- **ChatGPT** went from 0 to peak 82 in under 6 months (Nov 2022 – May 2023), one of the fastest breakout events in the dataset.
- **inflation** and **recession** are strongly correlated (r ≈ 0.75) and both spiked during 2022 macro uncertainty.
- **crypto** and **Bitcoin** move together (r ≈ 0.82) but with crypto having ~5× the baseline search volume.
- **Netflix** shows slow decline (-1.5% YoY) suggesting category maturation or competition erosion.
- **mental health** is quietly accelerating (+68% YoY) with low absolute volume, indicating an early-growth niche.
- **Tesla** and **machine learning** are flat-to-slow-growth, suggesting these topics have passed peak novelty and entered steady-state awareness.

---

## 🗂️ Repository Structure

```
google-search-trends-market-intelligence/
├── data/
│   ├── interest_over_time_worldwide.csv      # 262 rows × 14 keywords
│   ├── interest_over_time_us.csv               # 262 rows × 14 keywords
│   ├── interest_by_region_us.csv               # 714 rows (states × keywords)
│   ├── related_queries_top.csv               # 345 rows
│   ├── related_queries_rising.csv            # 340 rows
│   └── data_dictionary.md
├── notebooks/
│   ├── 01_exploratory_analysis.ipynb           # EDA: peaks, correlations, maps
│   ├── 02_market_intelligence_sql.ipynb        # 10 business SQL queries
│   └── 03_executive_dashboard.ipynb            # Streamlit-ready: explorer, alerts, forecast
├── fetch_trends_data.py                       # Automated pytrends fetcher
├── clean_data.py                              # Data cleaning / tidying
├── build_notebooks.py                         # Notebook generation + execution
├── dashboard.py                               # Streamlit app
├── requirements.txt
└── README.md                                  # This file
```

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Fetch fresh data (optional — data already included)
python fetch_trends_data.py
python clean_data.py

# 3. Launch Streamlit dashboard
streamlit run dashboard.py

# 4. Open notebooks
jupyter lab notebooks/
```

---

## 📈 Notebook Highlights

### 01 — Exploratory Analysis
- Multi-category time-series visualization (Tech / Health / Finance)
- Peak detection with `scipy.signal.find_peaks`
- Full correlation matrix (Plotly heatmap)
- YoY growth rate bar chart
- US choropleth map (animated by keyword)
- Category summary statistics

### 02 — Market Intelligence: 10 Business SQL Queries
Executed with `pandasql` on in-memory real data:

| # | Query | Business Value |
|---|-------|---------------|
| 1 | Topic ranking by volume & growth | Prioritize content/marketing spend |
| 2 | Regional interest heatmap | Geo-targeted campaigns |
| 3 | Emerging topics (>100% YoY) | Spot breakout niches early |
| 4 | Trend correlation matrix | Cross-promotion & bundling |
| 5 | Seasonal pattern detection | Calendar-based campaign timing |
| 6 | Event-driven spike analysis | News-jacking opportunity |
| 7 | Category lifecycle detection | Portfolio rebalancing |
| 8 | Cross-category opportunity | Low-competition, high-growth niches |
| 9 | Interest forecasting | Budget & capacity planning |
| 10 | Geographic arbitrage | Region-specific product launches |

### 03 — Executive Dashboard
- **Trend Explorer:** Multi-select time series with hover tooltips
- **Regional Map:** US state choropleth with top-10 table
- **Breakout Alerts:** Rising related queries by parent keyword
- **Forecast Panel:** 1-year linear projection with trend direction
- **Category Scorecard:** Tech vs Health vs Finance performance

---

## 🧮 Data Source & Methodology

- **Primary source:** [Google Trends](https://trends.google.com) via [`pytrends`](https://github.com/GeneralMills/pytrends) (live API, no key required)
- **BigQuery reference:** `bigquery-public-data.google_trends` — schema validated against this public dataset
- **Fetch date:** 2026-05-15
- **Keywords:** 14 topics across Tech (7), Health (3), Finance (4)
- **Timeframe:** `today 5-y` (weekly granularity, 262 weeks)
- **Geos:** Worldwide + US nationwide + US by state
- **Rate limiting:** 1.5–2s delays between API calls
- **Data quality:** 100% real — zero synthetic or simulated values

---

## 🛠️ Tech Stack

| Component | Tool |
|-----------|------|
| Data fetch | `pytrends` |
| Analysis | `pandas`, `numpy`, `scipy`, `scikit-learn` |
| SQL | `pandasql` (SQLite backend on DataFrames) |
| Visualization | `plotly` |
| Dashboard | `streamlit` |
| Notebook execution | `nbformat` + `nbconvert` + `ipykernel` |

---

## 👤 Author

**Sierra Napier** — Founder, e3-ai.com  
Data Scientist · AI Architect · Performance Analytics & Visualization

---

*Part of the [sierra-business-intelligence](https://github.com/gosidehustlesisi/sierra-business-intelligence) portfolio.*
