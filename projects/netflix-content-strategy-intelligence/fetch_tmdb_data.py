#!/usr/bin/env python3
"""
TMDB Live Data Fetcher
Pulls current entertainment industry data from The Movie Database (TMDB) API.

Data Sources:
    - Trending movies (daily)       → /trending/movie/day
    - Popular TV shows              → /tv/popular
    - Movie genres + popularity     → /genre/movie/list + /discover/movie
    - Top-rated movies              → /movie/top_rated
    - Upcoming releases             → /movie/upcoming

Environment:
    TMDB_API_KEY — required. Get free key at https://www.themoviedb.org/settings/api
    TMDB_READ_TOKEN — optional (v4 auth), takes precedence over API_KEY.

Rate Limit: 40 requests per 10 seconds (respected via time.sleep).
"""

import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests

TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_IMG_BASE = "https://image.tmdb.org/t/p/w500"
RATE_LIMIT_REQ = 40
RATE_LIMIT_WINDOW = 10  # seconds

# ── Auth helpers ────────────────────────────────────────────────────────────

def get_auth_headers():
    token = os.environ.get("TMDB_READ_TOKEN", "").strip()
    if token:
        return {"Authorization": f"Bearer {token}", "accept": "application/json"}
    return None


def get_api_key():
    return os.environ.get("TMDB_API_KEY", "").strip()


def tmdb_get(endpoint, params=None, page=1):
    """
    GET from TMDB v3 API. Uses Bearer token if available, else falls back
    to api_key query parameter. Respects rate limit.
    """
    url = f"{TMDB_BASE}{endpoint}"
    req_params = dict(params or {})
    req_params["page"] = page

    headers = get_auth_headers()
    if headers:
        pass  # token auth
    else:
        key = get_api_key()
        if not key:
            print("[ERROR] No TMDB_API_KEY or TMDB_READ_TOKEN set.")
            print("        Register free at https://www.themoviedb.org/settings/api")
            sys.exit(1)
        req_params["api_key"] = key

    # Simple rate-limiting: 40 req / 10 sec => 0.25 sec min between calls
    time.sleep(0.27)

    resp = requests.get(url, headers=headers, params=req_params, timeout=30)
    if resp.status_code == 429:
        # Back off and retry once
        time.sleep(2)
        resp = requests.get(url, headers=headers, params=req_params, timeout=30)
    resp.raise_for_status()
    return resp.json()


# ── Fetchers ────────────────────────────────────────────────────────────────

def fetch_trending_movies(pages=5):
    rows = []
    for p in range(1, pages + 1):
        data = tmdb_get("/trending/movie/day", page=p)
        for item in data.get("results", []):
            rows.append({
                "tmdb_id": item["id"],
                "title": item.get("title"),
                "original_title": item.get("original_title"),
                "popularity": item.get("popularity"),
                "vote_average": item.get("vote_average"),
                "vote_count": item.get("vote_count"),
                "release_date": item.get("release_date"),
                "genre_ids": json.dumps(item.get("genre_ids", [])),
                "overview": item.get("overview"),
                "poster_path": item.get("poster_path"),
                "media_type": item.get("media_type", "movie"),
                "fetched_at": datetime.utcnow().isoformat(),
            })
    return pd.DataFrame(rows)


def fetch_popular_tv(pages=5):
    rows = []
    for p in range(1, pages + 1):
        data = tmdb_get("/tv/popular", page=p)
        for item in data.get("results", []):
            rows.append({
                "tmdb_id": item["id"],
                "name": item.get("name"),
                "original_name": item.get("original_name"),
                "popularity": item.get("popularity"),
                "vote_average": item.get("vote_average"),
                "vote_count": item.get("vote_count"),
                "first_air_date": item.get("first_air_date"),
                "origin_country": json.dumps(item.get("origin_country", [])),
                "genre_ids": json.dumps(item.get("genre_ids", [])),
                "overview": item.get("overview"),
                "poster_path": item.get("poster_path"),
                "fetched_at": datetime.utcnow().isoformat(),
            })
    return pd.DataFrame(rows)


def fetch_movie_genres():
    data = tmdb_get("/genre/movie/list")
    rows = []
    for g in data.get("genres", []):
        rows.append({
            "genre_id": g["id"],
            "genre_name": g["name"],
            "fetched_at": datetime.utcnow().isoformat(),
        })
    return pd.DataFrame(rows)


def fetch_top_rated_movies(pages=5):
    rows = []
    for p in range(1, pages + 1):
        data = tmdb_get("/movie/top_rated", page=p)
        for item in data.get("results", []):
            rows.append({
                "tmdb_id": item["id"],
                "title": item.get("title"),
                "vote_average": item.get("vote_average"),
                "vote_count": item.get("vote_count"),
                "popularity": item.get("popularity"),
                "release_date": item.get("release_date"),
                "genre_ids": json.dumps(item.get("genre_ids", [])),
                "overview": item.get("overview"),
                "fetched_at": datetime.utcnow().isoformat(),
            })
    return pd.DataFrame(rows)


def fetch_upcoming_movies(pages=5):
    rows = []
    for p in range(1, pages + 1):
        data = tmdb_get("/movie/upcoming", page=p)
        for item in data.get("results", []):
            rows.append({
                "tmdb_id": item["id"],
                "title": item.get("title"),
                "release_date": item.get("release_date"),
                "popularity": item.get("popularity"),
                "vote_average": item.get("vote_average"),
                "vote_count": item.get("vote_count"),
                "genre_ids": json.dumps(item.get("genre_ids", [])),
                "overview": item.get("overview"),
                "fetched_at": datetime.utcnow().isoformat(),
            })
    return pd.DataFrame(rows)


# ── Genre popularity: discover by genre and count results ───────────────────

def fetch_genre_popularity(genre_df):
    """
    For each genre, run /discover/movie with that genre_id and sort_by=popularity.desc
    We just fetch page 1 and record the top popularity score + total result count.
    """
    rows = []
    for _, row in genre_df.iterrows():
        gid = row["genre_id"]
        gname = row["genre_name"]
        try:
            data = tmdb_get("/discover/movie", params={
                "with_genres": gid,
                "sort_by": "popularity.desc",
            }, page=1)
            results = data.get("results", [])
            top_pop = results[0]["popularity"] if results else 0.0
            total_results = data.get("total_results", 0)
            rows.append({
                "genre_id": gid,
                "genre_name": gname,
                "top_movie_popularity": top_pop,
                "total_movies_in_genre": total_results,
                "fetched_at": datetime.utcnow().isoformat(),
            })
        except Exception as e:
            print(f"  [WARN] Genre {gname} ({gid}) failed: {e}")
            rows.append({
                "genre_id": gid,
                "genre_name": gname,
                "top_movie_popularity": 0.0,
                "total_movies_in_genre": 0,
                "fetched_at": datetime.utcnow().isoformat(),
            })
    return pd.DataFrame(rows)


# ── Main entrypoint ─────────────────────────────────────────────────────────

def fetch_all(data_dir="data"):
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    print(f"\n{'='*60}")
    print(f"TMDB LIVE FETCH — {datetime.utcnow().isoformat()}")
    print(f"{'='*60}\n")

    datasets = {}

    print("[1/6] Fetching trending movies (daily)...")
    datasets["trending_movies"] = fetch_trending_movies(pages=5)
    print(f"       Records: {len(datasets['trending_movies']):,}")

    print("[2/6] Fetching popular TV shows...")
    datasets["popular_tv"] = fetch_popular_tv(pages=5)
    print(f"       Records: {len(datasets['popular_tv']):,}")

    print("[3/6] Fetching movie genres...")
    datasets["movie_genres"] = fetch_movie_genres()
    print(f"       Records: {len(datasets['movie_genres']):,}")

    print("[4/6] Fetching top-rated movies...")
    datasets["top_rated_movies"] = fetch_top_rated_movies(pages=5)
    print(f"       Records: {len(datasets['top_rated_movies']):,}")

    print("[5/6] Fetching upcoming releases...")
    datasets["upcoming_movies"] = fetch_upcoming_movies(pages=5)
    print(f"       Records: {len(datasets['upcoming_movies']):,}")

    print("[6/6] Fetching genre popularity via discover...")
    datasets["genre_popularity"] = fetch_genre_popularity(datasets["movie_genres"])
    print(f"       Records: {len(datasets['genre_popularity']):,}")

    # Save CSVs
    for name, df in datasets.items():
        path = Path(data_dir) / f"{name}_{ts}.csv"
        df.to_csv(path, index=False)
        print(f"  ✓ Saved {name}: {path.name} ({len(df):,} rows)")

    # Also save as "latest" without timestamp for easy notebook loading
    for name, df in datasets.items():
        path = Path(data_dir) / f"{name}_latest.csv"
        df.to_csv(path, index=False)

    # Write manifest
    manifest = {
        "fetched_at": datetime.utcnow().isoformat(),
        "timestamp_suffix": ts,
        "record_counts": {k: len(v) for k, v in datasets.items()},
        "files": [f"{k}_{ts}.csv" for k in datasets.keys()] + [f"{k}_latest.csv" for k in datasets.keys()],
    }
    manifest_path = Path(data_dir) / f"manifest_{ts}.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\n  ✓ Manifest: {manifest_path.name}")

    print(f"\n{'='*60}")
    print("FETCH COMPLETE — all data is live from TMDB API")
    print(f"{'='*60}\n")
    return datasets, manifest


if __name__ == "__main__":
    fetch_all()
