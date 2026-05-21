import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import json
from pathlib import Path

# Load data
data_dir = Path('projects/netflix-content-strategy-intelligence/data')
trending = pd.read_csv(data_dir / 'trending_movies_latest.csv')
tv = pd.read_csv(data_dir / 'popular_tv_latest.csv')
genres = pd.read_csv(data_dir / 'movie_genres_latest.csv')
genre_pop = pd.read_csv(data_dir / 'genre_popularity_latest.csv')
upcoming = pd.read_csv(data_dir / 'upcoming_movies_latest.csv')

def parse_genres(s):
    try: return json.loads(s) if isinstance(s, str) else []
    except: return []

trending['genre_ids_list'] = trending['genre_ids'].apply(parse_genres)
id_to_name = dict(zip(genres['genre_id'], genres['genre_name']))

genre_counts = {}
for glist in trending['genre_ids_list']:
    for gid in glist:
        genre_counts[id_to_name.get(gid, 'Unknown')] = genre_counts.get(id_to_name.get(gid, 'Unknown'), 0) + 1
genre_df = pd.DataFrame(list(genre_counts.items()), columns=['genre', 'count']).sort_values('count', ascending=False)

# Create dashboard
fig = plt.figure(figsize=(16, 10), facecolor='#0f1115')
fig.suptitle('Netflix Content Intelligence — Executive Dashboard', fontsize=18, fontweight='bold', color='white', y=0.98)

# Metric cards row
ax_metrics = fig.add_axes([0.05, 0.78, 0.9, 0.18])
ax_metrics.set_facecolor('#0f1115')
ax_metrics.axis('off')

metrics = [
    ('Trending Movies', f'{len(trending):,}', '#06b6d4'),
    ('Popular TV Shows', f'{len(tv):,}', '#f59e0b'),
    ('Genres Mapped', f'{len(genres):,}', '#10b981'),
    ('Upcoming Releases', f'{len(upcoming):,}', '#ef4444'),
]

for i, (label, value, color) in enumerate(metrics):
    x = 0.05 + i * 0.24
    rect = mpatches.FancyBboxPatch((x, 0.1), 0.2, 0.7, boxstyle="round,pad=0.02", 
                                    facecolor='#1a2234', edgecolor=color, linewidth=2)
    ax_metrics.add_patch(rect)
    ax_metrics.text(x + 0.1, 0.65, value, ha='center', va='center', fontsize=22, 
                    fontweight='bold', color=color, transform=ax_metrics.transAxes)
    ax_metrics.text(x + 0.1, 0.3, label, ha='center', va='center', fontsize=11, 
                    color='#94a3b8', transform=ax_metrics.transAxes)

# Content mix pie
ax1 = fig.add_axes([0.05, 0.42, 0.25, 0.32])
ax1.set_facecolor('#0f1115')
sizes = [len(trending), len(tv)]
labels = ['Movies', 'TV Shows']
colors = ['#3b82f6', '#f97316']
wedges, texts, autotexts = ax1.pie(sizes, labels=labels, autopct='%1.1f%%', 
                                     colors=colors, textprops={'color': 'white', 'fontsize': 10},
                                     startangle=90)
for autotext in autotexts:
    autotext.set_fontsize(11)
    autotext.set_fontweight('bold')
ax1.set_title('Content Mix', color='white', fontsize=12, fontweight='bold', pad=10)

# Top genres bar
ax2 = fig.add_axes([0.35, 0.42, 0.28, 0.32])
ax2.set_facecolor('#0f1115')
top10 = genre_df.head(10)
bars = ax2.barh(range(len(top10)), top10['count'], color='#06b6d4')
ax2.set_yticks(range(len(top10)))
ax2.set_yticklabels(top10['genre'], color='white', fontsize=9)
ax2.set_xlabel('Title Count', color='#94a3b8', fontsize=10)
ax2.set_title('Top 10 Genres', color='white', fontsize=12, fontweight='bold', pad=10)
ax2.tick_params(axis='x', colors='#94a3b8')
ax2.invert_yaxis()
for spine in ax2.spines.values():
    spine.set_color('#1f2d44')

# Rating distribution
ax3 = fig.add_axes([0.68, 0.42, 0.27, 0.32])
ax3.set_facecolor('#0f1115')
ax3.hist(trending['vote_average'], bins=25, color='#ef4444', edgecolor='#0f1115', alpha=0.8)
ax3.axvline(trending['vote_average'].mean(), color='white', linestyle='--', linewidth=2, 
            label=f'Mean: {trending["vote_average"].mean():.2f}')
ax3.set_xlabel('Vote Average', color='#94a3b8', fontsize=10)
ax3.set_ylabel('Count', color='#94a3b8', fontsize=10)
ax3.set_title('Rating Distribution', color='white', fontsize=12, fontweight='bold', pad=10)
ax3.tick_params(axis='both', colors='#94a3b8')
ax3.legend(facecolor='#1a2234', edgecolor='#1f2d44', labelcolor='white', loc='upper left')
for spine in ax3.spines.values():
    spine.set_color('#1f2d44')

# Upcoming releases by month
ax4 = fig.add_axes([0.05, 0.06, 0.42, 0.3])
ax4.set_facecolor('#0f1115')
upcoming['release_month'] = pd.to_datetime(upcoming['release_date'], errors='coerce').dt.month
month_counts = upcoming['release_month'].value_counts().sort_index()
months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
values = [month_counts.get(i, 0) for i in range(1, 13)]
bars = ax4.bar(months, values, color='#10b981', edgecolor='#0f1115')
ax4.set_xlabel('Month', color='#94a3b8', fontsize=10)
ax4.set_ylabel('Upcoming Releases', color='#94a3b8', fontsize=10)
ax4.set_title('Release Pipeline (Upcoming)', color='white', fontsize=12, fontweight='bold', pad=10)
ax4.tick_params(axis='both', colors='#94a3b8')
for spine in ax4.spines.values():
    spine.set_color('#1f2d44')

# Data source note
ax5 = fig.add_axes([0.52, 0.06, 0.43, 0.3])
ax5.set_facecolor('#0f1115')
ax5.axis('off')
ax5.text(0.5, 0.85, 'Data Sources', ha='center', va='top', fontsize=13, 
         fontweight='bold', color='white', transform=ax5.transAxes)
sources = [
    '• TMDB API (live): 438 records per fetch',
    '• Netflix Kaggle (CC0): 8,807 titles',
    '• Fetched: 2026-05-19',
    '',
    'Key Metrics:',
    f'• Avg Movie Rating: {trending["vote_average"].mean():.2f}/10',
    f'• Avg TV Rating: {tv["vote_average"].mean():.2f}/10',
    f'• Top Genre: {genre_df.iloc[0]["genre"]} ({genre_df.iloc[0]["count"]} titles)',
]
for j, line in enumerate(sources):
    ax5.text(0.1, 0.7 - j*0.09, line, ha='left', va='top', fontsize=10, 
             color='#94a3b8', transform=ax5.transAxes)

# Footer
fig.text(0.5, 0.01, 'Live TMDB API data | Authenticated via Bearer token | github.com/gosidehustlesisi/sierra-business-intelligence', 
         ha='center', va='bottom', fontsize=9, color='#64748b')

out_path = Path('projects/netflix-content-strategy-intelligence/figures/03_executive_dashboard.png')
plt.savefig(out_path, dpi=150, facecolor='#0f1115', edgecolor='none', bbox_inches='tight', pad_inches=0.3)
print(f'Saved: {out_path} ({out_path.stat().st_size:,} bytes)')
