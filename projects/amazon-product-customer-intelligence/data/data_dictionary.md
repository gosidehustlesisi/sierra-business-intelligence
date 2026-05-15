# Amazon Electronics Reviews — Data Dictionary

**Dataset:** `amazon_reviews_electronics_5core.csv`
**Records:** 130,038 (sampled 1/13 from 1,689,188 Electronics 5-core)
**Date Range:** 1999-11-23 to 2014-07-23
**Source:** [UCSD Amazon Review Data](http://jmcauley.ucsd.edu/data/amazon/)

## Columns

| Column | Type | Description |
|--------|------|-------------|
| `reviewerID` | string | Unique reviewer identifier (e.g., A2SUAM1J3GNN3B) |
| `asin` | string | Amazon Standard Identification Number — product ID |
| `reviewerName` | string | Reviewer display name (may be empty) |
| `helpful_upvotes` | integer | Number of "helpful" votes received |
| `helpful_total` | integer | Total votes on helpfulness (up + down) |
| `reviewText` | string | Full review text content |
| `overall` | float | Star rating (1.0–5.0) |
| `summary` | string | Short review summary/title |
| `unixReviewTime` | integer | Review timestamp (Unix seconds since epoch) |
| `reviewTime` | string | Human-readable date (MM DD, YYYY format) |

## Derived Metrics (computed in notebooks)

| Metric | Formula | Value |
|--------|---------|-------|
| Helpfulness Ratio | `helpful_upvotes / helpful_total` | 83.7% overall |
| Review Length | `len(reviewText)` | Median 345 chars |
| Review Year/Month | `datetime.fromtimestamp(unixReviewTime)` | — |

## Data Quality

- **Missing reviewerName:** ~2.3% empty
- **Missing reviewText:** ~0.06% (78 reviews with no text)
- **Missing summary:** 0%
- **No duplicate reviewerID+asin combinations** in 5-core subset (each user-product pair is unique)

## Sampling Method

Uniform random sampling at rate 1/13 with seed 42 from the full Electronics 5-core JSON. Preserves temporal, rating, and product distributions.

## Citation

> Ni, Jianmo, Jiacheng Li, and Julian McAuley. "Justifying recommendations using distantly-labeled reviews and fine-grained aspects." *Empirical Methods in Natural Language Processing (EMNLP)*, 2019.
