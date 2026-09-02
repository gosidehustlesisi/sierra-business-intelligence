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
import re
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

def get_api_key():
    """Get TMDB API key from Streamlit Cloud secrets or environment."""
    try:
        import streamlit as st
        return st.secrets.get("TMDB_API_KEY", "")
    except Exception:
        pass
    return os.environ.get("TMDB_API_KEY", "").strip()


def get_read_token():
    """Get TMDB read token from Streamlit Cloud secrets or environment."""
    try:
        import streamlit as st
        return st.secrets.get("TMDB_READ_TOKEN", "")
    except Exception:
        pass
    return os.environ.get("TMDB_READ_TOKEN", "").strip()


def get_auth_headers():
    token = get_read_token()
    if token:
        return {"Authorization": f"Bearer {token}", "accept": "application/json"}
    return None


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


# ── Snapshot retention ───────────────────────────────────────────────────────

SNAPSHOT_RE = re.compile(r"^(?P<stem>.+)_(?P<ts>\d{8}_\d{6})\.(?P<ext>csv|json)$")


def prune_old_snapshots(data_dir="data", keep=14):
    """Delete timestamped dataset snapshots beyond the most recent `keep` per dataset.

    Matches files like trending_movies_20260810_060012.csv and manifest_20260810_060012.json,
    grouping by the stem before the timestamp. Never touches *_latest.csv files.
    """
    data_path = Path(data_dir)
    groups = {}
    for f in data_path.iterdir():
        if not f.is_file():
            continue
        m = SNAPSHOT_RE.match(f.name)
        if not m:
            continue
        groups.setdefault(m.group("stem"), []).append((m.group("ts"), f))

    for stem, snapshots in groups.items():
        snapshots.sort(key=lambda x: x[0], reverse=True)
        for _, f in snapshots[keep:]:
            f.unlink()
            print(f"  ✓ Pruned old snapshot: {f.name}")


# ── Main entrypoint ─────────────────────────────────────────────────────────

def fetch_movie_trailers(movie_ids):
    """
    Fetch YouTube trailer keys for a list of movie IDs.
    TMDB /movie/{id}/videos endpoint returns videos with type='Trailer' and site='YouTube'.
    Returns dict: {tmdb_id: {'youtube_key': str, 'name': str, 'type': str}}
    """
    trailers = {}
    for mid in movie_ids:
        try:
            data = tmdb_get(f"/movie/{mid}/videos")
            results = data.get("results", [])
            # Prefer official trailer, fallback to any trailer
            trailer = None
            for v in results:
                if v.get("type") == "Trailer" and v.get("site") == "YouTube":
                    if "official" in v.get("name", "").lower() or not trailer:
                        trailer = v
                        if "official" in v.get("name", "").lower():
                            break
            if trailer:
                trailers[mid] = {
                    "youtube_key": trailer["key"],
                    "trailer_name": trailer.get("name", ""),
                    "trailer_type": trailer.get("type", ""),
                }
        except Exception as e:
            print(f"  [WARN] Trailer fetch failed for movie {mid}: {e}")
    return trailers


def enrich_with_trailers(df, trailers_dict):
    """Add trailer columns to a movie DataFrame."""
    df = df.copy()
    df["youtube_key"] = df["tmdb_id"].map(lambda x: trailers_dict.get(x, {}).get("youtube_key", ""))
    df["trailer_name"] = df["tmdb_id"].map(lambda x: trailers_dict.get(x, {}).get("trailer_name", ""))
    df["trailer_type"] = df["tmdb_id"].map(lambda x: trailers_dict.get(x, {}).get("trailer_type", ""))
    df["trailer_url"] = df["youtube_key"].apply(lambda k: f"https://www.youtube.com/watch?v={k}" if k else "")
    return df


def fetch_all(data_dir="data"):
    """Fetch all live TMDB datasets, save CSVs + manifest, return (datasets, manifest)."""
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

    # ── Fetch trailers for all movie datasets ───────────────────────────────
    print("\n[7/7] Fetching YouTube trailers for all movies...")
    all_movie_ids = set()
    for name in ["trending_movies", "top_rated_movies", "upcoming_movies"]:
        if name in datasets:
            all_movie_ids.update(datasets[name]["tmdb_id"].tolist())
    print(f"       Unique movie IDs: {len(all_movie_ids)}")
    trailers = fetch_movie_trailers(list(all_movie_ids))
    print(f"       Trailers found: {len(trailers)}")

    # Enrich movie datasets with trailer data
    for name in ["trending_movies", "top_rated_movies", "upcoming_movies"]:
        if name in datasets:
            datasets[name] = enrich_with_trailers(datasets[name], trailers)
            # Re-save enriched version
            path = Path(data_dir) / f"{name}_{ts}.csv"
            datasets[name].to_csv(path, index=False)
            path = Path(data_dir) / f"{name}_latest.csv"
            datasets[name].to_csv(path, index=False)

    # Save trailers as separate CSV
    if trailers:
        trailers_df = pd.DataFrame([
            {"tmdb_id": k, **v} for k, v in trailers.items()
        ])
        trailers_df.to_csv(Path(data_dir) / f"trailers_{ts}.csv", index=False)
        trailers_df.to_csv(Path(data_dir) / "trailers_latest.csv", index=False)
        print(f"  ✓ Saved trailers: {len(trailers_df)} records")

    # Write manifest
    manifest = {
        "fetched_at": datetime.utcnow().isoformat(),
        "timestamp_suffix": ts,
        "record_counts": {k: len(v) for k, v in datasets.items()},
        "trailer_count": len(trailers),
        "files": [f"{k}_{ts}.csv" for k in datasets.keys()] + [f"{k}_latest.csv" for k in datasets.keys()],
    }
    manifest_path = Path(data_dir) / f"manifest_{ts}.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    latest_manifest_path = Path(data_dir) / "manifest_latest.json"
    with open(latest_manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\n  ✓ Manifest: {manifest_path.name}")

    prune_old_snapshots(data_dir)

    print(f"\n{'='*60}")
    print("FETCH COMPLETE — all data is live from TMDB API")
    print(f"{'='*60}\n")
    return datasets, manifest


if __name__ == "__main__":
    fetch_all()
