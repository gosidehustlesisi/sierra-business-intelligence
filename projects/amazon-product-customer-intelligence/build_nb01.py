import json
import os
import sys
import base64
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Ensure we're in the right directory
os.chdir('/root/.openclaw/workspace/sierra-business-intelligence/projects/amazon-product-customer-intelligence')

# Add venv packages
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

reviews = pd.read_csv(data_dir / 'amazon_reviews_electronics_5core.csv')
reviews['reviewDate'] = pd.to_datetime(reviews['unixReviewTime'], unit='s')
reviews['reviewYear'] = reviews['reviewDate'].dt.year
reviews['reviewLength'] = reviews['reviewText'].fillna('').str.len()
reviews['helpfulnessRatio'] = np.where(reviews['helpful_total'] > 0, reviews['helpful_upvotes'] / reviews['helpful_total'], np.nan)

price_history['timestamp'] = pd.to_datetime(price_history['timestamp'])

print('Data loaded successfully')
print(f'Products: {len(products)}, History: {len(price_history)}, Deals: {len(deals)}, Reviews: {len(reviews)}')

# Create figures directory
Path('figures').mkdir(exist_ok=True)

# Helper to capture matplotlib output
def get_png_base64():
    import io
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def make_image_output():
    b64 = get_png_base64()
    return {
        'output_type': 'display_data',
        'data': {
            'image/png': b64,
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

# ---------------------------------------------------------------------------
# NOTEBOOK 01: Exploratory Analysis
# ---------------------------------------------------------------------------

nb01 = {
    'cells': [],
    'metadata': {'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
                 'language_info': {'name': 'python', 'version': '3.12.0'}},
    'nbformat': 4, 'nbformat_minor': 4
}

# Cell 0: Markdown
nb01['cells'].append({
    'cell_type': 'markdown',
    'metadata': {},
    'source': '# 01 — Exploratory Analysis: Live Keepa Price Data + Historical Review Patterns\n\n**Data Sources:**\n- **Live:** Keepa API — Amazon Electronics bestsellers, price history, deals (seed data until API key configured)\n- **Historical:** UCSD Amazon Review Dataset — 130,038 Electronics reviews (1999–2014)\n\n**Generated:** 2026-05-17'
})

# Cell 1: Imports
nb01['cells'].append({
    'cell_type': 'code',
    'execution_count': 1,
    'metadata': {},
    'outputs': [],
    'source': 'import pandas as pd\nimport numpy as np\nimport matplotlib.pyplot as plt\nimport seaborn as sns\nfrom pathlib import Path\nimport warnings\nwarnings.filterwarnings(\'ignore\')\n\nsns.set_style(\'whitegrid\')\nplt.rcParams[\'figure.figsize\'] = (12, 6)\nplt.rcParams[\'figure.dpi\'] = 100'
})

# Cell 2: Load data
exec('''
import glob

data_dir = Path('data')
products_files = sorted(data_dir.glob('keepa_products_*.csv'))
history_files = sorted(data_dir.glob('keepa_price_history_*.csv'))
deals_files = sorted(data_dir.glob('keepa_deals_*.csv'))

products = pd.read_csv(products_files[-1]) if products_files else pd.DataFrame()
price_history = pd.read_csv(history_files[-1]) if history_files else pd.DataFrame()
deals = pd.read_csv(deals_files[-1]) if deals_files else pd.DataFrame()

reviews = pd.read_csv(data_dir / 'amazon_reviews_electronics_5core.csv')
reviews['reviewDate'] = pd.to_datetime(reviews['unixReviewTime'], unit='s')
reviews['reviewYear'] = reviews['reviewDate'].dt.year
reviews['reviewLength'] = reviews['reviewText'].fillna('').str.len()
reviews['helpfulnessRatio'] = np.where(reviews['helpful_total'] > 0, reviews['helpful_upvotes'] / reviews['helpful_total'], np.nan)

price_history['timestamp'] = pd.to_datetime(price_history['timestamp'])
''')

load_lines = [
    '=== LIVE KEEPA DATA ===',
    f'Products: {len(products)} | Brands: {products["brand"].nunique()} | Price range: ${products["current_price"].min():.2f} – ${products["current_price"].max():.2f}',
    f'Avg rating: {products["rating"].mean():.2f} ★ | Avg reviews: {products["review_count"].mean():,.0f}',
    f'Price history records: {len(price_history):,} (180-day span)',
    f'Deals active: {len(deals)} products with price drops 15–35%',
    '',
    '=== HISTORICAL UCSD REVIEWS ===',
    f'Reviews: {len(reviews):,} | Products: {reviews["asin"].nunique():,} | Reviewers: {reviews["reviewerID"].nunique():,}',
    f'Date range: {reviews["reviewDate"].min().date()} → {reviews["reviewDate"].max().date()}',
    f'Avg rating: {reviews["overall"].mean():.2f} ★'
]

nb01['cells'].append({
    'cell_type': 'code',
    'execution_count': 2,
    'metadata': {},
    'outputs': [make_text_output(load_lines)],
    'source': '# Load live Keepa data (auto-detect latest files)\nimport glob\n\ndata_dir = Path(\'data\')\n\nproducts_files = sorted(data_dir.glob(\'keepa_products_*.csv\'))\nhistory_files = sorted(data_dir.glob(\'keepa_price_history_*.csv\'))\ndeals_files = sorted(data_dir.glob(\'keepa_deals_*.csv\'))\n\nproducts = pd.read_csv(products_files[-1]) if products_files else pd.DataFrame()\nprice_history = pd.read_csv(history_files[-1]) if history_files else pd.DataFrame()\ndeals = pd.read_csv(deals_files[-1]) if deals_files else pd.DataFrame()\n\n# Load historical review data\nreviews = pd.read_csv(data_dir / \'amazon_reviews_electronics_5core.csv\')\nreviews[\'reviewDate\'] = pd.to_datetime(reviews[\'unixReviewTime\'], unit=\'s\')\nreviews[\'reviewYear\'] = reviews[\'reviewDate\'].dt.year\nreviews[\'reviewLength\'] = reviews[\'reviewText\'].fillna(\'\').str.len()\nreviews[\'helpfulnessRatio\'] = np.where(\n    reviews[\'helpful_total\'] > 0,\n    reviews[\'helpful_upvotes\'] / reviews[\'helpful_total\'],\n    np.nan\n)\n\nprice_history[\'timestamp\'] = pd.to_datetime(price_history[\'timestamp\'])\n\nprint(f"Products: {len(products)} | Brands: {products[\'brand\'].nunique()} | Price range: ${products[\'current_price\'].min():.2f} – ${products[\'current_price\'].max():.2f}")\nprint(f"Avg rating: {products[\'rating\'].mean():.2f} ★ | Avg reviews: {products[\'review_count\'].mean():,.0f}")\nprint(f"Price history records: {len(price_history):,} (180-day span)")\nprint(f"Deals active: {len(deals)} products with price drops 15–35%")\nprint()\nprint(f"Reviews: {len(reviews):,} | Products: {reviews[\'asin\'].nunique():,} | Reviewers: {reviews[\'reviewerID\'].nunique():,}")\nprint(f"Date range: {reviews[\'reviewDate\'].min().date()} → {reviews[\'reviewDate\'].max().date()}")\nprint(f"Avg rating: {reviews[\'overall\'].mean():.2f} ★")'
})

# Cell 3: Brand landscape
exec('''
brand_stats = products.groupby('brand').agg(
    count=('asin', 'size'),
    avg_price=('current_price', 'mean'),
    avg_rating=('rating', 'mean'),
    total_reviews=('review_count', 'sum')
).reset_index().sort_values('count', ascending=True)

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.barh(brand_stats['brand'], brand_stats['count'], color=sns.color_palette('husl', len(brand_stats)))
for bar, price, rating in zip(bars, brand_stats['avg_price'], brand_stats['avg_rating']):
    ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
            f'${price:.0f} | {rating:.1f}★', va='center', fontsize=9)
ax.set_xlabel('Products in Bestseller List')
ax.set_title('Brand Presence — Amazon Electronics Bestsellers (Live Keepa Data)', fontsize=14, fontweight='bold')
ax.set_xlim(0, brand_stats['count'].max() + 3)
plt.tight_layout()
plt.savefig('figures/figure_001_brand_landscape.png', dpi=150, bbox_inches='tight')
''')

nb01['cells'].append({
    'cell_type': 'code',
    'execution_count': 3,
    'metadata': {},
    'outputs': [make_image_output()],
    'source': 'brand_stats = products.groupby(\'brand\').agg(\n    count=(\'asin\', \'size\'),\n    avg_price=(\'current_price\', \'mean\'),\n    avg_rating=(\'rating\', \'mean\'),\n    total_reviews=(\'review_count\', \'sum\')\n).reset_index().sort_values(\'count\', ascending=True)\n\nfig, ax = plt.subplots(figsize=(12, 6))\nbars = ax.barh(brand_stats[\'brand\'], brand_stats[\'count\'], color=sns.color_palette(\'husl\', len(brand_stats)))\nfor bar, price, rating in zip(bars, brand_stats[\'avg_price\'], brand_stats[\'avg_rating\']):\n    ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,\n            f\'${price:.0f} | {rating:.1f}★\', va=\'center\', fontsize=9)\nax.set_xlabel(\'Products in Bestseller List\')\nax.set_title(\'Brand Presence — Amazon Electronics Bestsellers (Live Keepa Data)\', fontsize=14, fontweight=\'bold\')\nax.set_xlim(0, brand_stats[\'count\'].max() + 3)\nplt.tight_layout()\nplt.savefig(\'figures/figure_001_brand_landscape.png\', dpi=150, bbox_inches=\'tight\')\nplt.show()'
})

# Cell 4: Price vs Rating scatter
exec('''
fig, ax = plt.subplots(figsize=(12, 6))
scatter = ax.scatter(products['current_price'], products['rating'],
                     s=products['review_count']/500, c=products['review_count'],
                     cmap='viridis', alpha=0.7, edgecolors='black', linewidth=0.5)
for _, row in products.iterrows():
    if row['review_count'] > 100000 or row['current_price'] > 900:
        ax.annotate(row['title'][:25], (row['current_price'], row['rating']),
                    fontsize=8, alpha=0.8)
ax.set_xlabel('Current Price ($)')
ax.set_ylabel('Rating (★)')
ax.set_title('Price vs. Rating — Bubble Size = Review Volume', fontsize=14, fontweight='bold')
ax.set_xlim(0, 1200)
ax.set_ylim(4.3, 4.9)
plt.colorbar(scatter, label='Review Count')
plt.tight_layout()
plt.savefig('figures/figure_002_price_rating_scatter.png', dpi=150, bbox_inches='tight')
''')

nb01['cells'].append({
    'cell_type': 'code',
    'execution_count': 4,
    'metadata': {},
    'outputs': [make_image_output()],
    'source': 'fig, ax = plt.subplots(figsize=(12, 6))\nscatter = ax.scatter(products[\'current_price\'], products[\'rating\'],\n                     s=products[\'review_count\']/500, c=products[\'review_count\'],\n                     cmap=\'viridis\', alpha=0.7, edgecolors=\'black\', linewidth=0.5)\nfor _, row in products.iterrows():\n    if row[\'review_count\'] > 100000 or row[\'current_price\'] > 900:\n        ax.annotate(row[\'title\'][:25], (row[\'current_price\'], row[\'rating\']),\n                    fontsize=8, alpha=0.8)\nax.set_xlabel(\'Current Price ($)\')\nax.set_ylabel(\'Rating (★)\')\nax.set_title(\'Price vs. Rating — Bubble Size = Review Volume\', fontsize=14, fontweight=\'bold\')\nax.set_xlim(0, 1200)\nax.set_ylim(4.3, 4.9)\nplt.colorbar(scatter, label=\'Review Count\')\nplt.tight_layout()\nplt.savefig(\'figures/figure_002_price_rating_scatter.png\', dpi=150, bbox_inches=\'tight\')\nplt.show()'
})

# Cell 5: Price history trends
exec('''
top_6_asins = products.nlargest(6, 'review_count')['asin'].tolist()
top_history = price_history[price_history['asin'].isin(top_6_asins)].copy()

fig, ax = plt.subplots(figsize=(14, 8))
for asin in top_6_asins:
    sub = top_history[top_history['asin'] == asin]
    if not sub.empty:
        title = products[products['asin'] == asin]['title'].values[0][:30]
        ax.plot(sub['timestamp'], sub['price'], label=title, alpha=0.8, linewidth=2)
ax.set_xlabel('Date')
ax.set_ylabel('Price ($)')
ax.set_title('6-Month Price Tracking — Top Reviewed Electronics (Keepa Live)', fontsize=14, fontweight='bold')
ax.legend(loc='upper right', fontsize=9, ncol=2)
ax.xaxis.set_major_locator(plt.MaxNLocator(8))
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig('figures/figure_003_price_history_trends.png', dpi=150, bbox_inches='tight')
''')

nb01['cells'].append({
    'cell_type': 'code',
    'execution_count': 5,
    'metadata': {},
    'outputs': [make_image_output()],
    'source': 'top_6_asins = products.nlargest(6, \'review_count\')[\'asin\'].tolist()\ntop_history = price_history[price_history[\'asin\'].isin(top_6_asins)].copy()\n\nfig, ax = plt.subplots(figsize=(14, 8))\nfor asin in top_6_asins:\n    sub = top_history[top_history[\'asin\'] == asin]\n    if not sub.empty:\n        title = products[products[\'asin\'] == asin][\'title\'].values[0][:30]\n        ax.plot(sub[\'timestamp\'], sub[\'price\'], label=title, alpha=0.8, linewidth=2)\nax.set_xlabel(\'Date\')\nax.set_ylabel(\'Price ($)\')\nax.set_title(\'6-Month Price Tracking — Top Reviewed Electronics (Keepa Live)\', fontsize=14, fontweight=\'bold\')\nax.legend(loc=\'upper right\', fontsize=9, ncol=2)\nax.xaxis.set_major_locator(plt.MaxNLocator(8))\nplt.xticks(rotation=30)\nplt.tight_layout()\nplt.savefig(\'figures/figure_003_price_history_trends.png\', dpi=150, bbox_inches=\'tight\')\nplt.show()'
})

# Cell 6: Deal analysis
exec('''
fig, ax = plt.subplots(figsize=(12, 6))
deals_sorted = deals.sort_values('price_drop_pct', ascending=True)
colors = ['#d32f2f' if x > 25 else '#f57c00' if x > 20 else '#fbc02d' for x in deals_sorted['price_drop_pct']]
bars = ax.barh(deals_sorted['title'].str[:35], deals_sorted['price_drop_pct'], color=colors)
for bar, prev, curr in zip(bars, deals_sorted['previous_price'], deals_sorted['current_price']):
    ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
            f'${curr:.0f} (was ${prev:.0f})', va='center', fontsize=9)
ax.set_xlabel('Price Drop (%)')
ax.set_title('Active Deals — Electronics Price Drops (Keepa Live)', fontsize=14, fontweight='bold')
ax.set_xlim(0, deals['price_drop_pct'].max() + 8)
plt.tight_layout()
plt.savefig('figures/figure_004_active_deals.png', dpi=150, bbox_inches='tight')
''')

nb01['cells'].append({
    'cell_type': 'code',
    'execution_count': 6,
    'metadata': {},
    'outputs': [make_image_output()],
    'source': 'fig, ax = plt.subplots(figsize=(12, 6))\ndeals_sorted = deals.sort_values(\'price_drop_pct\', ascending=True)\ncolors = [\'#d32f2f\' if x > 25 else \'#f57c00\' if x > 20 else \'#fbc02d\' for x in deals_sorted[\'price_drop_pct\']]\nbars = ax.barh(deals_sorted[\'title\'].str[:35], deals_sorted[\'price_drop_pct\'], color=colors)\nfor bar, prev, curr in zip(bars, deals_sorted[\'previous_price\'], deals_sorted[\'current_price\']):\n    ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,\n            f\'${curr:.0f} (was ${prev:.0f})\', va=\'center\', fontsize=9)\nax.set_xlabel(\'Price Drop (%)\')\nax.set_title(\'Active Deals — Electronics Price Drops (Keepa Live)\', fontsize=14, fontweight=\'bold\')\nax.set_xlim(0, deals[\'price_drop_pct\'].max() + 8)\nplt.tight_layout()\nplt.savefig(\'figures/figure_004_active_deals.png\', dpi=150, bbox_inches=\'tight\')\nplt.show()'
})

# Cell 7: Historical reviews by year
exec('''
yearly = reviews.groupby('reviewYear').size()
fig, ax = plt.subplots(figsize=(12, 6))
ax.bar(yearly.index, yearly.values, color='steelblue', alpha=0.8)
ax.plot(yearly.index, yearly.values, color='darkred', marker='o', linewidth=2)
peak_year = yearly.idxmax()
peak_count = yearly.max()
ax.annotate(f'Peak: {peak_year}\\n{peak_count:,} reviews',
            xy=(peak_year, peak_count), xytext=(peak_year-2, peak_count+3000),
            arrowprops=dict(arrowstyle='->', color='darkred'),
            fontsize=10, color='darkred', fontweight='bold')
ax.set_xlabel('Year')
ax.set_ylabel('Review Count')
ax.set_title('Historical Review Volume — Amazon Electronics (UCSD 1999–2014)', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('figures/figure_005_historical_reviews_by_year.png', dpi=150, bbox_inches='tight')
''')

nb01['cells'].append({
    'cell_type': 'code',
    'execution_count': 7,
    'metadata': {},
    'outputs': [make_image_output()],
    'source': 'yearly = reviews.groupby(\'reviewYear\').size()\nfig, ax = plt.subplots(figsize=(12, 6))\nax.bar(yearly.index, yearly.values, color=\'steelblue\', alpha=0.8)\nax.plot(yearly.index, yearly.values, color=\'darkred\', marker=\'o\', linewidth=2)\npeak_year = yearly.idxmax()\npeak_count = yearly.max()\nax.annotate(f\'Peak: {peak_year}\\n{peak_count:,} reviews\',\n            xy=(peak_year, peak_count), xytext=(peak_year-2, peak_count+3000),\n            arrowprops=dict(arrowstyle=\'->\', color=\'darkred\'),\n            fontsize=10, color=\'darkred\', fontweight=\'bold\')\nax.set_xlabel(\'Year\')\nax.set_ylabel(\'Review Count\')\nax.set_title(\'Historical Review Volume — Amazon Electronics (UCSD 1999–2014)\', fontsize=14, fontweight=\'bold\')\nplt.tight_layout()\nplt.savefig(\'figures/figure_005_historical_reviews_by_year.png\', dpi=150, bbox_inches=\'tight\')\nplt.show()'
})

# Cell 8: Rating comparison
exec('''
fig, ax = plt.subplots(figsize=(12, 6))
hist_ratings = reviews['overall'].value_counts().sort_index()
hist_pct = hist_ratings / hist_ratings.sum() * 100
live_ratings = []
for _, row in products.iterrows():
    live_ratings.extend([row['rating']] * int(row['review_count'] / 1000))
live_series = pd.Series(live_ratings)
x = np.arange(1, 6)
width = 0.35
bars1 = ax.bar(x - width/2, [hist_pct.get(i, 0) for i in x], width, label='Historical (UCSD 1999–2014)', color='steelblue', alpha=0.8)
bars2 = ax.bar(x + width/2, [live_series.round().value_counts().get(i, 0) / len(live_series) * 100 for i in x], width,
                label='Live (Keepa 2025)', color='coral', alpha=0.8)
ax.set_xlabel('Star Rating')
ax.set_ylabel('Percentage (%)')
ax.set_title('Rating Distribution — Historical vs. Live Amazon Electronics', fontsize=14, fontweight='bold')
ax.legend()
ax.set_xticks(x)
plt.tight_layout()
plt.savefig('figures/figure_006_rating_comparison.png', dpi=150, bbox_inches='tight')
''')

nb01['cells'].append({
    'cell_type': 'code',
    'execution_count': 8,
    'metadata': {},
    'outputs': [make_image_output()],
    'source': 'fig, ax = plt.subplots(figsize=(12, 6))\nhist_ratings = reviews[\'overall\'].value_counts().sort_index()\nhist_pct = hist_ratings / hist_ratings.sum() * 100\nlive_ratings = []\nfor _, row in products.iterrows():\n    live_ratings.extend([row[\'rating\']] * int(row[\'review_count\'] / 1000))\nlive_series = pd.Series(live_ratings)\nx = np.arange(1, 6)\nwidth = 0.35\nbars1 = ax.bar(x - width/2, [hist_pct.get(i, 0) for i in x], width, label=\'Historical (UCSD 1999–2014)\', color=\'steelblue\', alpha=0.8)\nbars2 = ax.bar(x + width/2, [live_series.round().value_counts().get(i, 0) / len(live_series) * 100 for i in x], width,\n                label=\'Live (Keepa 2025)\', color=\'coral\', alpha=0.8)\nax.set_xlabel(\'Star Rating\')\nax.set_ylabel(\'Percentage (%)\')\nax.set_title(\'Rating Distribution — Historical vs. Live Amazon Electronics\', fontsize=14, fontweight=\'bold\')\nax.legend()\nax.set_xticks(x)\nplt.tight_layout()\nplt.savefig(\'figures/figure_006_rating_comparison.png\', dpi=150, bbox_inches=\'tight\')\nplt.show()'
})

# Cell 9: Summary
summary_lines = [
    '┌─────────────────────────────────────────────────────────────┐',
    '│  LIVE KEEPA DATA (Electronics Bestsellers)                │',
    '├─────────────────────────────────────────────────────────────┤',
    f'│  Products tracked:        {len(products):<36}│',
    f'│  Brands represented:      {products["brand"].nunique()} (Apple, Samsung, Sony, etc.)   │',
    f'│  Price range:             ${products["current_price"].min():.2f} – ${products["current_price"].max():.2f}              │',
    f'│  Median price:            ${products["current_price"].median():.2f}                          │',
    f'│  Avg rating:              {products["rating"].mean():.2f} ★                         │',
    f'│  Total review volume:     {products["review_count"].sum()/1e6:.2f}M (across {len(products)} products)       │',
    f'│  Active deals:            {len(deals)} (avg drop: {deals["price_drop_pct"].mean():.1f}%)            │',
    f'│  Price history span:      180 days ({len(price_history):,} records)        │',
    '└─────────────────────────────────────────────────────────────┘',
    '',
    '┌─────────────────────────────────────────────────────────────┐',
    '│  HISTORICAL UCSD REVIEWS (Electronics 5-core)               │',
    '├─────────────────────────────────────────────────────────────┤',
    f'│  Total reviews:           {len(reviews):<36}│',
    f'│  Unique products:         {reviews["asin"].nunique():<36}│',
    f'│  Unique reviewers:        {reviews["reviewerID"].nunique():<36}│',
    f'│  Date range:              {reviews["reviewDate"].min().date()} → {reviews["reviewDate"].max().date()}         │',
    f'│  Avg rating:              {reviews["overall"].mean():.2f} ★                         │',
    f'│  5-star dominance:        {(reviews["overall"]==5).mean()*100:.1f}%                            │',
    f'│  Helpfulness rate:        {(reviews[reviews["helpful_total"]>0]["helpful_upvotes"].sum()/reviews[reviews["helpful_total"]>0]["helpful_total"].sum()*100):.1f}%                            │',
    f'│  Peak year:               {yearly.idxmax()} ({yearly.max():,} reviews)   │',
    '└─────────────────────────────────────────────────────────────┘'
]

nb01['cells'].append({
    'cell_type': 'code',
    'execution_count': 9,
    'metadata': {},
    'outputs': [make_text_output(summary_lines)],
    'source': 'yearly = reviews.groupby(\'reviewYear\').size()\nprint("┌─────────────────────────────────────────────────────────────┐")\nprint("│  LIVE KEEPA DATA (Electronics Bestsellers)                │")\nprint("├─────────────────────────────────────────────────────────────┤")\nprint(f"│  Products tracked:        {len(products):<36}│")\nprint(f"│  Brands represented:      {products[\'brand\'].nunique()} (Apple, Samsung, Sony, etc.)   │")\nprint(f"│  Price range:             ${products[\'current_price\'].min():.2f} – ${products[\'current_price\'].max():.2f}              │")\nprint(f"│  Median price:            ${products[\'current_price\'].median():.2f}                          │")\nprint(f"│  Avg rating:              {products[\'rating\'].mean():.2f} ★                         │")\nprint(f"│  Total review volume:     {products[\'review_count\'].sum()/1e6:.2f}M (across {len(products)} products)       │")\nprint(f"│  Active deals:            {len(deals)} (avg drop: {deals[\'price_drop_pct\'].mean():.1f}%)            │")\nprint(f"│  Price history span:      180 days ({len(price_history):,} records)        │")\nprint("└─────────────────────────────────────────────────────────────┘")\nprint()\nprint("┌─────────────────────────────────────────────────────────────┐")\nprint("│  HISTORICAL UCSD REVIEWS (Electronics 5-core)               │")\nprint("├─────────────────────────────────────────────────────────────┤")\nprint(f"│  Total reviews:           {len(reviews):<36}│")\nprint(f"│  Unique products:         {reviews[\'asin\'].nunique():<36}│")\nprint(f"│  Unique reviewers:        {reviews[\'reviewerID\'].nunique():<36}│")\nprint(f"│  Date range:              {reviews[\'reviewDate\'].min().date()} → {reviews[\'reviewDate\'].max().date()}         │")\nprint(f"│  Avg rating:              {reviews[\'overall\'].mean():.2f} ★                         │")\nprint(f"│  5-star dominance:        {(reviews[\'overall\']==5).mean()*100:.1f}%                            │")\nprint(f"│  Helpfulness rate:        {(reviews[reviews[\'helpful_total\']>0][\'helpful_upvotes\'].sum()/reviews[reviews[\'helpful_total\']>0][\'helpful_total\'].sum()*100):.1f}%                            │")\nprint(f"│  Peak year:               {yearly.idxmax()} ({yearly.max():,} reviews)   │")\nprint("└─────────────────────────────────────────────────────────────┘")'
})

# Save notebook 01
with open('notebooks/01_exploratory_analysis.ipynb', 'w') as f:
    json.dump(nb01, f, indent=1)

print('Notebook 01 saved successfully')
