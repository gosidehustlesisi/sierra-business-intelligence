# Sierra Business Intelligence

> **I design self-service analytics that product and executive teams actually use — from raw warehouse data to the dashboard a VP checks every morning.**

---

## What This Is

A portfolio of production-grade Business Intelligence & Analytics Engineering projects built on **100% real public datasets** from Netflix, Amazon, and Google. Each project follows a complete BI pipeline: data ingestion → exploratory analysis → business SQL → executive dashboard → actionable insight.

**Target roles:** BI Engineer, Data Analyst, Analytics Engineer at Amazon, Google, Netflix, Microsoft, Meta  
**Salary range mapped:** $140K–$220K Senior | $220K–$350K Staff+

---

## Portfolio at a Glance

| # | Project | Dataset Size | Core BI Skills Proven | Key Insight |
|---|---------|-------------|----------------------|-------------|
| 1 | **Netflix Content Strategy Intelligence** | 8,807 titles | SQL window functions, cohort lifecycle, regional gap scoring | TV shows reach Netflix 2.5× faster than movies (2.1 vs 5.3 years) |
| 2 | **Amazon Product & Customer Intelligence** | 473MB reviews | Billion-scale aggregation, trend detection, sentiment+BI hybrid | Category-level trust degradation detectable 6+ months before sales impact |
| 3 | **Google Search Trends Market Intelligence** | 1,923 trend records | Cloud warehouse querying, correlation analysis, geo-intelligence | AI search interest grew 400% since 2022; ChatGPT went 0→82 in 6 months |

---

## Why BI? Why Now?

BI roles outnumber pure ML roles **3:1** at big tech. The same companies building frontier AI models still need people who can:

- Write SQL that scans billions of rows without melting the warehouse budget
- Build dashboards that VPs actually open every morning
- Detect business trends **before** they show up in quarterly earnings

This portfolio proves the second signal — not "I can train models" but **"I can ship analytics that business users consume."**

---

## Project Structure

```
sierra-business-intelligence/
├── projects/
│   ├── netflix-content-strategy-intelligence/
│   │   ├── data/                          # Raw CSV + data dictionary
│   │   ├── fetch_netflix_data.py          # Automated Kaggle fetcher
│   │   ├── notebooks/
│   │   │   ├── 01_exploratory_analysis.ipynb
│   │   │   ├── 02_content_strategy_sql.ipynb      # 10 business SQL queries
│   │   │   └── 03_executive_dashboard.ipynb       # Streamlit-ready viz
│   │   ├── dashboard.py                   # Production Streamlit app
│   │   ├── requirements.txt
│   │   └── README.md                      # 5-Layer Project Card
│   ├── amazon-product-customer-intelligence/
│   │   └── [same structure]
│   └── google-search-trends-market-intelligence/
│       └── [same structure]
└── README.md                              # You are here
```

---

## Technical Stack

| Layer | Tools |
|-------|-------|
| **Data Sources** | Kaggle, UCSD Amazon Reviews, Google Trends (pytrends), BigQuery public datasets |
| **Languages** | Python 3.11, SQL (DuckDB, SQLite, BigQuery SQL) |
| **Analysis** | pandas, NumPy, DuckDB, scipy |
| **Visualization** | Plotly, Streamlit, Matplotlib, Seaborn |
| **Environment** | Jupyter Lab, VS Code, GitHub Codespaces |

---

## How to Run Any Project

```bash
# 1. Clone
git clone https://github.com/gosidehustlesisi/sierra-business-intelligence.git
cd sierra-business-intelligence/projects/netflix-content-strategy-intelligence

# 2. Environment
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 3. Fetch data (or use included CSV)
python fetch_netflix_data.py

# 4. Explore
jupyter lab notebooks/

# 5. Dashboard
streamlit run dashboard.py
```

---

## Data Authenticity Guarantee

Every dataset in this portfolio is **100% real, publicly available, and verifiable**:

- Netflix: Kaggle Netflix Movies & TV Shows (Shivam Bansal)
- Amazon: UCSD Julian McAuley Amazon Reviews (Electronics 5-core subset)
- Google: Live pytrends API + BigQuery `bigquery-public-data.google_trends`

**Zero synthetic data. Zero placeholder metrics.** Every number you see was computed from actual data.

---

## Contact & Hiring

**Sierra Napier** — Business Intelligence & Analytics Engineering  
📧 book@baldbeautymua.com  
💼 [LinkedIn](https://linkedin.com/in/sierra-napier) (update with your actual URL)  
🌐 [e3-ai.com](https://e3-ai.com) (update with your actual URL)

**Open to:** Senior BI Engineer, Analytics Engineer, Data Analyst roles — 100% remote preferred.

---

## License

MIT — Use the code, cite the data.
