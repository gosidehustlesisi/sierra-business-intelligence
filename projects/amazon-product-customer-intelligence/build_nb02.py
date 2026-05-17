import json
import os
import sys
import base64
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

os.chdir('/root/.openclaw/workspace/sierra-business-intelligence/projects/amazon-product-customer-intelligence')
venv_site = Path('venv/lib/python3.12/site-packages')
if str(venv_site) not in sys.path:
    sys.path.insert(0, str(venv_site))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import duckdb

sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['figure.dpi'] = 100

# Load data
data_dir = Path('data')
products_files = sorted(data_dir.glob('keepa_products_*.csv'))
history_files = sorted(data_dir.glob('keepa_price_history_*.csv'))
deals_files = sorted(data_dir.glob('keepa_deals_*.csv'))

products = pd.read_csv(products_files[-1]) if products_files else pd.DataFrame()
price_history = pd.read_csv(history_files[-1]) if history_files else pd.DataFrame()
deals = pd.read_csv(deals_files[-1]) if deals_files else pd.DataFrame()

price_history['timestamp'] = pd.to_datetime(price_history['timestamp'])

print('Data loaded for SQL notebook')

Path('figures').mkdir(exist_ok=True)

def get_png_base64():
    import io
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def make_image_output():
    return {
        'output_type': 'display_data',
        'data': {
            'image/png': get_png_base64(),
            'text/plain': ['<Figure size 1200x600 with 1 Axes>']
        },
        'metadata': {}
    }

def make_text_output(lines):
    return {
        'output_type': 'stream',
        'name': 'stdout',
        'text': [line + '\n' for line in lines]
    }

def make_table_output(df, title=""):
    lines = [title] if title else []
    lines.append(df.to_string(index=False))
    return make_text_output(lines)

# Create in-memory DuckDB
con = duckdb.connect(':memory:')
con.execute("CREATE TABLE products AS SELECT * FROM products")
con.execute("CREATE TABLE price_history AS SELECT * FROM price_history")
con.execute("CREATE TABLE deals AS SELECT * FROM deals")

nb02 = {
    'cells': [],
    'metadata': {'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
                 'language_info': {'name': 'python', 'version': '3.12.0'}},
    'nbformat': 4, 'nbformat_minor': 4
}

nb02['cells'].append({
    'cell_type': 'markdown',
    'metadata': {},
    'source': '# 02 — Price Intelligence SQL (DuckDB)\n\n**10 business queries on live Keepa price data using DuckDB in-memory analytics.**\n\n**Data:** Keepa Electronics bestsellers + price history + deals\n\n**Generated:** 2026-05-17'
})

nb02['cells'].append({
    'cell_type': 'code',
    'execution_count': 1,
    'metadata': {},
    'outputs': [],
    'source': 'import pandas as pd\nimport duckdb\nimport matplotlib.pyplot as plt\nimport seaborn as sns\nimport numpy as np\nfrom pathlib import Path\n\nsns.set_style("whitegrid")\nplt.rcParams["figure.figsize"] = (12, 6)\nplt.rcParams["figure.dpi"] = 100\n\n# Load data\ndata_dir = Path("data")\nproducts = pd.read_csv(sorted(data_dir.glob("keepa_products_*.csv"))[-1])\nprice_history = pd.read_csv(sorted(data_dir.glob("keepa_price_history_*.csv"))[-1])\ndeals = pd.read_csv(sorted(data_dir.glob("keepa_deals_*.csv"))[-1])\nprice_history["timestamp"] = pd.to_datetime(price_history["timestamp"])\n\n# Create DuckDB in-memory database\ncon = duckdb.connect(":memory:")\ncon.execute("CREATE TABLE products AS SELECT * FROM products")\ncon.execute("CREATE TABLE price_history AS SELECT * FROM price_history")\ncon.execute("CREATE TABLE deals AS SELECT * FROM deals")\nprint("DuckDB ready — 3 tables loaded")'
})

# Query 1: Product Performance Ranking
q1 = con.execute("""
SELECT 
    brand,
    COUNT(*) as product_count,
    ROUND(AVG(current_price), 2) as avg_price,
    ROUND(AVG(rating), 2) as avg_rating,
    SUM(review_count) as total_reviews,
    ROUND(AVG((list_price - current_price) / NULLIF(list_price, 0) * 100), 1) as avg_discount_pct
FROM products
GROUP BY brand
ORDER BY total_reviews DESC
""").fetchdf()

exec("""
fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(q1['brand'], q1['total_reviews'] / 1000, color=sns.color_palette('husl', len(q1)))
ax.set_ylabel('Total Reviews (thousands)')
ax.set_title('Q1 — Brand Performance: Review Volume by Brand', fontsize=14, fontweight='bold')
for bar, rating in zip(bars, q1['avg_rating']):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
            f'{rating:.1f}★', ha='center', fontsize=10)
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig('figures/figure_007_q1_brand_performance.png', dpi=150, bbox_inches='tight')
""")

nb02['cells'].append({
    'cell_type': 'markdown',
    'metadata': {},
    'source': '## Q1 — Product Performance Ranking by Brand'
})
nb02['cells'].append({
    'cell_type': 'code',
    'execution_count': 2,
    'metadata': {},
    'outputs': [make_table_output(q1, "Q1 Results — Brand Performance Ranking"), make_image_output()],
    'source': 'q1 = con.execute("""\nSELECT \n    brand,\n    COUNT(*) as product_count,\n    ROUND(AVG(current_price), 2) as avg_price,\n    ROUND(AVG(rating), 2) as avg_rating,\n    SUM(review_count) as total_reviews,\n    ROUND(AVG((list_price - current_price) / NULLIF(list_price, 0) * 100), 1) as avg_discount_pct\nFROM products\nGROUP BY brand\nORDER BY total_reviews DESC\n""").fetchdf()\nprint(q1.to_string(index=False))\n\nfig, ax = plt.subplots(figsize=(12, 6))\nbars = ax.bar(q1["brand"], q1["total_reviews"] / 1000, color=sns.color_palette("husl", len(q1)))\nax.set_ylabel("Total Reviews (thousands)")\nax.set_title("Q1 — Brand Performance: Review Volume by Brand", fontsize=14, fontweight="bold")\nfor bar, rating in zip(bars, q1["avg_rating"]):\n    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,\n            f"{rating:.1f}★", ha="center", fontsize=10)\nplt.xticks(rotation=30)\nplt.tight_layout()\nplt.savefig("figures/figure_007_q1_brand_performance.png", dpi=150, bbox_inches="tight")\nplt.show()'
})

# Query 2: Price Trend Analysis (30-day rolling)
q2 = con.execute("""
SELECT 
    asin,
    title,
    DATE_TRUNC('month', timestamp::DATE) as month,
    ROUND(AVG(price), 2) as avg_monthly_price,
    ROUND(MIN(price), 2) as min_price,
    ROUND(MAX(price), 2) as max_price,
    ROUND(MAX(price) - MIN(price), 2) as price_volatility
FROM price_history
GROUP BY asin, title, month
ORDER BY asin, month
""").fetchdf()

exec("""
top_asin = q2['asin'].value_counts().index[0]
sub = q2[q2['asin'] == top_asin]
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(sub['month'], sub['avg_monthly_price'], marker='o', linewidth=2, label='Avg Price')
ax.fill_between(sub['month'], sub['min_price'], sub['max_price'], alpha=0.3, label='Min-Max Range')
ax.set_xlabel('Month')
ax.set_ylabel('Price ($)')
ax.set_title(f'Q2 — Price Trend: {sub["title"].iloc[0][:30]}', fontsize=14, fontweight='bold')
ax.legend()
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig('figures/figure_008_q2_price_trend.png', dpi=150, bbox_inches='tight')
""")

nb02['cells'].append({
    'cell_type': 'markdown',
    'metadata': {},
    'source': '## Q2 — Price Trend Analysis (Monthly Aggregation)'
})
nb02['cells'].append({
    'cell_type': 'code',
    'execution_count': 3,
    'metadata': {},
    'outputs': [make_table_output(q2.head(10), "Q2 Results — Monthly Price Trends (first 10 rows)"), make_image_output()],
    'source': 'q2 = con.execute("""\nSELECT \n    asin,\n    title,\n    DATE_TRUNC(\'month\', timestamp::DATE) as month,\n    ROUND(AVG(price), 2) as avg_monthly_price,\n    ROUND(MIN(price), 2) as min_price,\n    ROUND(MAX(price), 2) as max_price,\n    ROUND(MAX(price) - MIN(price), 2) as price_volatility\nFROM price_history\nGROUP BY asin, title, month\nORDER BY asin, month\n""").fetchdf()\nprint(q2.head(10).to_string(index=False))\n\ntop_asin = q2["asin"].value_counts().index[0]\nsub = q2[q2["asin"] == top_asin]\nfig, ax = plt.subplots(figsize=(12, 6))\nax.plot(sub["month"], sub["avg_monthly_price"], marker="o", linewidth=2, label="Avg Price")\nax.fill_between(sub["month"], sub["min_price"], sub["max_price"], alpha=0.3, label="Min-Max Range")\nax.set_xlabel("Month")\nax.set_ylabel("Price ($)")\nax.set_title(f"Q2 — Price Trend: {sub[\'title\'].iloc[0][:30]}", fontsize=14, fontweight="bold")\nax.legend()\nplt.xticks(rotation=30)\nplt.tight_layout()\nplt.savefig("figures/figure_008_q2_price_trend.png", dpi=150, bbox_inches="tight")\nplt.show()'
})

# Query 3: Deal Detection
q3 = con.execute("""
SELECT 
    d.asin,
    d.title,
    d.current_price,
    d.previous_price,
    d.price_drop_pct,
    d.deal_type,
    p.rating,
    p.review_count,
    ROUND((p.list_price - d.current_price) / NULLIF(p.list_price, 0) * 100, 1) as total_savings_pct
FROM deals d
JOIN products p ON d.asin = p.asin
ORDER BY d.price_drop_pct DESC
""").fetchdf()

exec("""
fig, ax = plt.subplots(figsize=(12, 6))
colors = ['#d32f2f' if x > 25 else '#f57c00' if x > 20 else '#fbc02d' for x in q3['price_drop_pct']]
bars = ax.bar(q3['title'].str[:30], q3['price_drop_pct'], color=colors)
ax.set_ylabel('Price Drop (%)')
ax.set_title('Q3 — Deal Detection: Active Price Drops by Product', fontsize=14, fontweight='bold')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('figures/figure_009_q3_deal_detection.png', dpi=150, bbox_inches='tight')
""")

nb02['cells'].append({
    'cell_type': 'markdown',
    'metadata': {},
    'source': '## Q3 — Deal Detection: Products with Active Price Drops'
})
nb02['cells'].append({
    'cell_type': 'code',
    'execution_count': 4,
    'metadata': {},
    'outputs': [make_table_output(q3, "Q3 Results — Deal Detection"), make_image_output()],
    'source': 'q3 = con.execute("""\nSELECT \n    d.asin,\n    d.title,\n    d.current_price,\n    d.previous_price,\n    d.price_drop_pct,\n    d.deal_type,\n    p.rating,\n    p.review_count,\n    ROUND((p.list_price - d.current_price) / NULLIF(p.list_price, 0) * 100, 1) as total_savings_pct\nFROM deals d\nJOIN products p ON d.asin = p.asin\nORDER BY d.price_drop_pct DESC\n""").fetchdf()\nprint(q3.to_string(index=False))\n\nfig, ax = plt.subplots(figsize=(12, 6))\ncolors = ["#d32f2f" if x > 25 else "#f57c00" if x > 20 else "#fbc02d" for x in q3["price_drop_pct"]]\nbars = ax.bar(q3["title"].str[:30], q3["price_drop_pct"], color=colors)\nax.set_ylabel("Price Drop (%)")\nax.set_title("Q3 — Deal Detection: Active Price Drops by Product", fontsize=14, fontweight="bold")\nplt.xticks(rotation=45, ha="right")\nplt.tight_layout()\nplt.savefig("figures/figure_009_q3_deal_detection.png", dpi=150, bbox_inches="tight")\nplt.show()'
})

# Query 4: Category Analysis — Price tiers
q4 = con.execute("""
SELECT 
    CASE 
        WHEN current_price < 50 THEN 'Budget (<$50)'
        WHEN current_price < 150 THEN 'Mid-range ($50–$150)'
        WHEN current_price < 400 THEN 'Premium ($150–$400)'
        ELSE 'Luxury ($400+)'
    END as price_tier,
    COUNT(*) as product_count,
    ROUND(AVG(current_price), 2) as tier_avg_price,
    ROUND(AVG(rating), 2) as tier_avg_rating,
    SUM(review_count) as tier_total_reviews
FROM products
GROUP BY price_tier
ORDER BY tier_avg_price
""").fetchdf()

exec("""
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
ax1.pie(q4['product_count'], labels=q4['price_tier'], autopct='%1.1f%%', startangle=90, colors=sns.color_palette('pastel'))
ax1.set_title('Product Count by Price Tier')
bars = ax2.bar(q4['price_tier'], q4['tier_avg_rating'], color=sns.color_palette('muted', len(q4)))
ax2.set_ylabel('Average Rating (★)')
ax2.set_title('Average Rating by Price Tier')
ax2.set_ylim(4.0, 5.0)
for bar, rating in zip(bars, q4['tier_avg_rating']):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, f'{rating:.2f}', ha='center')
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig('figures/figure_010_q4_price_tiers.png', dpi=150, bbox_inches='tight')
""")

nb02['cells'].append({
    'cell_type': 'markdown',
    'metadata': {},
    'source': '## Q4 — Category Analysis: Price Tiers'
})
nb02['cells'].append({
    'cell_type': 'code',
    'execution_count': 5,
    'metadata': {},
    'outputs': [make_table_output(q4, "Q4 Results — Price Tier Analysis"), make_image_output()],
    'source': 'q4 = con.execute("""\nSELECT \n    CASE \n        WHEN current_price < 50 THEN \'Budget (<$50)\'\n        WHEN current_price < 150 THEN \'Mid-range ($50–$150)\'\n        WHEN current_price < 400 THEN \'Premium ($150–$400)\'\n        ELSE \'Luxury ($400+)\'\n    END as price_tier,\n    COUNT(*) as product_count,\n    ROUND(AVG(current_price), 2) as tier_avg_price,\n    ROUND(AVG(rating), 2) as tier_avg_rating,\n    SUM(review_count) as tier_total_reviews\nFROM products\nGROUP BY price_tier\nORDER BY tier_avg_price\n""").fetchdf()\nprint(q4.to_string(index=False))\n\nfig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))\nax1.pie(q4["product_count"], labels=q4["price_tier"], autopct="%1.1f%%", startangle=90, colors=sns.color_palette("pastel"))\nax1.set_title("Product Count by Price Tier")\nbars = ax2.bar(q4["price_tier"], q4["tier_avg_rating"], color=sns.color_palette("muted", len(q4)))\nax2.set_ylabel("Average Rating (★)")\nax2.set_title("Average Rating by Price Tier")\nax2.set_ylim(4.0, 5.0)\nfor bar, rating in zip(bars, q4["tier_avg_rating"]):\n    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, f"{rating:.2f}", ha="center")\nplt.xticks(rotation=15)\nplt.tight_layout()\nplt.savefig("figures/figure_010_q4_price_tiers.png", dpi=150, bbox_inches="tight")\nplt.show()'
})

# Query 5: Price volatility ranking
q5 = con.execute("""
SELECT 
    ph.asin,
    MAX(ph.title) as title,
    ROUND(AVG(ph.price), 2) as avg_price,
    ROUND(STDDEV(ph.price), 2) as price_stddev,
    ROUND((STDDEV(ph.price) / AVG(ph.price)) * 100, 2) as volatility_pct,
    COUNT(*) as data_points
FROM price_history ph
GROUP BY ph.asin
HAVING COUNT(*) > 10
ORDER BY volatility_pct DESC
LIMIT 10
""").fetchdf()

exec("""
fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.barh(q5['title'].str[:30], q5['volatility_pct'], color=sns.color_palette('rocket_r', len(q5)))
ax.set_xlabel('Price Volatility (%)')
ax.set_title('Q5 — Top 10 Most Volatile Products by Price', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('figures/figure_011_q5_volatility.png', dpi=150, bbox_inches='tight')
""")

nb02['cells'].append({
    'cell_type': 'markdown',
    'metadata': {},
    'source': '## Q5 — Price Volatility Ranking'
})
nb02['cells'].append({
    'cell_type': 'code',
    'execution_count': 6,
    'metadata': {},
    'outputs': [make_table_output(q5, "Q5 Results — Top 10 Most Volatile Products"), make_image_output()],
    'source': 'q5 = con.execute("""\nSELECT \n    ph.asin,\n    MAX(ph.title) as title,\n    ROUND(AVG(ph.price), 2) as avg_price,\n    ROUND(STDDEV(ph.price), 2) as price_stddev,\n    ROUND((STDDEV(ph.price) / AVG(ph.price)) * 100, 2) as volatility_pct,\n    COUNT(*) as data_points\nFROM price_history ph\nGROUP BY ph.asin\nHAVING COUNT(*) > 10\nORDER BY volatility_pct DESC\nLIMIT 10\n""").fetchdf()\nprint(q5.to_string(index=False))\n\nfig, ax = plt.subplots(figsize=(12, 6))\nbars = ax.barh(q5["title"].str[:30], q5["volatility_pct"], color=sns.color_palette("rocket_r", len(q5)))\nax.set_xlabel("Price Volatility (%)")\nax.set_title("Q5 — Top 10 Most Volatile Products by Price", fontsize=14, fontweight="bold")\nplt.tight_layout()\nplt.savefig("figures/figure_011_q5_volatility.png", dpi=150, bbox_inches="tight")\nplt.show()'
})

# Query 6: Discount opportunity score
q6 = con.execute("""
SELECT 
    asin,
    title,
    current_price,
    list_price,
    ROUND((list_price - current_price) / NULLIF(list_price, 0) * 100, 1) as discount_pct,
    rating,
    review_count,
    ROUND(rating * LOG(review_count + 1) * (list_price - current_price) / NULLIF(list_price, 0), 2) as deal_score
FROM products
WHERE list_price > current_price
ORDER BY deal_score DESC
LIMIT 15
""").fetchdf()

exec("""
fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.barh(q6['title'].str[:30], q6['deal_score'], color=sns.color_palette('coolwarm', len(q6)))
ax.set_xlabel('Deal Opportunity Score (Rating × Log(Reviews) × Discount%)')
ax.set_title('Q6 — Top 15 Discount Opportunity Scores', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('figures/figure_012_q6_deal_score.png', dpi=150, bbox_inches='tight')
""")

nb02['cells'].append({
    'cell_type': 'markdown',
    'metadata': {},
    'source': '## Q6 — Discount Opportunity Score'
})
nb02['cells'].append({
    'cell_type': 'code',
    'execution_count': 7,
    'metadata': {},
    'outputs': [make_table_output(q6, "Q6 Results — Top 15 Discount Opportunities"), make_image_output()],
    'source': 'q6 = con.execute("""\nSELECT \n    asin,\n    title,\n    current_price,\n    list_price,\n    ROUND((list_price - current_price) / NULLIF(list_price, 0) * 100, 1) as discount_pct,\n    rating,\n    review_count,\n    ROUND(rating * LOG(review_count + 1) * (list_price - current_price) / NULLIF(list_price, 0), 2) as deal_score\nFROM products\nWHERE list_price > current_price\nORDER BY deal_score DESC\nLIMIT 15\n""").fetchdf()\nprint(q6.to_string(index=False))\n\nfig, ax = plt.subplots(figsize=(12, 6))\nbars = ax.barh(q6["title"].str[:30], q6["deal_score"], color=sns.color_palette("coolwarm", len(q6)))\nax.set_xlabel("Deal Opportunity Score (Rating × Log(Reviews) × Discount%)")\nax.set_title("Q6 — Top 15 Discount Opportunity Scores", fontsize=14, fontweight="bold")\nplt.tight_layout()\nplt.savefig("figures/figure_012_q6_deal_score.png", dpi=150, bbox_inches="tight")\nplt.show()'
})

# Query 7: Review quality vs price
q7 = con.execute("""
SELECT 
    CASE 
        WHEN current_price < 50 THEN 'Budget'
        WHEN current_price < 150 THEN 'Mid-range'
        WHEN current_price < 400 THEN 'Premium'
        ELSE 'Luxury'
    END as tier,
    ROUND(AVG(rating), 2) as avg_rating,
    ROUND(AVG(review_count), 0) as avg_reviews,
    COUNT(*) as count
FROM products
GROUP BY tier
ORDER BY MIN(current_price)
""").fetchdf()

exec("""
fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(q7))
width = 0.35
bars1 = ax.bar(x - width/2, q7['avg_rating'], width, label='Avg Rating', color='steelblue')
ax2 = ax.twinx()
bars2 = ax2.bar(x + width/2, q7['avg_reviews'] / 1000, width, label='Avg Reviews (K)', color='coral')
ax.set_xlabel('Price Tier')
ax.set_ylabel('Average Rating (★)')
ax2.set_ylabel('Average Reviews (thousands)')
ax.set_title('Q7 — Review Quality vs. Price Tier', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(q7['tier'])
ax.legend(loc='upper left')
ax2.legend(loc='upper right')
plt.tight_layout()
plt.savefig('figures/figure_013_q7_review_vs_price.png', dpi=150, bbox_inches='tight')
""")

nb02['cells'].append({
    'cell_type': 'markdown',
    'metadata': {},
    'source': '## Q7 — Review Quality vs. Price Tier'
})
nb02['cells'].append({
    'cell_type': 'code',
    'execution_count': 8,
    'metadata': {},
    'outputs': [make_table_output(q7, "Q7 Results — Review Quality by Price Tier"), make_image_output()],
    'source': 'q7 = con.execute("""\nSELECT \n    CASE \n        WHEN current_price < 50 THEN \'Budget\'\n        WHEN current_price < 150 THEN \'Mid-range\'\n        WHEN current_price < 400 THEN \'Premium\'\n        ELSE \'Luxury\'\n    END as tier,\n    ROUND(AVG(rating), 2) as avg_rating,\n    ROUND(AVG(review_count), 0) as avg_reviews,\n    COUNT(*) as count\nFROM products\nGROUP BY tier\nORDER BY MIN(current_price)\n""").fetchdf()\nprint(q7.to_string(index=False))\n\nfig, ax = plt.subplots(figsize=(10, 6))\nx = np.arange(len(q7))\nwidth = 0.35\nbars1 = ax.bar(x - width/2, q7["avg_rating"], width, label="Avg Rating", color="steelblue")\nax2 = ax.twinx()\nbars2 = ax2.bar(x + width/2, q7["avg_reviews"] / 1000, width, label="Avg Reviews (K)", color="coral")\nax.set_xlabel("Price Tier")\nax.set_ylabel("Average Rating (★)")\nax2.set_ylabel("Average Reviews (thousands)")\nax.set_title("Q7 — Review Quality vs. Price Tier", fontsize=14, fontweight="bold")\nax.set_xticks(x)\nax.set_xticklabels(q7["tier"])\nax.legend(loc="upper left")\nax2.legend(loc="upper right")\nplt.tight_layout()\nplt.savefig("figures/figure_013_q7_review_vs_price.png", dpi=150, bbox_inches="tight")\nplt.show()'
})

# Query 8: Price drop frequency by brand
q8 = con.execute("""
SELECT 
    p.brand,
    COUNT(DISTINCT d.asin) as products_with_deals,
    COUNT(*) as total_deals,
    ROUND(AVG(d.price_drop_pct), 1) as avg_drop_pct,
    ROUND(MAX(d.price_drop_pct), 1) as max_drop_pct
FROM deals d
JOIN products p ON d.asin = p.asin
GROUP BY p.brand
ORDER BY products_with_deals DESC
""").fetchdf()

exec("""
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(q8['brand'], q8['products_with_deals'], color=sns.color_palette('Set2', len(q8)))
ax.set_ylabel('Products with Active Deals')
ax.set_title('Q8 — Deal Frequency by Brand', fontsize=14, fontweight='bold')
for bar, avg in zip(bars, q8['avg_drop_pct']):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
            f'{avg:.1f}% avg', ha='center', fontsize=9)
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig('figures/figure_014_q8_deals_by_brand.png', dpi=150, bbox_inches='tight')
""")

nb02['cells'].append({
    'cell_type': 'markdown',
    'metadata': {},
    'source': '## Q8 — Price Drop Frequency by Brand'
})
nb02['cells'].append({
    'cell_type': 'code',
    'execution_count': 9,
    'metadata': {},
    'outputs': [make_table_output(q8, "Q8 Results — Deals by Brand"), make_image_output()],
    'source': 'q8 = con.execute("""\nSELECT \n    p.brand,\n    COUNT(DISTINCT d.asin) as products_with_deals,\n    COUNT(*) as total_deals,\n    ROUND(AVG(d.price_drop_pct), 1) as avg_drop_pct,\n    ROUND(MAX(d.price_drop_pct), 1) as max_drop_pct\nFROM deals d\nJOIN products p ON d.asin = p.asin\nGROUP BY p.brand\nORDER BY products_with_deals DESC\n""").fetchdf()\nprint(q8.to_string(index=False))\n\nfig, ax = plt.subplots(figsize=(10, 6))\nbars = ax.bar(q8["brand"], q8["products_with_deals"], color=sns.color_palette("Set2", len(q8)))\nax.set_ylabel("Products with Active Deals")\nax.set_title("Q8 — Deal Frequency by Brand", fontsize=14, fontweight="bold")\nfor bar, avg in zip(bars, q8["avg_drop_pct"]):\n    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,\n            f"{avg:.1f}% avg", ha="center", fontsize=9)\nplt.xticks(rotation=30)\nplt.tight_layout()\nplt.savefig("figures/figure_014_q8_deals_by_brand.png", dpi=150, bbox_inches="tight")\nplt.show()'
})

# Query 9: Time-to-best-price analysis
q9 = con.execute("""
SELECT 
    asin,
    MAX(title) as title,
    MIN(price) as all_time_low,
    MAX(price) as all_time_high,
    ROUND(AVG(price), 2) as avg_price,
    ROUND((MAX(price) - MIN(price)) / NULLIF(MAX(price), 0) * 100, 1) as max_savings_pct,
    COUNT(*) as observations
FROM price_history
GROUP BY asin
HAVING COUNT(*) > 20
ORDER BY max_savings_pct DESC
LIMIT 10
""").fetchdf()

exec("""
fig, ax = plt.subplots(figsize=(12, 6))
x = np.arange(len(q9))
width = 0.35
bars1 = ax.bar(x - width/2, q9['all_time_high'], width, label='All-Time High', color='lightcoral', alpha=0.8)
bars2 = ax.bar(x + width/2, q9['all_time_low'], width, label='All-Time Low', color='lightgreen', alpha=0.8)
ax.set_ylabel('Price ($)')
ax.set_title('Q9 — All-Time High vs. Low Prices (Top 10 Savings Opportunities)', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(q9['title'].str[:20], rotation=45, ha='right')
ax.legend()
plt.tight_layout()
plt.savefig('figures/figure_015_q9_high_low.png', dpi=150, bbox_inches='tight')
""")

nb02['cells'].append({
    'cell_type': 'markdown',
    'metadata': {},
    'source': '## Q9 — Time-to-Best-Price Analysis'
})
nb02['cells'].append({
    'cell_type': 'code',
    'execution_count': 10,
    'metadata': {},
    'outputs': [make_table_output(q9, "Q9 Results — All-Time High/Low Analysis"), make_image_output()],
    'source': 'q9 = con.execute("""\nSELECT \n    asin,\n    MAX(title) as title,\n    MIN(price) as all_time_low,\n    MAX(price) as all_time_high,\n    ROUND(AVG(price), 2) as avg_price,\n    ROUND((MAX(price) - MIN(price)) / NULLIF(MAX(price), 0) * 100, 1) as max_savings_pct,\n    COUNT(*) as observations\nFROM price_history\nGROUP BY asin\nHAVING COUNT(*) > 20\nORDER BY max_savings_pct DESC\nLIMIT 10\n""").fetchdf()\nprint(q9.to_string(index=False))\n\nfig, ax = plt.subplots(figsize=(12, 6))\nx = np.arange(len(q9))\nwidth = 0.35\nbars1 = ax.bar(x - width/2, q9["all_time_high"], width, label="All-Time High", color="lightcoral", alpha=0.8)\nbars2 = ax.bar(x + width/2, q9["all_time_low"], width, label="All-Time Low", color="lightgreen", alpha=0.8)\nax.set_ylabel("Price ($)")\nax.set_title("Q9 — All-Time High vs. Low Prices (Top 10 Savings Opportunities)", fontsize=14, fontweight="bold")\nax.set_xticks(x)\nax.set_xticklabels(q9["title"].str[:20], rotation=45, ha="right")\nax.legend()\nplt.tight_layout()\nplt.savefig("figures/figure_015_q9_high_low.png", dpi=150, bbox_inches="tight")\nplt.show()'
})

# Query 10: Market concentration
q10 = con.execute("""
SELECT 
    brand,
    COUNT(*) as products,
    SUM(review_count) as total_reviews,
    ROUND(SUM(review_count) * 100.0 / (SELECT SUM(review_count) FROM products), 1) as market_share_pct,
    ROUND(AVG(current_price), 2) as avg_price,
    ROUND(AVG(rating), 2) as avg_rating
FROM products
GROUP BY brand
ORDER BY market_share_pct DESC
""").fetchdf()

exec("""
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
ax1.pie(q10['market_share_pct'], labels=q10['brand'], autopct='%1.1f%%', startangle=90, colors=sns.color_palette('tab10'))
ax1.set_title('Market Share by Review Volume')
bars = ax2.bar(q10['brand'], q10['products'], color=sns.color_palette('tab10', len(q10)))
ax2.set_ylabel('Product Count')
ax2.set_title('Products in Bestseller List by Brand')
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig('figures/figure_016_q10_market_concentration.png', dpi=150, bbox_inches='tight')
""")

nb02['cells'].append({
    'cell_type': 'markdown',
    'metadata': {},
    'source': '## Q10 — Market Concentration Analysis'
})
nb02['cells'].append({
    'cell_type': 'code',
    'execution_count': 11,
    'metadata': {},
    'outputs': [make_table_output(q10, "Q10 Results — Market Concentration"), make_image_output()],
    'source': 'q10 = con.execute("""\nSELECT \n    brand,\n    COUNT(*) as products,\n    SUM(review_count) as total_reviews,\n    ROUND(SUM(review_count) * 100.0 / (SELECT SUM(review_count) FROM products), 1) as market_share_pct,\n    ROUND(AVG(current_price), 2) as avg_price,\n    ROUND(AVG(rating), 2) as avg_rating\nFROM products\nGROUP BY brand\nORDER BY market_share_pct DESC\n""").fetchdf()\nprint(q10.to_string(index=False))\n\nfig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))\nax1.pie(q10["market_share_pct"], labels=q10["brand"], autopct="%1.1f%%", startangle=90, colors=sns.color_palette("tab10"))\nax1.set_title("Market Share by Review Volume")\nbars = ax2.bar(q10["brand"], q10["products"], color=sns.color_palette("tab10", len(q10)))\nax2.set_ylabel("Product Count")\nax2.set_title("Products in Bestseller List by Brand")\nplt.xticks(rotation=30)\nplt.tight_layout()\nplt.savefig("figures/figure_016_q10_market_concentration.png", dpi=150, bbox_inches="tight")\nplt.show()'
})

# Save
with open('notebooks/02_price_intelligence_sql.ipynb', 'w') as f:
    json.dump(nb02, f, indent=1)

print('Notebook 02 saved successfully')
