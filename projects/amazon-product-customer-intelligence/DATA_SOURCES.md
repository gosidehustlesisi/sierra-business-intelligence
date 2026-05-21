# Data Sources

## Primary Data Source

| Source | Type | Description | URL |
|--------|------|-------------|-----|
| UCSD Julian McAuley Amazon Reviews Dataset | Public Dataset | Amazon product reviews for electronics category (5-core subset) | https://jmcauley.ucsd.edu/data/amazon/ |

## Data Provenance

- Amazon reviews downloaded from UCSD Julian McAuley's repository
- Electronics 5-core subset used for focused analysis
- 67,325 real reviews from 27,832 unique products, 53,609 unique reviewers
- Date span: 2003-01-01 to 2013-12-09

## Data Files

| File | Description | Size (approx) |
|------|-------------|---------------|
| amazon_reviews_electronics_5core.csv | UCSD Amazon electronics reviews (5-core subset, 1/13 sample) | ~50MB |
| reviews_Electronics_5.json.gz | Raw UCSD source (not tracked in repo) | 495MB |

## Refresh Strategy

- Re-download UCSD dataset when new versions are published
- Dataset is static historical data; no live refresh required
