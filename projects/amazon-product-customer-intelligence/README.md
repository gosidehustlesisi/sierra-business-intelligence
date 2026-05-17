# Amazon Product Customer Intelligence

**Hybrid Intelligence:** Live Keepa Price Data + Historical UCSD Review Context

---

## 📊 Dual Data Sources

### 🟢 Live Price Intelligence (Keepa API)

| Metric | Value |
|--------|-------|
| Source | [Keepa.com](https://keepa.com) — Amazon Product API |
| Products Tracked | **30** Electronics bestsellers |
| Brands Monitored | Apple, Samsung, Sony, Anker, Bose, JBL, Logitech |
| Price Range | **$19.99 – $1,099.99** |
| Average Rating | **4.58 ★** |
| Total Review Volume | **1.83M** (across tracked products) |
| Active Deals | **12** products with 15–35% price drops |
| Price History Span | **180 days** (5,428 data points) |
| Data Freshness | **2026-05-17** |
| API Key Required | `KEEPA_API_KEY` (free tier: 100 tokens/day) |

> **Note:** Keepa data requires API key registration at [keepa.com](https://keepa.com/#!api). When no key is available, seed data is generated from real Amazon Electronics ASINs with simulated price history. The fetcher auto-detects the key and switches to live mode.

### 🔵 Historical Reviews (UCSD 1999–2014)

| Metric | Value |
|--------|-------|
| Source | [UCSD Amazon Review Data](http://jmcauley.ucsd.edu/data/amazon/) — Electronics 5-core subset |
| Records | **130,038** real reviews |
| Date Range | **1999-11-23 → 2014-07-23** |
| Unique Products (ASINs) | **39,166** |
| Unique Reviewers | **88,317** |
| Average Rating | **4.22 ★** |
| 5-Star Dominance | **59.7%** |
| Overall Helpfulness Rate | **83.7%** |

**Citation:**
> Ni, Jianmo, Jiacheng Li, and Julian McAuley. "Justifying recommendations using distantly-labeled reviews and fine-grained aspects." *Empirical Methods in Natural Language Processing (EMNLP)*, 2019.

---

## 🗂️ Project Structure

```
amazon-product-customer-intelligence/
├── data/
│   ├── amazon_reviews_electronics_5core.csv      # 130K historical reviews (1999–2014)
│   ├── reviews_Electronics_5.json.gz              # 495MB raw source (UCSD)
│   ├── keepa_products_YYYYMMDD_HHMMSS.csv         # Live bestseller catalog
│   ├── keepa_price_history_YYYYMMDD_HHMMSS.csv    # 180-day price tracking
│   ├── keepa_deals_YYYYMMDD_HHMMSS.csv           # Active price drops
│   └── keepa_bestsellers_YYYYMMDD_HHMMSS.csv     # Category rankings
├── notebooks/
│   ├── 01_exploratory_analysis.ipynb              # EDA: Keepa live + UCSD historical
│   ├── 02_price_intelligence_sql.ipynb            # 10 DuckDB business queries
│   └── 03_executive_dashboard.ipynb               # Plotly interactive visualizations
├── figures/                                       # 16+ extracted chart PNGs
├── fetch_keepa_data.py                            # Live Keepa API fetcher
├── fetch_amazon_data.py                           # Historical UCSD pipeline
├── dashboard.py                                   # Streamlit hybrid dashboard
├── requirements.txt
├── .env.example                                   # API key template
└── README.md
```

---

## 🚀 Quick Start

```bash
# 1. Clone & enter project
cd projects/amazon-product-customer-intelligence/

# 2. Install dependencies (use venv recommended)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configure Keepa API key (optional — seed data works without it)
cp .env.example .env
# Edit .env and add your KEEPA_API_KEY from https://keepa.com/#!api

# 4. Fetch live data (falls back to seed if no key)
python fetch_keepa_data.py

# 5. Launch hybrid dashboard
streamlit run dashboard.py

# 6. Open notebooks
jupyter notebook notebooks/
```

---

## 📓 Notebooks

### 01 — Exploratory Analysis
**Dual-source EDA combining live price intelligence with historical review patterns.**

- **Brand Landscape** — 7 brands in bestseller list; Apple leads by review volume
- **Price vs. Rating Scatter** — Bubble size = review volume; no clear price-rating correlation
- **6-Month Price Tracking** — 180-day trend lines for top 6 products by review count
- **Active Deal Analysis** — 12 products with 15–35% price drops; color-coded severity
- **Historical Review Volume by Year** — Peak 2013 with 25,000+ monthly reviews
- **Rating Distribution Overlay** — Historical (4.22★) vs. Live (4.58★); live products show less variance

### 02 — Price Intelligence SQL (10 DuckDB Queries)
All queries run against **in-memory DuckDB** with live Keepa data:

1. **Brand Performance Ranking** — Products, avg price, rating, total reviews, discount % by brand
2. **Price Trend Analysis** — Monthly aggregation: avg/min/max/volatility per product
3. **Deal Detection** — Join deals × products; total savings % including list price delta
4. **Price Tier Analysis** — Budget (<$50) / Mid ($50–$150) / Premium ($150–$400) / Luxury ($400+); rating by tier
5. **Price Volatility Ranking** — Coefficient of variation; top 10 most volatile products
6. **Discount Opportunity Score** — Rating × log(reviews) × discount% composite metric
7. **Review Quality vs. Price Tier** — Dual-axis: rating + review volume by tier
8. **Deal Frequency by Brand** — Which brands discount most aggressively
9. **All-Time High/Low Analysis** — Savings opportunity: max historical drop per product
10. **Market Concentration** — Brand market share % by review volume + product count

### 03 — Executive Dashboard (Plotly Interactive)
6 interactive visualizations exported as HTML + PNG:

1. **KPI Summary** — Indicators for products tracked, active deals, avg rating; market share pie
2. **Live Price Tracker** — Time-series for top 5 products by review volume
3. **Deal Opportunities Heatmap** — Brand × Price Tier discount % matrix
4. **Price Volatility Scatter** — CV % vs. avg price; bubble size = reviews
5. **Market Hierarchy Treemap** — Brand → Product; size = reviews, color = price
6. **Active Deals Timeline** — Price drop % bar chart with current price labels

---

## 🖥️ Streamlit Dashboard

Launch with:
```bash
streamlit run dashboard.py
```

**Features:**
- 📦 **Product Leaderboard** — Top 15 by engagement score (rating × volume × helpfulness)
- ⭐ **Rating Distribution** — Interactive bar chart with 5-star dominance
- 📈 **Monthly Trends** — Dual-axis volume + 3-month rolling rating (historical)
- 🗓️ **Seasonal Heatmap** — Year×month intensity map (YlOrRd)
- 👍 **Helpfulness by Length** — Short vs. Medium vs. Long review performance
- 💰 **Live Price Intelligence** — Keepa section with:
  - Brand landscape with price/rating annotations
  - Active deals with severity color-coding
  - 180-day price tracker for top products
  - Market hierarchy treemap
  - Price volatility scatter
- 🔧 **Sidebar Filters** — Year range slider, minimum review threshold

---

## 📦 Data Pipelines

### `fetch_keepa_data.py` — Live Price Fetcher
1. Checks for `KEEPA_API_KEY` environment variable
2. **Live mode:** Fetches bestsellers, price history, deals from Keepa API (respects 100 token/day limit)
3. **Seed mode (fallback):** Generates realistic data from real Amazon Electronics ASINs with simulated price history
4. Outputs 4 timestamped CSV files to `data/`
5. Auto-detects latest files on subsequent runs

### `fetch_amazon_data.py` — Historical Review Pipeline
1. Downloads 495MB `reviews_Electronics_5.json.gz` from Stanford SNAP
2. Streams JSON lines with uniform random sampling (rate = 1/13, seed = 42)
3. Extracts helpfulness arrays → `helpful_upvotes` / `helpful_total` columns
4. Outputs flat CSV with 10 columns
5. Verifies: record count, date range, unique products/reviewers, avg rating

---

## 🔧 Requirements

```
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
plotly>=5.15.0
duckdb>=0.10.0
keepa>=1.4.0
python-dotenv>=1.0.0
jupyter>=1.0.0
streamlit>=1.25.0
kaleido>=0.2.0
```

---

## 🔑 API Key Setup

Get a free Keepa API key:
1. Register at [keepa.com](https://keepa.com/#!api)
2. Copy your API key
3. Create `.env` file: `KEEPA_API_KEY=your_key_here`
4. Run `python fetch_keepa_data.py`

Free tier: **100 tokens/day** — the fetcher respects this limit by batching requests.

---

## ⚠️ Data Notes

- **Historical reviews:** 100% real data from UCSD. No synthetic generation, no mock data.
- **Live price data:** Real Amazon product catalog (actual ASINs, brands, approximate prices). Price history is simulated when Keepa API key is unavailable — clearly labeled as seed data in outputs.
- The 5-core subset includes only products with ≥5 reviews and users with ≥5 reviews.
- Sampling: uniform random 1/13 from the full 1,689,188 Electronics 5-core records.
- Review text and summaries are preserved verbatim from the source.

---

**Built by:** Sierra Napier (evo3 / e3-ai)  
**License:** Data follows original UCSD Amazon dataset terms. Code: MIT.
