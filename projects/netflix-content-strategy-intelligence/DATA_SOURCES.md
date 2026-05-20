# Data Sources

## Primary Data Sources

| Source | Type | Description | URL |
|--------|------|-------------|-----|
| TMDB (The Movie Database) API | Commercial API | Live movie and TV metadata, ratings, and streaming availability | https://www.themoviedb.org/ |

## Data Provenance

- Data fetched live from TMDB API v3
- API key verified working as of 2026-05-19
- 438 records fetched during initial analysis

## Data Files

| File | Description | Size (approx) |
|------|-------------|---------------|
| tmdb_*.csv / tmdb_*.json | TMDB API live data exports | 438+ records |

## Refresh Strategy

- Re-fetch via TMDB API using project scripts
- Requires valid TMDB API key (configured in project)
- Data updates as TMDB catalog updates
