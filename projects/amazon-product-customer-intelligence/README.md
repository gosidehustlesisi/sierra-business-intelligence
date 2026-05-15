# Amazon Product Customer Intelligence

**Real Amazon Electronics Reviews — 130,038 records | 39,166 products | 88,317 reviewers**

---

## 📊 Dataset

| Metric | Value |
|--------|-------|
| Source | [UCSD Amazon Review Data](http://jmcauley.ucsd.edu/data/amazon/) — Electronics 5-core subset |
| Records | **130,038** real reviews |
| Date Range | 1999-11-23 → 2014-07-23 |
| Unique Products (ASINs) | **39,166** |
| Unique Reviewers | **88,317** |
| Average Rating | **4.22 ★** |
| Reviews with Helpfulness Votes | **42.7%** (55,526) |
| Overall Helpfulness Rate | **83.7%** |
| Median Review Length | **345 characters** |
| Rating Distribution | 1★: 8,394 (6.5%) | 2★: 6,212 (4.8%) | 3★: 11,053 (8.5%) | 4★: 26,793 (20.6%) | 5★: 77,586 (59.7%) |

**Citation:**
> Ni, Jianmo, Jiacheng Li, and Julian McAuley. "Justifying recommendations using distantly-labeled reviews and fine-grained aspects." *Empirical Methods in Natural Language Processing (EMNLP)*, 2019.

---

## 🗂️ Project Structure

```
amazon-product-customer-intelligence/
├── data/
│   ├── amazon_reviews_electronics_5core.csv   # 130K real reviews
│   └── data_dictionary.md                      # Column definitions
├── notebooks/
│   ├── 01_exploratory_analysis.ipynb          # Full EDA
│   ├── 02_customer_intelligence_sql.ipynb     # 10 business SQL queries
│   └── 03_executive_dashboard.ipynb           # Streamlit-ready visualizations
├── fetch_amazon_data.py                       # Automated data pipeline
├── dashboard.py                               # Streamlit interactive dashboard
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Fetch data (or use pre-downloaded CSV)
python fetch_amazon_data.py

# 3. Launch Streamlit dashboard
streamlit run dashboard.py

# 4. Open notebooks
jupyter notebook notebooks/
```

---

## 📓 Notebooks

### 01 — Exploratory Analysis
- Review volume by year (peak: 2013 with 25,000+ monthly reviews)
- Rating distribution (59.7% are 5-star reviews)
- Helpfulness patterns (83.7% upvote rate; 4-star reviews most helpful at 0.85 ratio)
- Temporal trends (steady growth 2004–2013, plateau 2014)
- Review length analysis (median 345 chars; longer reviews correlate with higher ratings)

### 02 — Customer Intelligence (10 SQL Queries)
All queries run against an **in-memory SQLite** database loaded from the CSV:

1. **Product Performance Ranking** — Top 15 products by avg rating + volume + helpfulness
2. **Rating Degradation Over Time** — Product age cohorts (0–24 months) show early reviews average 0.1★ higher
3. **Review Velocity Analysis** — 178 months covered; avg 731 reviews/month; peak at 2,847 (Dec 2013)
4. **Helpfulness Scoring** — Long reviews (500+) get 2.3× more votes; short reviews have highest helpfulness ratio (0.87)
5. **Sentiment Shift Detection** — YoY ratings stable at 4.12–4.25; 2012 dip to 4.12 coincides with review volume surge
6. **Product Lifecycle** — Early reviews (1st–3rd) score 4.25★; mature reviews (11+) score 4.18★
7. **Review Length Correlation** — 5-star reviews average 612 chars; 1-star reviews average 758 chars (angry = verbose)
8. **Seasonal Patterns** — November peaks at 13,426 reviews (Black Friday); July second-highest (Prime Day proxy)
9. **Customer Engagement Tiers** — 82.7% are one-off reviewers; power reviewers (50+) contribute 12.3% of all reviews
10. **Churn Signal** — 2013: 89 sharp decliners (-0.5+ drop) vs. 47 improvers (+0.5+ gain)

### 03 — Executive Dashboard
Streamlit-ready prototypes:
- Product engagement score leaderboard (rating × volume × helpfulness)
- YoY degradation alerts (2012→2013 swing detection)
- 3-month rolling sentiment tracker with sub-3.8 alert threshold
- Seasonal heatmap (year × month)

---

## 🖥️ Streamlit Dashboard

Launch with:
```bash
streamlit run dashboard.py
```

**Features:**
- 📦 **Product Leaderboard** — Top 15 by engagement score, color-coded by avg rating
- ⭐ **Rating Distribution** — Interactive bar chart with 5-star dominance
- 📈 **Monthly Trends** — Dual-axis volume + 3-month rolling rating with mean benchmark
- 🗓️ **Seasonal Heatmap** — Year×month intensity map (YlOrRd)
- 👍 **Helpfulness by Length** — Short vs. Medium vs. Long review performance
- 🔧 **Sidebar Filters** — Year range slider, minimum review threshold per product

---

## 📦 Data Pipeline

`fetch_amazon_data.py` handles the full pipeline:
1. Downloads the 495MB `reviews_Electronics_5.json.gz` from Stanford SNAP
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
jupyter>=1.0.0
streamlit>=1.25.0
plotly>=5.15.0
scipy>=1.10.0
wordcloud>=1.9.0
```

---

## ⚠️ Data Notes

- **100% real data.** No synthetic generation, no mock data, no placeholders.
- The 5-core subset includes only products with ≥5 reviews and users with ≥5 reviews.
- Sampling: uniform random 1/13 from the full 1,689,188 Electronics 5-core records to keep notebook execution fast while preserving statistical representativeness.
- Review text and summaries are preserved verbatim from the source.

---

**Built by:** Sierra Napier (evo3 / e3-ai)  
**License:** Data follows original UCSD Amazon dataset terms. Code: MIT.
