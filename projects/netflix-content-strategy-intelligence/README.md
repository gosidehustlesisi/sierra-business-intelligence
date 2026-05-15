# Netflix Content Strategy Intelligence

> **TL;DR:** End-to-end analysis of 8,807 Netflix titles revealing a 70/30 movie-to-TV split, 4.4-year average content lifecycle, and a 36.8% US concentration that signals emerging market whitespace.

---

## Business Question

How is Netflix's content portfolio structured across type, geography, genre, and time — and where are the strategic gaps for content acquisition and market expansion?

---

## What It Does

This project delivers a complete business intelligence suite for Netflix content strategy:

- **Exploratory Analysis:** Full EDA on 8,807 titles — content mix, ratings, countries, genres, duration, lifecycle
- **SQL Analytics:** 10 business-grade SQL queries (DuckDB) answering strategic questions from type distribution to emerging market opportunity scoring
- **Executive Dashboard:** Interactive Plotly visualizations for portfolio overview, regional heatmaps, genre opportunity matrices, and gap analysis
- **Streamlit App:** Production-ready dashboard (`dashboard.py`) with 6 views: Executive Summary, Content Mix, Regional Analysis, Genre Breakdown, Acquisition Timeline, Content Gaps
- **Automated Fetcher:** `fetch_netflix_data.py` pulls fresh data directly from Kaggle via `kagglehub`

---

## How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Fetch data (or use included CSV)
python fetch_netflix_data.py

# 3. Run notebooks
jupyter lab notebooks/

# 4. Launch Streamlit dashboard
streamlit run dashboard.py
```

---

## Key Insights

- **Content Mix:** Netflix catalog is movie-weighted at 69.6% movies vs 30.4% TV shows, but TV acquisition has accelerated since 2019 (29.7% of 2021 additions)
- **Geographic Concentration:** United States produces 36.8% of catalog titles, followed by India (10.4%) and UK (8.0%). 74 countries have below-average representation, representing expansion whitespace
- **Content Lifecycle:** Movies take 5.3 years on average from theatrical release to Netflix; TV shows only 2.1 years — Netflix prioritizes fresher serialized content
- **Audience Positioning:** 36.4% of content is TV-MA (mature), with 70.9% of total catalog targeting teen+ demographics — Netflix leans adult, not family
- **Genre Strategy:** "International Movies" is the #1 category at 14.2% market share, followed by Dramas (12.6%) — Netflix's global content strategy over US-centric programming is measurable in the data

---

## Technical Stack

| Layer | Tool |
|-------|------|
| Data Source | Kaggle Netflix Movies & TV Shows (8,807 records) |
| Language | Python 3.12 |
| Data Processing | pandas, numpy |
| SQL Analytics | DuckDB (in-memory) |
| Visualization | matplotlib, seaborn, plotly |
| Dashboard | Streamlit |
| Notebooks | Jupyter Lab |
| Data Fetch | kagglehub |

---

## Data Source

**Kaggle — Netflix Movies and TV Shows**  
Author: Shivam Bansal  
URL: https://www.kaggle.com/datasets/shivamb/netflix-shows  
License: CC0: Public Domain  
Records: 8,807 titles | Columns: 12 | Updated: 2021

---

## Project Structure

```
netflix-content-strategy-intelligence/
├── data/
│   ├── netflix_titles.csv          # Raw dataset (8,807 records)
│   └── data_dictionary.md          # Field definitions & quality notes
├── notebooks/
│   ├── 01_exploratory_analysis.ipynb    # Full EDA with visualizations
│   ├── 02_content_strategy_sql.ipynb  # 10 business SQL queries
│   └── 03_executive_dashboard.ipynb   # Interactive Plotly charts
├── output/                         # Generated charts & HTML exports
├── dashboard.py                    # Streamlit production dashboard
├── fetch_netflix_data.py           # Kaggle automated fetcher
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```
