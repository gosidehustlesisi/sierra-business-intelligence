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
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Load data
data_dir = Path('data')
products_files = sorted(data_dir.glob('keepa_products_*.csv'))
history_files = sorted(data_dir.glob('keepa_price_history_*.csv'))
deals_files = sorted(data_dir.glob('keepa_deals_*.csv'))

products = pd.read_csv(products_files[-1]) if products_files else pd.DataFrame()
price_history = pd.read_csv(history_files[-1]) if history_files else pd.DataFrame()
deals = pd.read_csv(deals_files[-1]) if deals_files else pd.DataFrame()

price_history['timestamp'] = pd.to_datetime(price_history['timestamp'])

print('Data loaded for dashboard notebook')

Path('figures').mkdir(exist_ok=True)

def fig_to_html_base64(fig):
    html = fig.to_html(include_plotlyjs='cdn', full_html=False)
    return base64.b64encode(html.encode('utf-8')).decode('utf-8')

def make_plotly_image_output(fig, suffix="plotly"):
    # Save as PNG for figures/ extraction
    title_text = fig.layout.title.text if hasattr(fig.layout.title, 'text') else str(fig.layout.title)
    safe_title = title_text[:30].replace(" ", "_").replace("/", "_").replace(":", "_")
    png_path = f'figures/figure_{suffix}_{safe_title}.png'
    # Use kaleido for static export if available
    try:
        fig.write_image(png_path, width=1200, height=600, scale=2)
    except Exception:
        # Fallback: save HTML only
        pass
    # Also save interactive HTML
    html_path = png_path.replace('.png', '.html')
    fig.write_html(html_path, include_plotlyjs='cdn')
    return {
        'output_type': 'display_data',
        'data': {
            'text/html': [fig.to_html(include_plotlyjs='cdn', full_html=False)],
            'text/plain': ['<plotly.graph_objs._figure.Figure>']
        },
        'metadata': {}
    }

def make_text_output(lines):
    return {
        'output_type': 'stream',
        'name': 'stdout',
        'text': [line + '\n' for line in lines]
    }

nb03 = {
    'cells': [],
    'metadata': {'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
                 'language_info': {'name': 'python', 'version': '3.12.0'}},
    'nbformat': 4, 'nbformat_minor': 4
}

nb03['cells'].append({
    'cell_type': 'markdown',
    'metadata': {},
    'source': '# 03 — Executive Dashboard (Plotly Interactive)\n\n**Interactive visualizations for Amazon Electronics price intelligence.**\n\n**Data:** Keepa live price data + historical UCSD review context\n\n**Generated:** 2026-05-17'
})

nb03['cells'].append({
    'cell_type': 'code',
    'execution_count': 1,
    'metadata': {},
    'outputs': [],
    'source': 'import pandas as pd\nimport numpy as np\nimport plotly.express as px\nimport plotly.graph_objects as go\nfrom plotly.subplots import make_subplots\nfrom pathlib import Path\n\ndata_dir = Path("data")\nproducts = pd.read_csv(sorted(data_dir.glob("keepa_products_*.csv"))[-1])\nprice_history = pd.read_csv(sorted(data_dir.glob("keepa_price_history_*.csv"))[-1])\ndeals = pd.read_csv(sorted(data_dir.glob("keepa_deals_*.csv"))[-1])\nprice_history["timestamp"] = pd.to_datetime(price_history["timestamp"])\nprint("Plotly data ready")'
})

# Chart 1: Executive Summary KPIs
exec('''
brand_share = products.groupby('brand')['review_count'].sum().reset_index()
brand_share['share_pct'] = brand_share['review_count'] / brand_share['review_count'].sum() * 100

fig1 = make_subplots(
    rows=2, cols=3,
    specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
           [{"type": "pie", "colspan": 3}, None, None]],
    subplot_titles=("Products Tracked", "Active Deals", "Avg Rating", "Market Share by Review Volume")
)

fig1.add_trace(go.Indicator(mode="number", value=len(products), number={'font': {'size': 48}}), row=1, col=1)
fig1.add_trace(go.Indicator(mode="number", value=len(deals), number={'font': {'size': 48}, 'suffix': "% avg drop"}), row=1, col=2)
fig1.add_trace(go.Indicator(mode="number", value=round(products['rating'].mean(), 2), number={'font': {'size': 48}, 'suffix': " ★"}), row=1, col=3)
fig1.add_trace(go.Pie(labels=brand_share['brand'], values=brand_share['share_pct'], hole=0.4), row=2, col=1)

fig1.update_layout(height=700, title_text="Executive KPI Dashboard — Amazon Electronics Intelligence", title_font_size=18)
''')

nb03['cells'].append({
    'cell_type': 'markdown',
    'metadata': {},
    'source': '## Chart 1 — Executive KPI Summary'
})
nb03['cells'].append({
    'cell_type': 'code',
    'execution_count': 2,
    'metadata': {},
    'outputs': [make_plotly_image_output(fig1, "001")],
    'source': 'brand_share = products.groupby("brand")["review_count"].sum().reset_index()\nbrand_share["share_pct"] = brand_share["review_count"] / brand_share["review_count"].sum() * 100\n\nfig1 = make_subplots(\n    rows=2, cols=3,\n    specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],\n           [{"type": "pie", "colspan": 3}, None, None]],\n    subplot_titles=("Products Tracked", "Active Deals", "Avg Rating", "Market Share by Review Volume")\n)\nfig1.add_trace(go.Indicator(mode="number", value=len(products), number={"font": {"size": 48}}), row=1, col=1)\nfig1.add_trace(go.Indicator(mode="number", value=len(deals), number={"font": {"size": 48}, "suffix": "% avg drop"}), row=1, col=2)\nfig1.add_trace(go.Indicator(mode="number", value=round(products["rating"].mean(), 2), number={"font": {"size": 48}, "suffix": " ★"}), row=1, col=3)\nfig1.add_trace(go.Pie(labels=brand_share["brand"], values=brand_share["share_pct"], hole=0.4), row=2, col=1)\nfig1.update_layout(height=700, title_text="Executive KPI Dashboard — Amazon Electronics Intelligence", title_font_size=18)\nfig1.show()'
})

# Chart 2: Interactive Price Tracker
exec('''
top_asins = products.nlargest(5, 'review_count')['asin'].tolist()
top_history = price_history[price_history['asin'].isin(top_asins)].copy()

fig2 = px.line(top_history, x='timestamp', y='price', color='title',
               title='Live Price Tracker — Top 5 Products by Review Volume',
               labels={'price': 'Price ($)', 'timestamp': 'Date'},
               height=500)
fig2.update_layout(legend=dict(orientation='h', yanchor='bottom', y=-0.3))
''')

nb03['cells'].append({
    'cell_type': 'markdown',
    'metadata': {},
    'source': '## Chart 2 — Live Price Tracker (Interactive)'
})
nb03['cells'].append({
    'cell_type': 'code',
    'execution_count': 3,
    'metadata': {},
    'outputs': [make_plotly_image_output(fig2, "002")],
    'source': 'top_asins = products.nlargest(5, "review_count")["asin"].tolist()\ntop_history = price_history[price_history["asin"].isin(top_asins)].copy()\nfig2 = px.line(top_history, x="timestamp", y="price", color="title",\n               title="Live Price Tracker — Top 5 Products by Review Volume",\n               labels={"price": "Price ($)", "timestamp": "Date"},\n               height=500)\nfig2.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.3))\nfig2.show()'
})

# Chart 3: Deal Opportunities Heatmap
exec('''
products['price_tier'] = pd.cut(products['current_price'], bins=[0, 50, 150, 400, 2000], labels=['Budget', 'Mid', 'Premium', 'Luxury'])
products['discount_pct'] = ((products['list_price'] - products['current_price']) / products['list_price'] * 100).fillna(0)

heatmap_data = products.groupby(['brand', 'price_tier']).agg(
    avg_discount=('discount_pct', 'mean'),
    count=('asin', 'size')
).reset_index()
heatmap_pivot = heatmap_data.pivot(index='brand', columns='price_tier', values='avg_discount').fillna(0)

fig3 = px.imshow(heatmap_pivot, text_auto='.1f', aspect='auto',
                  title='Average Discount % by Brand × Price Tier',
                  labels=dict(x='Price Tier', y='Brand', color='Discount %'),
                  height=400)
''')

nb03['cells'].append({
    'cell_type': 'markdown',
    'metadata': {},
    'source': '## Chart 3 — Deal Opportunities Heatmap'
})
nb03['cells'].append({
    'cell_type': 'code',
    'execution_count': 4,
    'metadata': {},
    'outputs': [make_plotly_image_output(fig3, "003")],
    'source': 'products["price_tier"] = pd.cut(products["current_price"], bins=[0, 50, 150, 400, 2000], labels=["Budget", "Mid", "Premium", "Luxury"])\nproducts["discount_pct"] = ((products["list_price"] - products["current_price"]) / products["list_price"] * 100).fillna(0)\nheatmap_data = products.groupby(["brand", "price_tier"]).agg(\n    avg_discount=("discount_pct", "mean"),\n    count=("asin", "size")\n).reset_index()\nheatmap_pivot = heatmap_data.pivot(index="brand", columns="price_tier", values="avg_discount").fillna(0)\nfig3 = px.imshow(heatmap_pivot, text_auto=".1f", aspect="auto",\n                  title="Average Discount % by Brand × Price Tier",\n                  labels=dict(x="Price Tier", y="Brand", color="Discount %"),\n                  height=400)\nfig3.show()'
})

# Chart 4: Price Volatility Scatter
exec('''
vol_data = price_history.groupby('asin').agg(
    price_std=('price', 'std'),
    price_mean=('price', 'mean'),
    observations=('price', 'size')
).reset_index()
vol_data = vol_data.merge(products[['asin', 'title', 'brand', 'rating', 'review_count']], on='asin')
vol_data['cv'] = vol_data['price_std'] / vol_data['price_mean'] * 100

fig4 = px.scatter(vol_data, x='price_mean', y='cv', size='review_count', color='brand',
                  hover_data=['title'], text='brand',
                  title='Price Volatility Analysis — Coefficient of Variation vs. Average Price',
                  labels={'price_mean': 'Average Price ($)', 'cv': 'Price Volatility (CV %)', 'review_count': 'Reviews'},
                  height=500)
fig4.update_traces(textposition='top center')
''')

nb03['cells'].append({
    'cell_type': 'markdown',
    'metadata': {},
    'source': '## Chart 4 — Price Volatility Analysis'
})
nb03['cells'].append({
    'cell_type': 'code',
    'execution_count': 5,
    'metadata': {},
    'outputs': [make_plotly_image_output(fig4, "004")],
    'source': 'vol_data = price_history.groupby("asin").agg(\n    price_std=("price", "std"),\n    price_mean=("price", "mean"),\n    observations=("price", "size")\n).reset_index()\nvol_data = vol_data.merge(products[["asin", "title", "brand", "rating", "review_count"]], on="asin")\nvol_data["cv"] = vol_data["price_std"] / vol_data["price_mean"] * 100\nfig4 = px.scatter(vol_data, x="price_mean", y="cv", size="review_count", color="brand",\n                  hover_data=["title"], text="brand",\n                  title="Price Volatility Analysis — Coefficient of Variation vs. Average Price",\n                  labels={"price_mean": "Average Price ($)", "cv": "Price Volatility (CV %)", "review_count": "Reviews"},\n                  height=500)\nfig4.update_traces(textposition="top center")\nfig4.show()'
})

# Chart 5: Treemap — Market Hierarchy
exec('''
fig5 = px.treemap(products, path=['brand', 'title'], values='review_count',
                  color='current_price', color_continuous_scale='RdYlGn_r',
                  title='Market Hierarchy — Brand × Product (Size = Review Volume, Color = Price)',
                  height=600)
''')

nb03['cells'].append({
    'cell_type': 'markdown',
    'metadata': {},
    'source': '## Chart 5 — Market Hierarchy Treemap'
})
nb03['cells'].append({
    'cell_type': 'code',
    'execution_count': 6,
    'metadata': {},
    'outputs': [make_plotly_image_output(fig5, "005")],
    'source': 'fig5 = px.treemap(products, path=["brand", "title"], values="review_count",\n                  color="current_price", color_continuous_scale="RdYlGn_r",\n                  title="Market Hierarchy — Brand × Product (Size = Review Volume, Color = Price)",\n                  height=600)\nfig5.show()'
})

# Chart 6: Deal Timeline
exec('''
if not deals.empty:
    deals_sorted = deals.sort_values('price_drop_pct', ascending=False)
    fig6 = go.Figure()
    fig6.add_trace(go.Bar(
        x=deals_sorted['title'].str[:30],
        y=deals_sorted['price_drop_pct'],
        marker_color=['#d32f2f' if x > 25 else '#f57c00' if x > 20 else '#fbc02d' for x in deals_sorted['price_drop_pct']],
        text=[f"${row['current_price']:.0f}" for _, row in deals_sorted.iterrows()],
        textposition='outside'
    ))
    fig6.update_layout(
        title='Active Deals — Price Drop Percentage',
        xaxis_title='Product',
        yaxis_title='Price Drop (%)',
        height=500,
        xaxis_tickangle=-45
    )
else:
    fig6 = go.Figure()
    fig6.add_annotation(text="No active deals detected", showarrow=False, font_size=20)
''')

nb03['cells'].append({
    'cell_type': 'markdown',
    'metadata': {},
    'source': '## Chart 6 — Active Deals Timeline'
})
nb03['cells'].append({
    'cell_type': 'code',
    'execution_count': 7,
    'metadata': {},
    'outputs': [make_plotly_image_output(fig6, "006")],
    'source': 'if not deals.empty:\n    deals_sorted = deals.sort_values("price_drop_pct", ascending=False)\n    fig6 = go.Figure()\n    fig6.add_trace(go.Bar(\n        x=deals_sorted["title"].str[:30],\n        y=deals_sorted["price_drop_pct"],\n        marker_color=["#d32f2f" if x > 25 else "#f57c00" if x > 20 else "#fbc02d" for x in deals_sorted["price_drop_pct"]],\n        text=[f"${row[\'current_price\']:.0f}" for _, row in deals_sorted.iterrows()],\n        textposition="outside"\n    ))\n    fig6.update_layout(\n        title="Active Deals — Price Drop Percentage",\n        xaxis_title="Product",\n        yaxis_title="Price Drop (%)",\n        height=500,\n        xaxis_tickangle=-45\n    )\nelse:\n    fig6 = go.Figure()\n    fig6.add_annotation(text="No active deals detected", showarrow=False, font_size=20)\nfig6.show()'
})

# Summary
summary_lines = [
    '=== EXECUTIVE DASHBOARD SUMMARY ===',
    f'Total products tracked: {len(products)}',
    f'Brands monitored: {products["brand"].nunique()}',
    f'Price history data points: {len(price_history):,}',
    f'Active deals: {len(deals)}',
    f'Price range: ${products["current_price"].min():.2f} – ${products["current_price"].max():.2f}',
    f'Average rating: {products["rating"].mean():.2f} ★',
    f'Total review volume: {products["review_count"].sum():,}',
    '',
    'Interactive HTML files saved to figures/ for standalone viewing.'
]

nb03['cells'].append({
    'cell_type': 'code',
    'execution_count': 8,
    'metadata': {},
    'outputs': [make_text_output(summary_lines)],
    'source': 'print("=== EXECUTIVE DASHBOARD SUMMARY ===")\nprint(f"Total products tracked: {len(products)}")\nprint(f"Brands monitored: {products[\'brand\'].nunique()}")\nprint(f"Price history data points: {len(price_history):,}")\nprint(f"Active deals: {len(deals)}")\nprint(f"Price range: ${products[\'current_price\'].min():.2f} – ${products[\'current_price\'].max():.2f}")\nprint(f"Average rating: {products[\'rating\'].mean():.2f} ★")\nprint(f"Total review volume: {products[\'review_count\'].sum():,}")\nprint()\nprint("Interactive HTML files saved to figures/ for standalone viewing.")'
})

# Save
with open('notebooks/03_executive_dashboard.ipynb', 'w') as f:
    json.dump(nb03, f, indent=1)

print('Notebook 03 saved successfully')
