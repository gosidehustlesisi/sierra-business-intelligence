#!/usr/bin/env python3
"""
Netflix Catalog Extractor — self-sourced from TMDB.

Builds a first-party, reproducible Netflix catalog by paging TMDB's /discover
endpoints filtered to Netflix's watch-provider id (8), subscription (flatrate)
titles only, for a given region. No third-party CSV uploads, no LLM-generated
rows, no synthetic data — every record is a real TMDB row you can reproduce by
re-running this script with your own key.

Why this and not a Kaggle dump:
    - First-party: pulled live from TMDB's API with YOUR key.
    - Reproducible: anyone with a key reruns this and gets your numbers.
    - Scored + current: real vote_average/popularity, reflects live availability.

Usage:
    export TMDB_API_KEY=xxxxx          # or TMDB_READ_TOKEN for v4 auth
    python fetch_netflix_catalog.py                 # full US catalog
    python fetch_netflix_catalog.py --region GB     # another region
    python fetch_netflix_catalog.py --max-pages 3   # quick smoke test

Output (in --data-dir, default ./data):
    netflix_catalog_latest.csv        # the catalog (movies + TV)
    netflix_catalog_<UTCstamp>.csv    # timestamped copy
    netflix_catalog_manifest.json     # source, region, date, counts

Env:
    TMDB_API_KEY    — v3 key. Free at https://www.themoviedb.org/settings/api
    TMDB_READ_TOKEN — optional v4 bearer token (takes precedence).

Rate limit: ~40 req / 10s, respected via a fixed inter-request sleep.
"""

import os
import sys
import time
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path

import requests
import pandas as pd

TMDB_BASE = "https://api.themoviedb.org/3"
NETFLIX_PROVIDER_ID = 8          # TMDB watch-provider id for Netflix
DEFAULT_REGION = "US"
TMDB_PAGE_CAP = 500              # TMDB hard pagination cap (500 * 20 = 10k)
RATE_SLEEP = 0.27               # ~40 requests / 10 seconds


# ── Auth ─────────────────────────────────────────────────────────────────────

def build_auth():
    """Prefer a v4 read token; fall back to a v3 api_key query param."""
    token = os.environ.get("TMDB_READ_TOKEN", "").strip()
    if token:
        return {"Authorization": f"Bearer {token}", "accept": "application/json"}, {}
    key = os.environ.get("TMDB_API_KEY", "").strip()
    if not key:
        sys.exit("[ERROR] Set TMDB_API_KEY (or TMDB_READ_TOKEN). "
                 "Free key: https://www.themoviedb.org/settings/api")
    return {"accept": "application/json"}, {"api_key": key}


_AUTH = None


def _auth():
    """Lazily resolve (and cache) auth so the module imports without a key."""
    global _AUTH
    if _AUTH is None:
        _AUTH = build_auth()
    return _AUTH


def tmdb_get(endpoint, params=None):
    """GET a TMDB endpoint with rate-limiting and one 429 back-off retry."""
    headers, auth_params = _auth()
    req = dict(auth_params)
    req.update(params or {})
    time.sleep(RATE_SLEEP)
    for attempt in range(3):
        resp = requests.get(f"{TMDB_BASE}{endpoint}", headers=headers,
                            params=req, timeout=30)
        if resp.status_code == 429:
            time.sleep(2 + attempt * 2)
            continue
        resp.raise_for_status()
        return resp.json()
    resp.raise_for_status()


# ── Extraction ───────────────────────────────────────────────────────────────

def genre_map(kind):
    """{genre_id: name} for 'movie' or 'tv'."""
    data = tmdb_get(f"/genre/{kind}/list")
    return {g["id"]: g["name"] for g in data.get("genres", [])}


def discover(kind, region, max_pages):
    """
    Page /discover/{kind} filtered to Netflix flatrate in `region`.
    Returns (deduped list of raw items, tmdb_reported_total_results).
    """
    params = {
        "with_watch_providers": NETFLIX_PROVIDER_ID,
        "watch_region": region,
        "with_watch_monetization_types": "flatrate",
        "sort_by": "popularity.desc",
        "page": 1,
    }
    first = tmdb_get(f"/discover/{kind}", params)
    total_pages = min(first.get("total_pages", 1), TMDB_PAGE_CAP)
    if max_pages:
        total_pages = min(total_pages, max_pages)

    seen = {item["id"]: item for item in first.get("results", [])}
    for page in range(2, total_pages + 1):
        params["page"] = page
        data = tmdb_get(f"/discover/{kind}", params)
        for item in data.get("results", []):
            seen[item["id"]] = item
        if page % 25 == 0:
            print(f"      {kind}: page {page}/{total_pages} ({len(seen)} unique)")

    print(f"  {kind}: {len(seen)} unique titles across {total_pages} pages "
          f"(TMDB total_results={first.get('total_results')})")
    return list(seen.values()), first.get("total_results", len(seen))


def normalize(item, kind, gmap, extracted_at):
    """Flatten a raw TMDB item to the catalog row schema."""
    is_movie = kind == "movie"
    date = item.get("release_date") if is_movie else item.get("first_air_date")
    year = (date or "")[:4]
    gids = item.get("genre_ids", [])
    return {
        "tmdb_id": item.get("id"),
        "media_type": "movie" if is_movie else "tv",
        "title": item.get("title") if is_movie else item.get("name"),
        "original_title": item.get("original_title") if is_movie else item.get("original_name"),
        "genres": "|".join(gmap.get(g, str(g)) for g in gids),
        "genre_ids": json.dumps(gids),
        "vote_average": item.get("vote_average"),
        "vote_count": item.get("vote_count"),
        "popularity": item.get("popularity"),
        "release_date": date,
        "release_year": int(year) if year.isdigit() else None,
        "original_language": item.get("original_language"),
        "origin_country": "|".join(item.get("origin_country", [])) if not is_movie else "",
        "overview": (item.get("overview") or "").replace("\n", " ").strip(),
        "extracted_at": extracted_at,
    }


def main():
    ap = argparse.ArgumentParser(description="Self-extract the Netflix catalog from TMDB.")
    ap.add_argument("--region", default=DEFAULT_REGION,
                    help="ISO 3166-1 region code (default: US)")
    ap.add_argument("--data-dir", default="data", help="output directory (default: data)")
    ap.add_argument("--max-pages", type=int, default=0,
                    help="cap pages per media type (0 = all, up to 500)")
    args = ap.parse_args()

    extracted_at = datetime.now(timezone.utc).isoformat()
    print(f"{'='*64}")
    print(f"NETFLIX CATALOG EXTRACT — TMDB provider {NETFLIX_PROVIDER_ID}, region {args.region}")
    print(f"{extracted_at}")
    print(f"{'='*64}")

    movie_genres = genre_map("movie")
    tv_genres = genre_map("tv")
    all_genres = {**movie_genres, **tv_genres}  # merge so any id resolves (e.g. 10749 on TV)

    print("[1/2] Discovering movies on Netflix...")
    movies, movie_total = discover("movie", args.region, args.max_pages)
    print("[2/2] Discovering TV on Netflix...")
    tv, tv_total = discover("tv", args.region, args.max_pages)

    rows = ([normalize(m, "movie", all_genres, extracted_at) for m in movies]
            + [normalize(t, "tv", all_genres, extracted_at) for t in tv])
    df = (pd.DataFrame(rows)
            .drop_duplicates(subset=["media_type", "tmdb_id"])
            .reset_index(drop=True))

    out = Path(args.data_dir)
    out.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    latest = out / "netflix_catalog_latest.csv"
    stamped = out / f"netflix_catalog_{ts}.csv"
    df.to_csv(latest, index=False)
    df.to_csv(stamped, index=False)

    manifest = {
        "source": f"TMDB /discover (with_watch_providers={NETFLIX_PROVIDER_ID} Netflix, flatrate)",
        "region": args.region,
        "extracted_at": extracted_at,
        "total_titles": int(len(df)),
        "movies": int((df["media_type"] == "movie").sum()),
        "tv": int((df["media_type"] == "tv").sum()),
        "tmdb_reported_total_movies": movie_total,
        "tmdb_reported_total_tv": tv_total,
        "files": [latest.name, stamped.name],
        "note": ("First-party self-extraction from TMDB. Reproduce by re-running "
                 "with a TMDB key. Zero synthetic records, zero third-party uploads."),
    }
    (out / "netflix_catalog_manifest.json").write_text(json.dumps(manifest, indent=2))

    print(f"\n  ✓ {len(df):,} titles  ({manifest['movies']} movies / {manifest['tv']} TV)")
    print(f"  ✓ {latest}")
    print(f"  ✓ manifest: netflix_catalog_manifest.json")
    print(f"\n{'='*64}")
    print(f"DONE — every row is a real TMDB record (Netflix {args.region}, {extracted_at[:10]})")
    print(f"{'='*64}")


if __name__ == "__main__":
    main()
