import pandas as pd
import streamlit as st
import plotly.express as px
from utils import load_all_data, parse_genres, format_timestamp

# Country mapping for choropleth (ISO 3166-1 alpha-3)
COUNTRY_MAP = {
    "US": "USA", "GB": "GBR", "JP": "JPN", "KR": "KOR", "CA": "CAN",
    "FR": "FRA", "DE": "DEU", "ES": "ESP", "IT": "ITA", "AU": "AUS",
    "BR": "BRA", "IN": "IND", "MX": "MEX", "RU": "RUS", "CN": "CHN",
    "SE": "SWE", "NO": "NOR", "DK": "DNK", "NL": "NLD", "BE": "BEL",
    "PL": "POL", "TR": "TUR", "AR": "ARG", "ZA": "ZAF", "FI": "FIN",
    "IE": "IRL", "NZ": "NZL", "PT": "PRT", "CH": "CHE", "AT": "AUT",
    "CZ": "CZE", "HU": "HUN", "RO": "ROU", "IL": "ISR", "TH": "THA",
    "PH": "PHL", "ID": "IDN", "MY": "MYS", "SG": "SGP", "TW": "TWN",
    "HK": "HKG", "GR": "GRC", "UA": "UKR", "SA": "SAU", "AE": "ARE",
    "EG": "EGY", "NG": "NGA", "KE": "KEN", "CO": "COL", "CL": "CHL",
    "PE": "PER", "VE": "VEN", "EC": "ECU", "UY": "URY", "PK": "PAK",
    "BD": "BGD", "VN": "VNM", "UA": "UKR", "SK": "SVK", "SI": "SVN",
    "HR": "HRV", "RS": "SRB", "BG": "BGR", "LT": "LTU", "LV": "LVA",
    "EE": "EST", "GE": "GEO", "AM": "ARM", "AZ": "AZE", "KZ": "KAZ",
    "UZ": "UZB", "KG": "KGZ", "TJ": "TJK", "TM": "TKM", "MN": "MNG",
    "KH": "KHM", "LA": "LAO", "MM": "MMR", "NP": "NPL", "BT": "BTN",
    "LK": "LKA", "MV": "MDV", "AF": "AFG", "IR": "IRN", "IQ": "IRQ",
    "JO": "JOR", "LB": "LBN", "SY": "SYR", "YE": "YEM", "OM": "OMN",
    "QA": "QAT", "BH": "BHR", "KW": "KWT", "CY": "CYP", "MT": "MLT",
    "LU": "LUX", "IS": "ISL", "GL": "GRL", "FO": "FRO", "LI": "LIE",
    "MC": "MCO", "SM": "SMR", "AD": "AND", "VA": "VAT"
}

st.set_page_config(page_title="Geographic Insights", page_icon="🌍", layout="wide")

data, manifest = load_all_data()

st.title("🌍 Geographic Insights")

fetched_at = manifest.get("fetched_at", "Unknown")
st.markdown(f'<span style="background:#E50914;color:white;padding:6px 14px;border-radius:20px;font-size:0.8rem;font-weight:600;">🔴 LIVE — Refreshed {format_timestamp(fetched_at)}</span>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

tv = data.get("popular_tv", pd.DataFrame())

if tv.empty or "origin_country" not in tv.columns:
    st.warning("TV data does not contain origin_country information. Geographic analysis requires this field.")
    st.info("Available columns in TV data: " + ", ".join(tv.columns.tolist() if not tv.empty else ["N/A"]))
    st.stop()

st.subheader("Content by Origin Country")

# Parse origin countries
import ast

def parse_countries(val):
    if pd.isna(val):
        return []
    try:
        if isinstance(val, str):
            val = val.strip()
            if val.startswith("[") and val.endswith("]"):
                return ast.literal_eval(val)
            else:
                return [val]
        elif isinstance(val, list):
            return val
        else:
            return [str(val)]
    except Exception:
        return []

tv["countries_list"] = tv["origin_country"].apply(parse_countries)

# Build country stats
country_stats = {}
for _, row in tv.iterrows():
    for country in row["countries_list"]:
        country = country.strip().upper()
        if not country:
            continue
        if country not in country_stats:
            country_stats[country] = {"count": 0, "total_rating": 0, "total_pop": 0, "titles": []}
        country_stats[country]["count"] += 1
        country_stats[country]["total_rating"] += row.get("vote_average", 0)
        country_stats[country]["total_pop"] += row.get("popularity", 0)
        title = row.get("name", "Unknown")
        country_stats[country]["titles"].append(title)

country_df = pd.DataFrame([
    {
        "Country": c,
        "Count": s["count"],
        "Avg Rating": s["total_rating"] / s["count"],
        "Avg Popularity": s["total_pop"] / s["count"],
        "Sample Titles": ", ".join(s["titles"][:3])
    }
    for c, s in country_stats.items()
]).sort_values("Count", ascending=False)

st.write(f"Analyzing {len(tv)} TV shows across {len(country_df)} origin countries")

# Choropleth World Map
st.subheader("🗺️ Global Content Distribution")

# Map countries to ISO alpha-3
country_df["iso_alpha"] = country_df["Country"].map(COUNTRY_MAP)
mapped_countries = country_df.dropna(subset=["iso_alpha"])

if len(mapped_countries) > 0:
    fig_map = px.choropleth(
        mapped_countries,
        locations="iso_alpha",
        color="Count",
        hover_name="Country",
        hover_data=["Avg Rating", "Avg Popularity", "Sample Titles"],
        color_continuous_scale="Reds",
        projection="natural earth",
        title="TV Show Count by Origin Country"
    )
    fig_map.update_layout(height=600, geo=dict(showframe=False, showcoastlines=True))
    st.plotly_chart(fig_map, use_container_width=True)
    st.caption(f"Mapped {len(mapped_countries)} of {len(country_df)} countries. Unmapped: {', '.join(country_df[country_df['iso_alpha'].isna()]['Country'].tolist())}")
else:
    st.warning("No countries could be mapped to ISO codes for choropleth display.")

col1, col2 = st.columns(2)

with col1:
    fig = px.bar(country_df.head(15), x="Count", y="Country", orientation="h",
                 color="Avg Rating", color_continuous_scale="RdYlGn",
                 hover_data=["Avg Popularity", "Sample Titles"])
    fig.update_layout(yaxis_categoryorder="total ascending", height=500)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.scatter(country_df, x="Count", y="Avg Rating", size="Avg Popularity",
                     color="Avg Rating", hover_name="Country",
                     color_continuous_scale="RdYlGn",
                     hover_data=["Sample Titles"])
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Country Detail View")
selected_country = st.selectbox("Select a country", country_df["Country"].tolist())

if selected_country:
    country_titles = []
    for _, row in tv.iterrows():
        countries = [c.strip().upper() for c in row["countries_list"]]
        if selected_country in countries:
            country_titles.append(row)
    
    if country_titles:
        cdf = pd.DataFrame(country_titles)
        st.write(f"**{len(cdf)}** titles from **{selected_country}**")
        
        cols = st.columns(3)
        for idx, (_, row) in enumerate(cdf.iterrows()):
            with cols[idx % 3]:
                title = row.get("name", "Unknown")
                rating = row.get("vote_average", 0)
                pop = row.get("popularity", 0)
                st.markdown(f"**{title}**")
                st.markdown(f"⭐ {rating:.2f} | 📈 {pop:.1f}")
                st.markdown("---")

st.caption(f"Data: TMDB API | TV Shows: {len(tv)} | Countries: {len(country_df)} | Last refresh: {format_timestamp(fetched_at)}")
