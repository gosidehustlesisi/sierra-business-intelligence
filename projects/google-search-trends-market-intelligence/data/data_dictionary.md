# Data Dictionary — Google Search Trends Market Intelligence

## Files

### `interest_over_time_worldwide.csv`
| Column | Type | Description |
|--------|------|-------------|
| `date` | datetime | Weekly start date (Sunday) |
| `AI` … `crypto` | int | Search interest index (0–100), normalized by Google for the query group |

- **Shape:** 262 weeks × 14 keywords
- **Coverage:** May 2021 – May 2026 (5 years)
- **Source:** Google Trends via pytrends (`timeframe='today 5-y'`, `geo=''`)

### `interest_over_time_us.csv`
Same schema as worldwide, filtered to United States (`geo='US'`).

### `interest_by_region_us.csv`
| Column | Type | Description |
|--------|------|-------------|
| `geoName` | string | US state name |
| `geoCode` | string | ISO state code (e.g., US-CA) |
| `keyword` | string | Search term |
| `interest` | int | Relative interest in that state (0–100) |
| `geo_scope` | string | Always "US" |
| `fetched_at` | string | Fetch timestamp |

- **Shape:** 714 rows (14 keywords × 51 US regions)
- **Source:** Google Trends via pytrends (`resolution='REGION'`, `geo='US'`)

### `related_queries_top.csv`
| Column | Type | Description |
|--------|------|-------------|
| `query` | string | Related search query |
| `value` | int | Relative frequency / percentage |
| `keyword` | string | Parent keyword |
| `type` | string | Always "top" |
| `fetched_at` | string | Fetch timestamp |

- **Shape:** 345 rows
- **Source:** Google Trends via pytrends (`related_queries()`)

### `related_queries_rising.csv`
Same schema as `related_queries_top.csv`, but `type` = "rising".
- **Shape:** 340 rows
- Contains queries with significant recent growth.

## Methodology Notes
1. All data fetched live from Google Trends via `pytrends` on 2026-05-15.
2. Interest values are **relative** (0–100) within the queried keyword group, not absolute search volume.
3. No synthetic data — every value came from a live API call.
4. Rate-limiting delays (1.5–2s) were applied between requests.

## BigQuery Reference
This project also references the public dataset `bigquery-public-data.google_trends` for schema alignment and validation, though actual data was fetched via pytrends for full keyword flexibility.
