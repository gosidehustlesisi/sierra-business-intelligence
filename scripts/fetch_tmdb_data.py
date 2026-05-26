#!/usr/bin/env python3
"""
Fetch TMDB data for Netflix notebooks.
Run before executing notebooks to ensure data files exist.
"""
import os, json, time, pandas as pd
from pathlib import Path
import requests

API_KEY = os.environ.get("TMDB_API_KEY", "")
if not API_KEY or API_KEY == "demo":
    API_KEY = "b96521e9c5e91e11151fa17741acc0d8"

BASE_URL = "https://api.themoviedb.org/3"

def tmdb_get(endpoint, params=None):
    url = f"{BASE_URL}{endpoint}"
    default_params = {"api_key": API_KEY}
    if params:
        default_params.update(params)
    try:
        resp = requests.get(url, params=default_params, timeout=30)
        if resp.status_code == 429:
            time.sleep(1)
            return tmdb_get(endpoint, params)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"  API error for {endpoint}: {e}")
        return {"results": []}

def main():
    data_dir = Path("projects/netflix-content-strategy-intelligence/data")
    data_dir.mkdir(parents=True, exist_ok=True)
    print(f"Writing data to: {data_dir.absolute()}")
    
    endpoints = [
        ("/trending/movie/day", "trending_movies_latest.csv", 
         lambda r: {"id": r["id"], "title": r.get("title", ""), "popularity": r.get("popularity", 0),
                    "vote_average": r.get("vote_average", 0), "vote_count": r.get("vote_count", 0),
                    "release_date": r.get("release_date", ""), "genre_ids": json.dumps(r.get("genre_ids", []))}),
        ("/tv/popular", "popular_tv_latest.csv",
         lambda r: {"id": r["id"], "name": r.get("name", ""), "popularity": r.get("popularity", 0),
                    "vote_average": r.get("vote_average", 0), "vote_count": r.get("vote_count", 0),
                    "first_air_date": r.get("first_air_date", ""), "genre_ids": json.dumps(r.get("genre_ids", []))}),
        ("/genre/movie/list", "movie_genres_latest.csv",
         lambda r: {"id": r["id"], "name": r.get("name", "")}),
    ]
    
    for endpoint, filename, mapper in endpoints:
        print(f"Fetching {filename}...")
        try:
            data = tmdb_get(endpoint)
            results = data.get("results", [])
            if results:
                df = pd.DataFrame([mapper(r) for r in results])
                df.to_csv(data_dir / filename, index=False)
                print(f"  ✓ {filename} ({len(df)} rows)")
            else:
                print(f"  ⚠ {filename}: no results")
        except Exception as e:
            print(f"  ✗ {filename}: {e}")
    
    # Genre popularity
    print("Fetching genre_popularity_latest.csv...")
    try:
        trending = tmdb_get("/trending/movie/day")
        results = trending.get("results", [])
        genre_counts = {}
        for r in results:
            for gid in r.get("genre_ids", []):
                genre_counts[gid] = genre_counts.get(gid, 0) + 1
        genres = tmdb_get("/genre/movie/list").get("genres", [])
        df = pd.DataFrame([{"genre_id": g["id"], "genre_name": g["name"], 
                            "movie_count": genre_counts.get(g["id"], 0)} for g in genres])
        df.to_csv(data_dir / "genre_popularity_latest.csv", index=False)
        print(f"  ✓ genre_popularity_latest.csv ({len(df)} rows)")
    except Exception as e:
        print(f"  ✗ genre_popularity_latest.csv: {e}")
    
    # Upcoming
    print("Fetching upcoming_movies_latest.csv...")
    try:
        data = tmdb_get("/movie/upcoming")
        results = data.get("results", [])
        df = pd.DataFrame([{"id": r["id"], "title": r.get("title", ""), "popularity": r.get("popularity", 0),
                            "vote_average": r.get("vote_average", 0), "release_date": r.get("release_date", ""),
                            "genre_ids": json.dumps(r.get("genre_ids", []))} for r in results])
        df.to_csv(data_dir / "upcoming_movies_latest.csv", index=False)
        print(f"  ✓ upcoming_movies_latest.csv ({len(df)} rows)")
    except Exception as e:
        print(f"  ✗ upcoming_movies_latest.csv: {e}")
    
    # Top rated
    print("Fetching top_rated_movies_latest.csv...")
    try:
        data = tmdb_get("/movie/top_rated")
        results = data.get("results", [])
        df = pd.DataFrame([{"id": r["id"], "title": r.get("title", ""), "popularity": r.get("popularity", 0),
                            "vote_average": r.get("vote_average", 0), "vote_count": r.get("vote_count", 0),
                            "release_date": r.get("release_date", ""), "genre_ids": json.dumps(r.get("genre_ids", []))} for r in results])
        df.to_csv(data_dir / "top_rated_movies_latest.csv", index=False)
        print(f"  ✓ top_rated_movies_latest.csv ({len(df)} rows)")
    except Exception as e:
        print(f"  ✗ top_rated_movies_latest.csv: {e}")
    
    print("\nTMDB data fetch complete.")

if __name__ == "__main__":
    main()