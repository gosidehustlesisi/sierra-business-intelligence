# Data Sources

## Primary Data Sources

| Source | Type | Description | URL |
|--------|------|-------------|-----|
| Google Trends | API | Real-time and historical search trend data by keyword, region, and time period | https://trends.google.com/trends/ |

## Data Provenance

- Data fetched via the `pytrends` Python library
- Unofficial but widely-used API wrapper for Google Trends
- Rate-limited by Google; no API key required

## Data Files

| File | Description | Size (approx) |
|------|-------------|---------------|
| pytrends fetched data | Google Trends interest-over-time and related queries | N/A |

## Refresh Strategy

- Re-fetch via `pytrends` library when updated analysis is needed
- Subject to Google rate limits; use backoff strategies
- Data is near-real-time but subject to Google's sampling
