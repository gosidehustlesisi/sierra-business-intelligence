# Data Sources — Netflix Content Strategy Intelligence

All data is **first-party and self-extracted from TMDB** with our own API key.
No third-party CSV uploads, no LLM-generated rows, no synthetic data. Every
number is reproducible: re-run the scripts below with a TMDB key and you get
the same dataset.

## Two layers (kept strictly separate)

| Layer | Source | What it answers | Script |
|-------|--------|-----------------|--------|
| **Catalog** | TMDB `/discover/movie` + `/discover/tv`, filtered to Netflix (`with_watch_providers=8`, `watch_region=US`, `flatrate`) | *Supply* — what Netflix's catalog contains: genre structure, content mix, release eras, real rating distributions | `fetch_netflix_catalog.py` |
| **Live snapshot** | TMDB `/trending`, `/movie/top_rated`, `/tv/popular`, `/movie/upcoming` | *Demand* — what's hot / top-rated / upcoming right now | `fetch_tmdb_data.py` |

**Source-separation rule:** catalog figures are built only from the catalog
extract; score-based "what's hot" figures only from the live snapshot. The two
are never joined. (This is the discipline the retired `fallback_data.py` violated
by fabricating scores — that file has been removed.)

## Provenance

- **Provider:** TMDB watch-provider id `8` = Netflix (availability via JustWatch), region `US`.
- **Method:** paginate `/discover` (TMDB cap 500 pages × 20), dedupe by id.
- **Extraction date + counts:** recorded in `data/netflix_catalog_manifest.json`
  (regenerated on every run). The headline title count = the real count from that manifest.
- **Fields captured:** `tmdb_id, media_type, title, genres, vote_average, vote_count,
  popularity, release_date, release_year, original_language, origin_country`.

## Data files

| File | Description |
|------|-------------|
| `data/netflix_catalog_latest.csv` | Self-extracted Netflix catalog (movies + TV), real TMDB fields |
| `data/netflix_catalog_manifest.json` | Source, region, extraction date, total/movie/TV counts |
| `data/{trending,top_rated,popular_tv,upcoming}_*.csv` | Live snapshot layer |

## Important: ratings vs. scores

TMDB `vote_average` is a real audience **score** (0–10) and is the only basis
for any "rated higher / quality" claim. There is no maturity-rating (TV-MA, etc.)
score in this dataset — "international / content mix" claims come from `genres`,
`original_language`, and `origin_country`, never from scores.

## Refresh

- Catalog: `python fetch_netflix_catalog.py` (optionally `--region`, `--max-pages`).
- Live snapshot: `python fetch_tmdb_data.py` (also runs daily via `.github/workflows/tmdb-refresh.yml`).
- Both require `TMDB_API_KEY` (or `TMDB_READ_TOKEN`) in the environment / repo secret.
