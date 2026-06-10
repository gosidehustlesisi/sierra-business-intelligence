#!/usr/bin/env python3
"""
Fetch live TMDB data for Netflix notebooks.

REQUIREMENTS:
  - TMDB_API_KEY environment variable must be set.
  - Get a free key at: https://www.themoviedb.org/settings/api
  - Store in GitHub Secrets as TMDB_API_KEY (never in source code).

This script fetches real API data only. It does NOT generate synthetic
fallback data. If the API key is missing or invalid, the script exits
with a non-zero code so CI fails explicitly rather than silently
substituting fake data.
"""
import os
import sys
import json
import time
import pandas as pd
from pathlib import Path
import requests

API_KEY = os.environ.get("TMDB_API_KEY", "")

if not API_KEY:
    print("ERROR: TMDB_API_KEY environment variable is not set.")
    print("Set it via GitHub Secrets or a local .env file (never commit the key).")
    sys.exit(1)

BASE_URL = "https://api.themoviedb.org/3"


def tmdb_get(endpoint, params=None):
    """Make a GET request to the TMDB API. Returns parsed JSON or raises on failure."""
    url = f"{BASE_URL}{endpoint}"
    default_params = {"api_key": API_KEY}
    if params:
        default_params.update(params)
    try:
        resp = requests.get(url, params=default_params, timeout=30)
        if resp.status_code == 401:
            print("ERROR: TMDB API returned 401 Unauthorized. Check that TMDB_API_KEY is valid.")
            sys.exit(1)
        if resp.status_code == 429:
            print("  Rate limited - waiting 10 seconds...")
            time.sleep(10)
            return tmdb_get(endpoint, params)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"  Network error for {endpoint}: {e}")
        raise


def fetch_and_save(endpoint, filename, mapper, data_dir):
    """Fetch one TMDB endpoint, parse results, and save to CSV."""
    print(f"Fetching {filename}...")
    data = tmdb_get(endpoint)
    results = data.get("results", data.get("genres", []))
    if not results:
        print(f"  WARNING: No results returned for {endpoint}. Skipping {filename}.")
        return 0
    df = pd.DataFrame([mapper(r) for r in results])
    df.to_csv(data_dir / filename, index=False)
    print(f"  Saved {filename} ({len(df)} rows)")
    return len(df)


def main():
    data_dir = Path("projects/netflix-content-strategy-intelligence/data")
    data_dir.mkdir(parents=True, exist_ok=True)
    print(f"Writing live TMDB data to: {data_dir.absolute()}")

    total_records = 0

    total_records += fetch_and_save(
        "/trending/movie/day", "trending_movies_latest.csv",
        lambda r: {
            "id": r["id"], "title": r.get("title", ""), "popularity": r.get("popularity", 0),
            "vote_average": r.get("vote_average", 0), "vote_count": r.get("vote_count", 0),
            "release_date": r.get("release_date", ""), "genre_ids": json.dumps(r.get("genre_ids", []))
        },
        data_dir
    )

    total_records += fetch_and_save(
        "/tv/popular", "popular_tv_latest.csv",
        lambda r: {
            "id": r["id"], "name": r.get("name", ""), "popularity": r.get("popularity", 0),
            "vote_average": r.get("vote_average", 0), "vote_count": r.get("vote_count", 0),
            "first_air_date": r.get("first_air_date", ""), "genre_ids": json.dumps(r.get("genre_ids", []))
        },
        data_dir
    )

    total_records += fetch_and_save(
        "/genre/movie/list", "movie_genres_latest.csv",
        lambda r: {"id": r["id"], "name": r.get("name", "")},
        data_dir
    )

    total_records += fetch_and_save(
        "/movie/upcoming", "upcoming_movies_latest.csv",
        lambda r: {
            "id": r["id"], "title": r.get("title", ""), "popularity": r.get("popularity", 0),
            "vote_average": r.get("vote_average", 0), "release_date": r.get("release_date", ""),
            "genre_ids": json.dumps(r.get("genre_ids", []))
        },
        data_dir
    )

    total_records += fetch_and_save(
        "/movie/top_rated", "top_rated_movies_latest.csv",
        lambda r: {
            "id": r["id"], "title": r.get("title", ""), "popularity": r.get("popularity", 0),
            "vote_average": r.get("vote_average", 0), "vote_count": r.get("vote_count", 0),
            "release_date": r.get("release_date", ""), "genre_ids": json.dumps(r.get("genre_ids", []))
        },
        data_dir
    )

    # Genre popularity: compute from trending data
    print("Computing genre_popularity_latest.csv from trending data...")
    trending = tmdb_get("/trending/movie/day")
    genres = tmdb_get("/genre/movie/list")
    genre_counts = {}
    for r in trending.get("results", []):
        for gid in r.get("genre_ids", []):
            genre_counts[gid] = genre_counts.get(gid, 0) + 1
    df = pd.DataFrame([
        {"genre_id": g["id"], "genre_name": g["name"], "movie_count": genre_counts.get(g["id"], 0)}
        for g in genres.get("genres", [])
    ])
    df.to_csv(data_dir / "genre_popularity_latest.csv", index=False)
    total_records += len(df)
    print(f"  Saved genre_popularity_latest.csv ({len(df)} rows)")

    print(f"\nTMDB live fetch complete. Total records written: {total_records}")


if __name__ == "__main__":
    main()
