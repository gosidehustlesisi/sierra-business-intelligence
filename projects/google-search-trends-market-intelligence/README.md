# Google Search Trends — Market Intelligence

> **Real-world search-intelligence pipeline** using live Google Trends data (pytrends).  
> 14 keywords · 5 years · worldwide + US regional · zero synthetic data.  
> **Last refreshed:** 2026-05-17 — all data re-fetched and notebooks re-executed.

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
1. **Amazon** — 72.0 (sustained baseline leader)
2. **crypto** — 37.0 (volatile but persistently high)
3. **Netflix** — 30.3 (steady entertainment demand)
4. **AI** — 28.8 (accelerating since 2023)
5. **ChatGPT** — 26.6 (explosive entry in 2023, stabilizing)

### YoY Growth Winners (Last 52 Weeks vs Prior)
| Topic | YoY Growth |
|-------|-----------|
| **AI** | +70.7% |
| **inflation** | +68.9% |
| **mental health** | +62.5% |
| **crypto** | +50.5% |
| **machine learning** | +50.0% |

### YoY Decliners
| Topic | YoY Change |
|-------|-----------|
| **Bitcoin** | −21.7% |
| **recession** | −7.1% |
| **Amazon** | −5.7% |
| **ChatGPT** | −0.4% |
| **Tesla** | +4.2% |

### Key Trend Patterns
- **AI** remains the dominant search topic with current interest at 67 (week of 2026-05-17), up +70.7% YoY. AI and ChatGPT are tightly correlated (r ≈ 0.96), confirming they move as a single conversational cluster.
- **ChatGPT** has stabilized at ~50–60 after its 2023 peak (82), down slightly (−0.4% YoY) but maintaining a permanently elevated plateau vs pre-launch baseline.
- **inflation** surged +68.9% YoY and hit an all-time high of 41 in early 2025, now cooling to 14 but still elevated vs historical baseline.
- **crypto** rebounded +50.5% YoY with current interest at 41, decoupling somewhat from Bitcoin (−21.7% YoY) — suggesting retail interest in "crypto" as a category exceeds specific asset curiosity.
- **mental health** is the quiet breakout: +62.5% YoY with low absolute volume (current: 2), indicating an early-growth niche with compounding potential.
- **Netflix** and **Amazon** are both flat-to-slow-decline (−5.7% for Amazon, +4.8% for Netflix), suggesting category maturation or competition erosion in streaming/e-commerce.
- **Tesla** is flat (+4.2% YoY) at low absolute interest (5), suggesting the topic has passed peak novelty and entered steady-state awareness.
- **recession** searches are down −7.1% YoY and decoupled from inflation (r ≈ 0.39 vs historical 0.75), indicating public concern has shifted from macro fears to specific price pressures.

---

## 🗂️ Repository Structure

```
google-search-trends-market-intelligence/
├── data/
│   ├── interest_over_time_worldwide.csv      # 262 rows × 14 keywords
│   ├── interest_over_time_us.csv               # 262 rows × 14 keywords
│   ├── interest_by_region_us.csv               # 714 rows (states × keywords)
│   ├── related_queries_top.csv               # 270 rows
│   ├── related_queries_rising.csv            # 263 rows
│   └── data_dictionary.md
├── notebooks/
│   ├── 01_exploratory_analysis.ipynb           # EDA: peaks, correlations, maps
│   ├── 02_market_intelligence_sql.ipynb        # 10 business SQL queries
│   └── 03_executive_dashboard.ipynb            # Streamlit-ready: explorer, alerts, forecast
├── figures/                                    # 7 static PNGs extracted from notebooks
├── fetch_trends_data.py                       # Automated pytrends fetcher
├── clean_data.py                              # Data cleaning / tidying
├── build_notebooks.py                         # Notebook generation + execution
├── dashboard.py                               # Streamlit app
├── requirements.txt
└── README.md                                  # This file
```

---

## Figure Gallery

### Search Trends Overview

![Search Interest](figures/01_exploratory_analysis_figure_001.png)
*AI is in its own category now — it's not "tech" anymore. Worldwide search interest shows AI's divergence from every other topic since 2023. This is structural growth, not a hype cycle.*

![YoY Growth](figures/01_exploratory_analysis_figure_004.png)
*Three stories in one chart: AI boom (+70.7%), inflation peak (+68.9% before cooling), mental health shift (+62.5%).*  

### Geographic & Breakout Intelligence

![Regional Map](figures/03_executive_dashboard_figure_002.png)
*California and New York drive tech-topic search — but the Midwest is catching up. US regional choropleth with state-level interest scores.*

![Breakout Alerts](figures/03_executive_dashboard_figure_003.png)
*Spot emerging trends before they hit headlines. "AI" spawns "AI art," "AI detector," "AI jobs" — early signals of where attention is migrating.*

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
- **Fetch date:** 2026-05-17 (data refreshed live via pytrends)
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

## 🔄 Data Refresh Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-05-17 | Full refresh via `fetch_trends_data.py` | Fresh pytrends data pulled; 3 notebooks re-executed; 7 figures extracted; README updated with current YoY metrics. 3 related-queries calls hit 429 rate-limit (recession, stock market, crypto). |

---

*Part of the [sierra-business-intelligence](https://github.com/gosidehustlesisi/sierra-business-intelligence) portfolio.*
