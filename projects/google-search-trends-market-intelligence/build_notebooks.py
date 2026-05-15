"""
Build and execute all three notebooks with real data outputs.
"""
import os
import json
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
from scipy import stats
from scipy.signal import find_peaks
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings("ignore")

# For notebook generation
import nbformat as nbf
from nbconvert.preprocessors import ExecutePreprocessor

DATA_DIR = "data"

# ============================================================
# NOTEBOOK 01: Exploratory Analysis
# ============================================================
nb01 = nbf.v4.new_notebook()
nb01.cells = []

cells_01 = [
    ("markdown", """# 01 — Exploratory Analysis: Google Search Trends

**Dataset:** Real Google Trends data via pytrends (live API)  
**Topics:** 14 keywords across Tech, Health, Finance  
**Timeframe:** Last 5 years (weekly granularity)  
**Author:** Sierra Napier | e3-ai.com
"""),
    ("code", "import pandas as pd\nimport numpy as np\nimport plotly.express as px\nimport plotly.graph_objects as go\nfrom plotly.subplots import make_subplots\nfrom scipy import stats\nfrom scipy.signal import find_peaks\nimport warnings\nwarnings.filterwarnings('ignore')\n\ndf_ww = pd.read_csv('data/interest_over_time_worldwide.csv', index_col=0, parse_dates=True)\ndf_us = pd.read_csv('data/interest_over_time_us.csv', index_col=0, parse_dates=True)\ndf_region = pd.read_csv('data/interest_by_region_us.csv')\n\nprint(f'Worldwide time series: {df_ww.shape}')\nprint(f'US time series: {df_us.shape}')\nprint(f'US regional: {df_region.shape}')\nprint(f'Keywords: {list(df_ww.columns)}')"),
    ("markdown", "## 1.1 Overall Trend Overview — Worldwide"),
    ("code", "fig = make_subplots(rows=3, cols=1, subplot_titles=('Tech', 'Health', 'Finance'), vertical_spacing=0.08)\n\ntech = ['AI', 'machine learning', 'ChatGPT', 'Bitcoin', 'Tesla', 'Netflix', 'Amazon']\nhealth = ['telehealth', 'mental health', 'fitness']\nfinance = ['inflation', 'recession', 'stock market', 'crypto']\n\nfor kw in tech:\n    fig.add_trace(go.Scatter(x=df_ww.index, y=df_ww[kw], name=kw, mode='lines'), row=1, col=1)\nfor kw in health:\n    fig.add_trace(go.Scatter(x=df_ww.index, y=df_ww[kw], name=kw, mode='lines'), row=2, col=1)\nfor kw in finance:\n    fig.add_trace(go.Scatter(x=df_ww.index, y=df_ww[kw], name=kw, mode='lines'), row=3, col=1)\n\nfig.update_layout(height=900, title_text='Worldwide Search Interest (2021–2026)', showlegend=False)\nfig.show()"),
    ("markdown", "## 1.2 Peak Detection — When did each topic spike?"),
    ("code", "peaks = {}\nfor col in df_ww.columns:\n    p, props = find_peaks(df_ww[col], height=50, distance=10)\n    if len(p) > 0:\n        peaks[col] = df_ww.index[p].strftime('%Y-%m-%d').tolist()\n    else:\n        p2, _ = find_peaks(df_ww[col], height=20, distance=10)\n        peaks[col] = df_ww.index[p2].strftime('%Y-%m-%d').tolist() if len(p2) > 0 else []\n\npeak_df = pd.DataFrame([(k, ', '.join(v[:3])) for k, v in peaks.items() if v], columns=['Keyword', 'Top Peaks (dates)'])\nprint(peak_df.to_string(index=False))"),
    ("markdown", "## 1.3 Correlation Matrix — Which topics move together?"),
    ("code", "corr = df_ww.corr()\nfig = px.imshow(corr, text_auto='.2f', aspect='auto', color_continuous_scale='RdBu_r',\n                title='Topic Correlation Matrix (Worldwide)', zmin=-1, zmax=1)\nfig.update_layout(height=700)\nfig.show()"),
    ("markdown", "## 1.4 Growth Rate — YoY change by category"),
    ("code", "# Calculate YoY growth using 52-week windows\ngrowth = {}\nfor col in df_ww.columns:\n    recent = df_ww[col].iloc[-52:].mean()\n    prior = df_ww[col].iloc[-104:-52].mean()\n    if prior > 0:\n        growth[col] = round((recent - prior) / prior * 100, 1)\n    else:\n        growth[col] = None\n\ngrowth_df = pd.DataFrame(list(growth.items()), columns=['Keyword', 'YoY_Growth_%']).sort_values('YoY_Growth_%', ascending=False)\nfig = px.bar(growth_df, x='Keyword', y='YoY_Growth_%', color='YoY_Growth_%',\n             color_continuous_scale='RdYlGn', title='YoY Growth Rate (%) — 52-week avg')\nfig.show()"),
    ("markdown", "## 1.5 Regional Interest Map — US States"),
    ("code", "pivot_region = df_region.pivot(index='geoName', columns='keyword', values='interest').fillna(0)\nfig = px.choropleth(df_region, locations='geoCode', color='interest',\n                    hover_name='geoName', scope='usa',\n                    animation_frame='keyword',\n                    color_continuous_scale='Plasma',\n                    title='Search Interest by US State (animated by keyword)')\nfig.update_layout(height=500)\nfig.show()"),
    ("markdown", "## 1.6 Category Summaries"),
    ("code", "summary = df_ww.describe().T[['mean', 'std', 'min', 'max']].round(2)\nsummary['category'] = summary.index.map(lambda x: 'Tech' if x in tech else ('Health' if x in health else 'Finance'))\nprint(summary.sort_values('mean', ascending=False))"),
]

for cell_type, source in cells_01:
    if cell_type == "markdown":
        nb01.cells.append(nbf.v4.new_markdown_cell(source))
    else:
        nb01.cells.append(nbf.v4.new_code_cell(source))

# ============================================================
# NOTEBOOK 02: Market Intelligence SQL
# ============================================================
nb02 = nbf.v4.new_notebook()
nb02.cells = []

cells_02 = [
    ("markdown", """# 02 — Market Intelligence: 10 Business SQL Queries

Using `pandasql` to run SQL on in-memory Google Trends data.

**Dataset:** Real Google Trends (pytrends API) — 14 keywords, 5 years, worldwide + US regional.
"""),
    ("code", "import pandas as pd\nimport pandasql as ps\nimport numpy as np\nfrom datetime import datetime\n\ndf_ww = pd.read_csv('data/interest_over_time_worldwide.csv', index_col=0, parse_dates=True).reset_index()\ndf_ww.columns = ['date'] + list(df_ww.columns[1:])\ndf_us = pd.read_csv('data/interest_over_time_us.csv', index_col=0, parse_dates=True).reset_index()\ndf_us.columns = ['date'] + list(df_us.columns[1:])\ndf_region = pd.read_csv('data/interest_by_region_us.csv')\n\n# Melt to long format for SQL\nww_long = df_ww.melt(id_vars=['date'], var_name='keyword', value_name='interest')\nus_long = df_us.melt(id_vars=['date'], var_name='keyword', value_name='interest')\n\nprint(f'ww_long: {ww_long.shape}, us_long: {us_long.shape}, region: {df_region.shape}')"),
    ("markdown", "## Q1 — Topic Interest Ranking by Volume & Growth Rate"),
    ("code", "q1 = '''\nSELECT \n    keyword,\n    ROUND(AVG(interest), 2) as avg_interest,\n    ROUND(MAX(interest), 2) as peak_interest,\n    ROUND(AVG(CASE WHEN date >= date('now', '-1 year') THEN interest END), 2) as recent_avg,\n    ROUND(AVG(CASE WHEN date >= date('now', '-2 year') AND date < date('now', '-1 year') THEN interest END), 2) as prior_avg\nFROM ww_long\nGROUP BY keyword\nORDER BY avg_interest DESC\n'''\nprint(ps.sqldf(q1, locals()).to_string(index=False))"),
    ("markdown", "## Q2 — Regional Interest Heatmap (top state per topic)"),
    ("code", "q2 = '''\nSELECT keyword, geoName, interest\nFROM (\n    SELECT keyword, geoName, interest,\n           ROW_NUMBER() OVER (PARTITION BY keyword ORDER BY interest DESC) as rn\n    FROM df_region\n)\nWHERE rn = 1\nORDER BY interest DESC\n'''\nprint(ps.sqldf(q2, locals()).to_string(index=False))"),
    ("markdown", "## Q3 — Emerging Topic Detection (growth >100% YoY)"),
    ("code", "# Compute YoY growth in a temp table\nww_long['year'] = ww_long['date'].dt.year\nyearly = ww_long.groupby(['keyword', 'year'])['interest'].mean().reset_index()\nyearly['prior'] = yearly.groupby('keyword')['interest'].shift(1)\nyearly['growth_pct'] = ((yearly['interest'] - yearly['prior']) / yearly['prior'] * 100).round(1)\n\nq3 = '''\nSELECT keyword, year, ROUND(interest, 2) as avg_interest, growth_pct\nFROM yearly\nWHERE growth_pct > 100 AND year >= 2022\nORDER BY growth_pct DESC\nLIMIT 15\n'''\nprint(ps.sqldf(q3, locals()).to_string(index=False))"),
    ("markdown", "## Q4 — Trend Correlation Matrix (SQL pivot)"),
    ("code", "# Self-join to compute correlations\ncorr_pairs = []\nkeywords = ww_long['keyword'].unique()\nfor i, a in enumerate(keywords):\n    for b in keywords[i+1:]:\n        merged = ww_long[ww_long['keyword'] == a][['date', 'interest']].merge(\n            ww_long[ww_long['keyword'] == b][['date', 'interest']], on='date', suffixes=('_a', '_b')\n        )\n        if len(merged) > 10:\n            r = np.corrcoef(merged['interest_a'], merged['interest_b'])[0, 1]\n            corr_pairs.append({'topic_a': a, 'topic_b': b, 'correlation': round(r, 3)})\ncorr_df = pd.DataFrame(corr_pairs)\nprint(corr_df.sort_values('correlation', ascending=False).head(15).to_string(index=False))"),
    ("markdown", "## Q5 — Seasonal Pattern Detection (monthly aggregation)"),
    ("code", "ww_long['month'] = ww_long['date'].dt.month\nseasonal = ww_long.groupby(['keyword', 'month'])['interest'].mean().reset_index()\n\nq5 = '''\nSELECT keyword, month, ROUND(interest, 2) as avg_interest\nFROM seasonal\nWHERE keyword IN ('fitness', 'mental health', 'crypto', 'AI')\nORDER BY keyword, month\n'''\nprint(ps.sqldf(q5, locals()).to_string(index=False))"),
    ("markdown", "## Q6 — Event-Driven Spike Analysis (weeks with >3σ moves)"),
    ("code", "# Z-score based spike detection\nspike_data = []\nfor kw in ww_long['keyword'].unique():\n    sub = ww_long[ww_long['keyword'] == kw].sort_values('date')\n    sub['rolling_mean'] = sub['interest'].rolling(12).mean()\n    sub['rolling_std'] = sub['interest'].rolling(12).std()\n    sub['zscore'] = (sub['interest'] - sub['rolling_mean']) / sub['rolling_std']\n    spikes = sub[sub['zscore'] > 3]\n    for _, row in spikes.iterrows():\n        spike_data.append({'keyword': kw, 'date': row['date'].strftime('%Y-%m-%d'), 'interest': row['interest'], 'zscore': round(row['zscore'], 2)})\nspike_df = pd.DataFrame(spike_data)\nprint(spike_df.head(15).to_string(index=False) if len(spike_df) > 0 else 'No extreme spikes (>3σ) detected in this window.')"),
    ("markdown", "## Q7 — Category Lifecycle: Early Growth → Peak → Decline"),
    ("code", "lifecycle = []\nfor kw in ww_long['keyword'].unique():\n    sub = ww_long[ww_long['keyword'] == kw].sort_values('date')\n    peak_idx = sub['interest'].idxmax()\n    peak_date = sub.loc[peak_idx, 'date']\n    peak_val = sub.loc[peak_idx, 'interest']\n    early = sub[sub['date'] < peak_date]['interest'].mean() if (sub['date'] < peak_date).any() else 0\n    late = sub[sub['date'] > peak_date]['interest'].mean() if (sub['date'] > peak_date).any() else 0\n    lifecycle.append({'keyword': kw, 'peak_date': peak_date.strftime('%Y-%m-%d'), 'peak_interest': peak_val,\n                      'early_avg': round(early, 1), 'late_avg': round(late, 1),\n                      'trend': 'Rising' if late > early * 1.1 else ('Declining' if late < early * 0.9 else 'Stable')})\nlifecycle_df = pd.DataFrame(lifecycle).sort_values('peak_date')\nprint(lifecycle_df.to_string(index=False))"),
    ("markdown", "## Q8 — Cross-Category Opportunity (low competition, high growth)"),
    ("code", "# Compute mean (proxy for competition) and recent YoY growth\nopp = []\nfor kw in ww_long['keyword'].unique():\n    sub = ww_long[ww_long['keyword'] == kw].sort_values('date')\n    mean_i = sub['interest'].mean()\n    recent = sub['interest'].iloc[-52:].mean()\n    prior = sub['interest'].iloc[-104:-52].mean() if len(sub) >= 104 else sub['interest'].iloc[:52].mean()\n    growth = ((recent - prior) / prior * 100) if prior > 0 else 0\n    opp.append({'keyword': kw, 'mean_interest': round(mean_i, 1), 'recent_growth_pct': round(growth, 1)})\nopp_df = pd.DataFrame(opp)\nopp_df['opportunity_score'] = (opp_df['recent_growth_pct'] / (opp_df['mean_interest'] + 1)).round(2)\nprint(opp_df.sort_values('opportunity_score', ascending=False).to_string(index=False))"),
    ("markdown", "## Q9 — Interest Forecasting (Simple Linear Projection)"),
    ("code", "from sklearn.linear_model import LinearRegression\n\nforecast_results = []\nfor kw in ww_long['keyword'].unique():\n    sub = ww_long[ww_long['keyword'] == kw].sort_values('date').dropna()\n    X = np.arange(len(sub)).reshape(-1, 1)\n    y = sub['interest'].values\n    model = LinearRegression().fit(X, y)\n    future_X = np.array([[len(sub) + i] for i in range(1, 53)])  # 1 year ahead\n    preds = model.predict(future_X)\n    trend_slope = model.coef_[0]\n    forecast_results.append({'keyword': kw, 'trend_slope': round(trend_slope, 3),\n                             'forecast_next_yr_avg': round(preds.mean(), 1),\n                             'trend_direction': 'Up' if trend_slope > 0.05 else ('Down' if trend_slope < -0.05 else 'Flat')})\nforecast_df = pd.DataFrame(forecast_results).sort_values('trend_slope', ascending=False)\nprint(forecast_df.to_string(index=False))"),
    ("markdown", "## Q10 — Geographic Arbitrage (topics hot in one state, cold in another)"),
    ("code", "# For each keyword, find max state and min state (with non-zero interest)\narbitrage = []\nfor kw in df_region['keyword'].unique():\n    sub = df_region[(df_region['keyword'] == kw) & (df_region['interest'] > 0)]\n    if len(sub) > 1:\n        max_row = sub.loc[sub['interest'].idxmax()]\n        min_row = sub.loc[sub['interest'].idxmin()]\n        ratio = max_row['interest'] / min_row['interest'] if min_row['interest'] > 0 else float('inf')\n        arbitrage.append({'keyword': kw, 'hottest_state': max_row['geoName'], 'hottest_interest': max_row['interest'],\n                          'coldest_state': min_row['geoName'], 'coldest_interest': min_row['interest'],\n                          'arbitrage_ratio': round(ratio, 1)})\narb_df = pd.DataFrame(arbitrage).sort_values('arbitrage_ratio', ascending=False)\nprint(arb_df.to_string(index=False))"),
]

for cell_type, source in cells_02:
    if cell_type == "markdown":
        nb02.cells.append(nbf.v4.new_markdown_cell(source))
    else:
        nb02.cells.append(nbf.v4.new_code_cell(source))

# ============================================================
# NOTEBOOK 03: Executive Dashboard
# ============================================================
nb03 = nbf.v4.new_notebook()
nb03.cells = []

cells_03 = [
    ("markdown", """# 03 — Executive Dashboard: Market Intelligence

Streamlit-ready notebook with trend explorer, regional maps, and breakout alerts.

**Data:** Real Google Trends (pytrends live API) | 14 keywords | 5 years
"""),
    ("code", "import pandas as pd\nimport numpy as np\nimport plotly.express as px\nimport plotly.graph_objects as go\nfrom plotly.subplots import make_subplots\nfrom sklearn.linear_model import LinearRegression\nimport warnings\nwarnings.filterwarnings('ignore')\n\ndf_ww = pd.read_csv('data/interest_over_time_worldwide.csv', index_col=0, parse_dates=True)\ndf_region = pd.read_csv('data/interest_by_region_us.csv')\nrising = pd.read_csv('data/related_queries_rising.csv')\nprint('Data loaded:', df_ww.shape, df_region.shape, rising.shape)"),
    ("markdown", "## 3.1 Trend Explorer — Multi-topic Time Series"),
    ("code", "# Interactive multi-select trend explorer\nselected = ['AI', 'ChatGPT', 'Bitcoin', 'inflation', 'crypto']\nfig = go.Figure()\nfor kw in selected:\n    if kw in df_ww.columns:\n        fig.add_trace(go.Scatter(x=df_ww.index, y=df_ww[kw], name=kw, mode='lines',\n                                  line=dict(width=2)))\nfig.update_layout(title='Trend Explorer: Selected Topics', xaxis_title='Date', yaxis_title='Interest (0–100)',\n                  hovermode='x unified', height=500, template='plotly_white')\nfig.show()"),
    ("markdown", "## 3.2 Regional Comparison Map"),
    ("code", "kw = 'AI'\nsub = df_region[df_region['keyword'] == kw]\nfig = px.choropleth(sub, locations='geoCode', color='interest', hover_name='geoName',\n                    scope='usa', color_continuous_scale='Viridis',\n                    title=f'Regional Interest: \"{kw}\" by US State')\nfig.update_layout(height=450)\nfig.show()"),
    ("markdown", "## 3.3 Breakout Alerts — Rising Related Queries"),
    ("code", "# Show top rising queries by parent keyword\nprint('=== BREAKOUT ALERTS: Top Rising Related Queries ===')\nfor kw in rising['keyword'].unique()[:7]:\n    sub = rising[rising['keyword'] == kw].head(3)\n    if not sub.empty:\n        print(f\"\\n🔥 {kw}:\")\n        for _, row in sub.iterrows():\n            print(f\"   • {row['query']} (+{row['value']}%)\")"),
    ("markdown", "## 3.4 Forecast Panel — 1-Year Linear Projection"),
    ("code", "forecast_panel = []\nfor kw in df_ww.columns:\n    y = df_ww[kw].values\n    X = np.arange(len(y)).reshape(-1, 1)\n    model = LinearRegression().fit(X, y)\n    future = np.array([[len(y) + i] for i in range(1, 53)])\n    preds = model.predict(future)\n    current = y[-4:].mean()\n    forecast_panel.append({'keyword': kw, 'current_avg': round(current, 1),\n                           'forecast_avg': round(preds.mean(), 1),\n                           'trend': '↗ Up' if model.coef_[0] > 0.05 else ('↘ Down' if model.coef_[0] < -0.05 else '→ Flat')})\nforecast_panel_df = pd.DataFrame(forecast_panel).sort_values('forecast_avg', ascending=False)\nprint(forecast_panel_df.to_string(index=False))"),
    ("markdown", "## 3.5 Category Performance Scorecard"),
    ("code", "cats = {\n    'Tech': ['AI', 'machine learning', 'ChatGPT', 'Bitcoin', 'Tesla', 'Netflix', 'Amazon'],\n    'Health': ['telehealth', 'mental health', 'fitness'],\n    'Finance': ['inflation', 'recession', 'stock market', 'crypto']\n}\nscorecard = []\nfor cat, kws in cats.items():\n    valid = [k for k in kws if k in df_ww.columns]\n    avg = df_ww[valid].mean().mean()\n    peak = df_ww[valid].max().max()\n    recent = df_ww[valid].iloc[-52:].mean().mean()\n    prior = df_ww[valid].iloc[-104:-52].mean().mean() if len(df_ww) >= 104 else df_ww[valid].iloc[:52].mean().mean()\n    growth = ((recent - prior) / prior * 100) if prior > 0 else 0\n    scorecard.append({'Category': cat, 'Avg_Interest': round(avg, 1), 'Peak': int(peak),\n                      'Recent_Avg': round(recent, 1), 'YoY_Growth_%': round(growth, 1)})\nscorecard_df = pd.DataFrame(scorecard)\nprint(scorecard_df.to_string(index=False))\n\nfig = px.bar(scorecard_df, x='Category', y='YoY_Growth_%', color='YoY_Growth_%',\n             text='YoY_Growth_%', title='Category YoY Growth %')\nfig.show()"),
]

for cell_type, source in cells_03:
    if cell_type == "markdown":
        nb03.cells.append(nbf.v4.new_markdown_cell(source))
    else:
        nb03.cells.append(nbf.v4.new_code_cell(source))

# Execute all notebooks
print("Executing Notebook 01...")
ep = ExecutePreprocessor(timeout=300, kernel_name="python3")
ep.preprocess(nb01, {"metadata": {"path": "."}})
with open("notebooks/01_exploratory_analysis.ipynb", "w", encoding="utf-8") as f:
    nbf.write(nb01, f)

print("Executing Notebook 02...")
ep.preprocess(nb02, {"metadata": {"path": "."}})
with open("notebooks/02_market_intelligence_sql.ipynb", "w", encoding="utf-8") as f:
    nbf.write(nb02, f)

print("Executing Notebook 03...")
ep.preprocess(nb03, {"metadata": {"path": "."}})
with open("notebooks/03_executive_dashboard.ipynb", "w", encoding="utf-8") as f:
    nbf.write(nb03, f)

print("\n✅ All 3 notebooks built and executed with real data outputs.")
