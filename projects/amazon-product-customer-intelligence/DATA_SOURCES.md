# Data Sources

## Primary Data Sources

| Source | Type | Description | URL |
|--------|------|-------------|-----|
| UCSD Julian McAuley Amazon Reviews Dataset | Public Dataset | Amazon product reviews for electronics category (5-core subset) | https://jmcauley.ucsd.edu/data/amazon/ |
| Keepa API | Commercial API | Live Amazon product pricing, sales rank, and availability data | https://keepa.com/ |

## Data Provenance

- Amazon reviews downloaded from UCSD Julian McAuley's repository
- Keepa API data fetched live with authenticated API key
- Electronics 5-core subset used for focused analysis

## Data Files

| File | Description | Size (approx) |
|------|-------------|---------------|
| amazon_reviews_electronics_5core.csv | UCSD Amazon electronics reviews (5-core subset) | N/A |
| keepa_*.csv | Keepa API live product data exports | N/A |

## Refresh Strategy

- Re-download UCSD dataset when new versions are published
- Re-fetch Keepa API data via project scripts for live analysis
- Keepa API requires valid subscription and API key
