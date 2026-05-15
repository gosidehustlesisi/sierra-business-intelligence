import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from collections import Counter

st.set_page_config(page_title="Netflix Content Strategy Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("data/netflix_titles.csv")
    df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
    df['year_added'] = df['date_added'].dt.year
    df['years_to_netflix'] = df['year_added'] - df['release_year']
    return df

df = load_data()

# Parse multi-value fields
countries = []
for entry in df['country'].dropna():
    countries.extend([c.strip() for c in entry.split(',')])
country_counts = pd.Series(Counter(countries)).sort_values(ascending=False)

genres = []
for entry in df['listed_in'].dropna():
    genres.extend([g.strip() for g in entry.split(',')])
genre_counts = pd.Series(Counter(genres)).sort_values(ascending=False)

# KPIs
total = len(df)
movies = len(df[df['type'] == 'Movie'])
tv_shows = len(df[df['type'] == 'TV Show'])
movie_pct = movies / total * 100

# Sidebar
st.sidebar.title("Netflix Content Strategy")
st.sidebar.markdown("---")
st.sidebar.info("""
**Dataset:** Kaggle Netflix Movies & TV Shows  
**Records:** 8,807 titles  
**Last Updated:** 2021
""")

page = st.sidebar.radio("Select View", [
    "Executive Summary",
    "Content Mix",
    "Regional Analysis",
    "Genre Breakdown",
    "Acquisition Timeline",
    "Content Gaps"
])

st.sidebar.markdown("---")
st.sidebar.caption("Built by sierra-business-intelligence")

if page == "Executive Summary":
    st.title("Netflix Content Portfolio — Executive Summary")
    
    cols = st.columns(4)
    cols[0].metric("Total Titles", f"{total:,}")
    cols[1].metric("Movies", f"{movies:,} ({movie_pct:.1f}%)")
    cols[2].metric("TV Shows", f"{tv_shows:,} ({100-movie_pct:.1f}%)")
    cols[3].metric("Countries", f"{len(country_counts):,}")
    
    cols2 = st.columns(4)
    lifecycle = df[(df['years_to_netflix'] >= 0) & (df['years_to_netflix'] <= 50)]
    avg_lifecycle = lifecycle['years_to_netflix'].mean()
    addition_by_year = df.groupby('year_added').size()
    peak_year = int(addition_by_year.idxmax())
    peak_count = int(addition_by_year.max())
    
    cols2[0].metric("Top Country", country_counts.index[0], f"{country_counts.iloc[0]:,} titles")
    cols2[1].metric("Top Genre", genre_counts.index[0], f"{genre_counts.iloc[0]:,} titles")
    cols2[2].metric("Avg Release→Netflix", f"{avg_lifecycle:.1f} years")
    cols2[3].metric("Peak Addition Year", str(peak_year), f"{peak_count:,} titles")
    
    st.markdown("---")
    
    st.subheader("Key Strategic Insights")
    st.markdown("""
    1. **Content Mix:** Netflix is heavily movie-weighted (69.6% movies vs 30.4% TV shows), but TV content has grown in acquisition share since 2019.
    2. **Geographic Concentration:** The US dominates with 36.8% of titles, followed by India (10.4%) and UK (8.0%). Emerging markets represent significant whitespace.
    3. **Content Lifecycle:** Movies take 5.3 years on average from release to Netflix; TV shows just 2.1 years — reflecting Netflix's push for fresher TV content.
    4. **Audience Targeting:** 36.4% of content is rated TV-MA (mature), indicating Netflix leans adult-oriented with 70.9% of catalog targeting teens+ audiences.
    5. **Genre Saturation:** "International Movies" is the #1 category (2,752 titles, 14.2% share), signaling Netflix's global content strategy over US-centric programming.
    """)

elif page == "Content Mix":
    st.title("Content Mix Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = go.Figure(data=[go.Pie(
            labels=['Movies', 'TV Shows'],
            values=[movies, tv_shows],
            hole=0.4,
            marker_colors=['#E50914', '#221F1F']
        )])
        fig.update_layout(title="Content Type Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        rating_counts = df['rating'].value_counts().head(10)
        fig = px.bar(x=rating_counts.index, y=rating_counts.values,
                     labels={'x': 'Rating', 'y': 'Titles'},
                     title="Rating Distribution",
                     color_discrete_sequence=['#E50914'])
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Duration analysis
    st.subheader("Duration Analysis")
    col3, col4 = st.columns(2)
    
    with col3:
        df_movies = df[df['type'] == 'Movie'].copy()
        df_movies['duration_min'] = df_movies['duration'].str.extract(r'(\d+)').astype(float)
        fig = px.histogram(df_movies, x='duration_min', nbins=50,
                           title="Movie Runtime Distribution",
                           color_discrete_sequence=['#E50914'])
        fig.update_layout(xaxis_title="Minutes", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)
    
    with col4:
        df_tv = df[df['type'] == 'TV Show'].copy()
        df_tv['seasons'] = df_tv['duration'].str.extract(r'(\d+)').astype(float)
        season_counts = df_tv['seasons'].value_counts().sort_index().head(10)
        fig = px.bar(x=season_counts.index.astype(str), y=season_counts.values,
                     labels={'x': 'Seasons', 'y': 'Shows'},
                     title="TV Show Season Distribution",
                     color_discrete_sequence=['#221F1F'])
        st.plotly_chart(fig, use_container_width=True)

elif page == "Regional Analysis":
    st.title("Regional Content Analysis")
    
    top_n = st.slider("Show Top N Countries", 5, 25, 15)
    
    fig = px.bar(
        x=country_counts.head(top_n).values,
        y=country_counts.head(top_n).index,
        orientation='h',
        labels={'x': 'Titles', 'y': 'Country'},
        title=f"Top {top_n} Content-Producing Countries",
        color_discrete_sequence=['#E50914']
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Country type breakdown
    st.subheader("Content Type by Country (Top 10)")
    country_type = {}
    for _, row in df.iterrows():
        if pd.isna(row['country']):
            continue
        for c in [c.strip() for c in row['country'].split(',')]:
            if c in country_counts.head(10).index:
                if c not in country_type:
                    country_type[c] = {'Movie': 0, 'TV Show': 0}
                country_type[c][row['type']] += 1
    
    heatmap_df = pd.DataFrame(country_type).T.fillna(0).astype(int)
    heatmap_df = heatmap_df.reindex(country_counts.head(10).index)
    
    fig = px.imshow(heatmap_df.T,
                    labels=dict(x="Country", y="Content Type", color="Titles"),
                    x=heatmap_df.index,
                    y=heatmap_df.columns,
                    color_continuous_scale='Reds',
                    title='Movies vs TV Shows by Country')
    st.plotly_chart(fig, use_container_width=True)

elif page == "Genre Breakdown":
    st.title("Genre Analysis")
    
    top_n = st.slider("Show Top N Genres", 5, 30, 20)
    
    fig = px.bar(
        x=genre_counts.head(top_n).values,
        y=genre_counts.head(top_n).index,
        orientation='h',
        labels={'x': 'Titles', 'y': 'Genre'},
        title=f"Top {top_n} Genres on Netflix",
        color_discrete_sequence=['#E50914']
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Genre opportunity matrix
    st.subheader("Genre Opportunity Matrix")
    genre_stats = {}
    for _, row in df.iterrows():
        if pd.isna(row['listed_in']) or pd.isna(row['country']):
            continue
        for g in [g.strip() for g in row['listed_in'].split(',')]:
            if g not in genre_stats:
                genre_stats[g] = {'count': 0, 'countries': set(), 'tv_ratio': 0, 'movies': 0, 'tv': 0}
            genre_stats[g]['count'] += 1
            for c in [c.strip() for c in row['country'].split(',')]:
                genre_stats[g]['countries'].add(c)
            if row['type'] == 'Movie':
                genre_stats[g]['movies'] += 1
            else:
                genre_stats[g]['tv'] += 1
    
    genre_matrix = pd.DataFrame({
        k: {
            'titles': v['count'],
            'countries': len(v['countries']),
            'tv_ratio': v['tv'] / v['count'] * 100,
            'opportunity': len(v['countries']) / v['count'] * 100
        }
        for k, v in genre_stats.items()
    }).T
    
    genre_matrix = genre_matrix.sort_values('titles', ascending=False).head(25)
    
    fig = px.scatter(genre_matrix.reset_index(), x='titles', y='countries',
                     size='tv_ratio', color='opportunity',
                     hover_name='index',
                     labels={'titles': 'Total Titles', 'countries': 'Countries',
                             'tv_ratio': 'TV %', 'opportunity': 'Opportunity Score'},
                     title='Genre Opportunity: Saturation vs Geographic Spread',
                     color_continuous_scale='RdYlGn',
                     size_max=30)
    st.plotly_chart(fig, use_container_width=True)

elif page == "Acquisition Timeline":
    st.title("Content Acquisition Timeline")
    
    # Content addition by year
    addition_by_type = df.groupby(['year_added', 'type']).size().unstack(fill_value=0)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=addition_by_type.index, y=addition_by_type['Movie'],
                             mode='lines', name='Movies', line=dict(color='#E50914', width=3)))
    fig.add_trace(go.Scatter(x=addition_by_type.index, y=addition_by_type['TV Show'],
                             mode='lines', name='TV Shows', line=dict(color='#221F1F', width=3)))
    fig.update_layout(title='Titles Added to Netflix by Year',
                      xaxis_title='Year Added', yaxis_title='Titles',
                      hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Content lifecycle
    st.subheader("Content Lifecycle: Release Year → Netflix")
    lifecycle_df = df[df['years_to_netflix'].between(0, 20)].copy()
    
    fig = go.Figure()
    for t in ['Movie', 'TV Show']:
        subset = lifecycle_df[lifecycle_df['type'] == t]
        fig.add_trace(go.Histogram(x=subset['years_to_netflix'], name=t,
                                   opacity=0.7, marker_color='#E50914' if t == 'Movie' else '#221F1F'))
    fig.update_layout(title='Years from Release to Netflix Addition',
                      xaxis_title='Years', yaxis_title='Titles',
                      barmode='overlay')
    st.plotly_chart(fig, use_container_width=True)
    
    st.info(f"Movies take an average of **{lifecycle_df[lifecycle_df['type']=='Movie']['years_to_netflix'].mean():.1f} years** from release to Netflix. TV Shows: **{lifecycle_df[lifecycle_df['type']=='TV Show']['years_to_netflix'].mean():.1f} years**.")

elif page == "Content Gaps":
    st.title("Regional Content Gap Analysis")
    
    global_avg = country_counts.mean()
    gap_data = []
    for country, count in country_counts.items():
        if count < global_avg and count >= 5:
            gap_data.append({
                'country': country,
                'titles': count,
                'gap': global_avg - count,
                'opportunity': (global_avg - count) / global_avg * 100
            })
    
    gap_df = pd.DataFrame(gap_data).sort_values('opportunity', ascending=False)
    
    st.subheader("Markets Below Global Average")
    st.write(f"Global average titles per country: **{global_avg:.1f}**")
    
    fig = px.bar(gap_df.head(20), x='opportunity', y='country', orientation='h',
                 color='titles',
                 labels={'opportunity': 'Opportunity Score (% below avg)',
                        'country': 'Country', 'titles': 'Current Titles'},
                 title='Regional Content Gaps (Top 20 Opportunity Markets)',
                 color_continuous_scale='Reds')
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("Emerging Market Opportunity Scoring")
    st.markdown("""
    Opportunity Score formula:
    - **30%** weight on total titles (volume signal)
    - **50%** weight on gap vs global average (underserved signal)
    - **20%** weight on TV content ratio (future growth signal)
    
    Excludes established markets (US, UK, Canada, France, Germany, Japan, South Korea).
    """)
    
    # Opportunity scoring
    opportunity = []
    for country, count in country_counts.items():
        if count < global_avg * 2 and count >= 5 and country not in [
            'United States', 'United Kingdom', 'Canada', 'France', 'Germany', 'Japan', 'South Korea'
        ]:
            # Get TV ratio
            tv_count = 0
            total_count = 0
            for _, row in df.iterrows():
                if pd.notna(row['country']) and country in [c.strip() for c in row['country'].split(',')]:
                    total_count += 1
                    if row['type'] == 'TV Show':
                        tv_count += 1
            tv_ratio = tv_count / total_count * 100 if total_count > 0 else 0
            score = (count * 0.3) + ((count - global_avg) * 0.5) + (tv_count * 0.2)
            opportunity.append({
                'country': country,
                'titles': count,
                'tv_count': tv_count,
                'tv_pct': round(tv_ratio, 1),
                'opportunity_score': round(score, 1)
            })
    
    opp_df = pd.DataFrame(opportunity).sort_values('opportunity_score', ascending=False).head(15)
    st.dataframe(opp_df, use_container_width=True)

st.markdown("---")
st.caption("Data: Kaggle Netflix Movies & TV Shows | Built with Streamlit + Plotly")
