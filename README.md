# Sierra Business Intelligence

**78,055 real records · 3 projects · 9 notebooks · 49+ production charts**

---

> I analyze complex data at scale, architect AI systems that automate it, and visualize the story so stakeholders act on it.

---

## 🔒 Trust Badges

| Source | Verification | Records |
|---|---|---|
| **Kaggle** — Netflix Movies & TV Shows | Direct CSV download, SHA-verified | 8,807 titles |
| **UCSD Julian McAuley** — Amazon Reviews (Electronics 5-core) | Stanford SNAP JSON.gz → streamed 1/13 sample → CSV | 67,325 reviews |
| **Google Trends** — pytrends API + BigQuery | Live API extraction, weekly granularity | 1,923 trend records |

These aren't toy models. Every number below came from running real code on real data.

---

## Project 1: Netflix Content Strategy Intelligence

### What this means for your business

Content acquisition and portfolio management decisions backed by SQL-driven lifecycle analysis. I quantified that TV shows reach Netflix 2.5× faster than movies (2.1 vs. 5.3 years), identified US concentration at 36.8% of the catalog, and flagged International Movies as the top genre opportunity at 14.2% share. This is analysis that directly informs licensing budgets and regional expansion priorities.

### Why this matters to hiring managers

I wrote 10 business-facing SQL queries in DuckDB against a real 8,807-title catalog, used window functions for cohort analysis, and built an 11-view Streamlit dashboard. I can do this on your warehouse on day one.

### Metrics Grid

| 8,807 titles | 6,131 movies (69.6%) / 2,676 TV shows (30.4%) | 36.8% US concentration | 4.4-year avg lifecycle |
|---|---|---|---|
| 14.2% International Movies | TV-MA = 36.4% | Peak 2019: 1,999 titles added | 11 dashboard views |

### TL;DR

**Netflix's catalog is 70% movies but TV shows turn around faster—if you're still licensing movies on a 5-year horizon, you're bleeding speed.**

### How we got there

> DuckDB in-memory analytics on Kaggle's Netflix dataset. Window functions for release-to-platform gap analysis. SQL `UNNEST` for multi-value genre/country parsing. Matplotlib/Seaborn for 8 output visualizations + Plotly for 5 interactive HTML exports. Streamlit dashboard with 11 chart definitions including portfolio overview, regional heatmap, genre opportunity scoring, and acquisition timeline.

### What I'd bring to your team

The ability to translate raw catalog data into acquisition strategy without waiting for a data engineering pipeline. I write the SQL, build the dashboard, and tell you what it means for the budget.

---

## Project 2: Amazon Product & Customer Intelligence

### What this means for your business

Customer sentiment and product quality signals extracted from 67,325 real Amazon Electronics reviews. I found that 59.5% of reviews are 5-star, but 1-star reviews are 16% longer on average (642 vs. 553 characters)—angry customers write more. Reviews with 5+ helpfulness votes average 3.72 stars, suggesting critical reviews drive the most engagement. These are actionable signals for product teams and customer success.

### Why this matters to hiring managers

I built a full pipeline from raw 495MB JSON.gz to cleaned CSV, ran 10 business SQL queries in SQLite, and produced a 5-view Streamlit dashboard. I ingest messy semi-structured data, clean it, and turn it into product decisions.

### Metrics Grid

| 67,325 reviews | 27,832 unique products | 53,609 unique reviewers | 4.22 ★ avg rating |
|---|---|---|---|
| 83.8% helpfulness rate | 59.5% five-star | Median 344 chars | 5★ = 553 chars, 1★ = 642 chars |

### TL;DR

**Your happiest customers are brief; your angriest are verbose and get the most engagement. Product teams should watch review length, not just stars.**

### How we got there

> Automated pipeline fetching `reviews_Electronics_5.json.gz` from Stanford SNAP, streaming with uniform 1/13 sampling (seed=42), extracting helpfulness arrays into `helpful_upvotes` / `helpful_total` columns. SQLite in-memory for 10 business SQL queries including `ROW_NUMBER()` product lifecycle stages (Early/Growth/Mature), length bucketing (<200 / 200-500 / 500-1000 / 1000+ chars), and reviewer loyalty tiers (One-time / Casual / Loyal). Matplotlib/Seaborn for EDA, Streamlit for dashboard.

### What I'd bring to your team

End-to-end data pipeline skills—from ingestion to executive dashboard—on real, messy e-commerce data. I spot the product-quality signals that CS teams miss.

---

## Project 3: Google Search Trends Market Intelligence

### What this means for your business

Real-time market interest tracking across 14 keywords over 262 weeks. I captured 1,923 trend records spanning worldwide, US national, and US regional granularity. This is competitive intelligence infrastructure: knowing when "AI" spikes, when "Netflix" softens, and where regional interest concentrates before your competitors do.

### Why this matters to hiring managers

I built a live-data pipeline using pytrends and BigQuery, handled multi-granularity time-series alignment, and produced correlation heatmaps and peak-detection alerts. I can build your market intelligence stack.

### Metrics Grid

| 1,923 trend records | 262 weeks × 14 keywords | 714 US regional data points | 5-year window (2021–2026) |
|---|---|---|---|
| Worldwide + US + Regional + Top/Rising queries | Peak detection via `scipy.signal.find_peaks` | Cross-keyword correlation matrix | Plotly geospatial choropleth |

### TL;DR

**Search interest is a leading indicator. I built the infrastructure to catch the spike before your competitors do.**

### How we got there

> pytrends API for live Google Trends extraction with 14 keywords across Tech, Health, and Finance. BigQuery for storage and retrieval. Pandas for multi-granularity time-series alignment (worldwide, US, regional). Plotly for interactive multi-line charts, correlation heatmaps, and US choropleth maps. Scipy peak detection for trend breakout alerts. Streamlit dashboard with 4 executive views.

### What I'd bring to your team

I can build your competitive intelligence pipeline—live data ingestion, automated alerting, and stakeholder-ready visualizations—without waiting for a dedicated BI team.

---

## 📦 Deliverable Inventory

| Domain | Techniques | Real Data Source | Records | Status |
|---|---|---|---|---|
| Content Strategy Intelligence | SQL window functions, cohort lifecycle, regional gap scoring | Kaggle Netflix Movies & TV Shows | 8,807 | ✅ Complete |
| Product & Customer Intelligence | SQLite aggregation, sentiment proxy, trend detection | UCSD Amazon Reviews (Electronics 5-core) | 67,325 | ✅ Complete |
| Search Trends Market Intelligence | Correlation analysis, geo-intelligence, peak detection | Google Trends (pytrends API + BigQuery) | 1,923 | ✅ Complete |

---

**Built by:** Sierra Napier (evo3 / e3-ai)  
**License:** Data follows original source terms. Code: MIT.
