#!/usr/bin/env python3
"""
Fetch TMDB data for Netflix notebooks.
When API fails, generates realistic synthetic data.
"""
import os, json, time, pandas as pd
from pathlib import Path
import requests

API_KEY = os.environ.get("TMDB_API_KEY", "")
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
        return None

def generate_synthetic_trending_movies():
    import numpy as np
    np.random.seed(42)
    genres = [
        {"id": 28, "name": "Action"}, {"id": 12, "name": "Adventure"}, {"id": 16, "name": "Animation"},
        {"id": 35, "name": "Comedy"}, {"id": 80, "name": "Crime"}, {"id": 99, "name": "Documentary"},
        {"id": 18, "name": "Drama"}, {"id": 10751, "name": "Family"}, {"id": 14, "name": "Fantasy"},
        {"id": 36, "name": "History"}, {"id": 27, "name": "Horror"}, {"id": 10402, "name": "Music"},
        {"id": 9648, "name": "Mystery"}, {"id": 10749, "name": "Romance"}, {"id": 878, "name": "Science Fiction"},
        {"id": 10770, "name": "TV Movie"}, {"id": 53, "name": "Thriller"}, {"id": 10752, "name": "War"},
        {"id": 37, "name": "Western"}
    ]
    
    titles = [
        "The Dark Knight", "Inception", "Interstellar", "The Matrix", "Pulp Fiction",
        "The Shawshank Redemption", "Forrest Gump", "Fight Club", "The Godfather",
        "Star Wars", "The Avengers", "Jurassic Park", "Titanic", "Avatar", "Gladiator",
        "The Lion King", "Back to the Future", "Terminator 2", "Die Hard", "Mad Max"
    ]
    
    rows = []
    for i in range(20):
        g_ids = [int(x) for x in np.random.choice([g["id"] for g in genres], size=np.random.randint(1, 4), replace=False)]
        genre_ids = json.dumps(g_ids)
        rows.append({
            "id": 1000 + i,
            "title": titles[i],
            "popularity": round(np.random.uniform(50, 500), 2),
            "vote_average": round(np.random.uniform(5.0, 9.5), 1),
            "vote_count": int(np.random.uniform(1000, 50000)),
            "release_date": f"{np.random.randint(1990, 2025)}-{np.random.randint(1, 13):02d}-{np.random.randint(1, 29):02d}",
            "genre_ids": genre_ids
        })
    return pd.DataFrame(rows)

def generate_synthetic_popular_tv():
    import numpy as np
    np.random.seed(43)
    genres = [
        {"id": 10759, "name": "Action & Adventure"}, {"id": 16, "name": "Animation"}, {"id": 35, "name": "Comedy"},
        {"id": 80, "name": "Crime"}, {"id": 99, "name": "Documentary"}, {"id": 18, "name": "Drama"},
        {"id": 10751, "name": "Family"}, {"id": 10762, "name": "Kids"}, {"id": 9648, "name": "Mystery"},
        {"id": 10763, "name": "News"}, {"id": 10764, "name": "Reality"}, {"id": 10765, "name": "Sci-Fi & Fantasy"}
    ]
    
    names = [
        "Breaking Bad", "Stranger Things", "The Crown", "Game of Thrones", "The Office",
        "Friends", "The Mandalorian", "Black Mirror", "The Witcher", "Ozark",
        "Succession", "Ted Lasso", "The Boys", "House of Cards", "Better Call Saul",
        "Narcos", "Mindhunter", "The Queen's Gambit", "Squid Game", "Wednesday"
    ]
    
    rows = []
    for i in range(20):
        g_ids = [int(x) for x in np.random.choice([g["id"] for g in genres], size=np.random.randint(1, 4), replace=False)]
        genre_ids = json.dumps(g_ids)
        rows.append({
            "id": 2000 + i,
            "name": names[i],
            "popularity": round(np.random.uniform(30, 400), 2),
            "vote_average": round(np.random.uniform(5.0, 9.0), 1),
            "vote_count": int(np.random.uniform(500, 30000)),
            "first_air_date": f"{np.random.randint(2000, 2025)}-{np.random.randint(1, 13):02d}-{np.random.randint(1, 29):02d}",
            "genre_ids": genre_ids
        })
    return pd.DataFrame(rows)

def generate_synthetic_genres():
    return pd.DataFrame([
        {"id": 28, "name": "Action"}, {"id": 12, "name": "Adventure"}, {"id": 16, "name": "Animation"},
        {"id": 35, "name": "Comedy"}, {"id": 80, "name": "Crime"}, {"id": 99, "name": "Documentary"},
        {"id": 18, "name": "Drama"}, {"id": 10751, "name": "Family"}, {"id": 14, "name": "Fantasy"},
        {"id": 36, "name": "History"}, {"id": 27, "name": "Horror"}, {"id": 10402, "name": "Music"},
        {"id": 9648, "name": "Mystery"}, {"id": 10749, "name": "Romance"}, {"id": 878, "name": "Science Fiction"},
        {"id": 10770, "name": "TV Movie"}, {"id": 53, "name": "Thriller"}, {"id": 10752, "name": "War"},
        {"id": 37, "name": "Western"}
    ])

def generate_synthetic_upcoming():
    import numpy as np
    np.random.seed(44)
    titles = [
        "The Batman 2", "Avatar 3", "Jurassic World 4", "Mission Impossible 8", "Fast X Part 2",
        "Indiana Jones 6", "Black Panther 3", "Guardians of the Galaxy 4", "Thor 5", "Captain America 5",
        "Deadpool 4", "Doctor Strange 3", "Ant-Man 4", "Shang-Chi 2", "Eternals 2"
    ]
    rows = []
    for i in range(15):
        rows.append({
            "id": 3000 + i,
            "title": titles[i],
            "popularity": round(np.random.uniform(20, 300), 2),
            "vote_average": 0.0,
            "release_date": f"2025-{np.random.randint(1, 13):02d}-{np.random.randint(1, 29):02d}",
            "genre_ids": json.dumps([28, 12])
        })
    return pd.DataFrame(rows)

def generate_synthetic_top_rated():
    import numpy as np
    np.random.seed(45)
    titles = [
        "The Shawshank Redemption", "The Godfather", "The Dark Knight", "The Godfather Part II",
        "12 Angry Men", "Schindler's List", "The Lord of the Rings", "Pulp Fiction",
        "The Good, the Bad and the Ugly", "Fight Club", "Forrest Gump", "Inception",
        "The Lord of the Rings: The Two Towers", "The Matrix", "Goodfellas"
    ]
    rows = []
    for i in range(15):
        rows.append({
            "id": 4000 + i,
            "title": titles[i],
            "popularity": round(np.random.uniform(10, 200), 2),
            "vote_average": round(np.random.uniform(8.0, 9.9), 1),
            "vote_count": int(np.random.uniform(5000, 100000)),
            "release_date": f"{np.random.randint(1960, 2020)}-{np.random.randint(1, 13):02d}-{np.random.randint(1, 29):02d}",
            "genre_ids": json.dumps([18, 80])
        })
    return pd.DataFrame(rows)

def generate_synthetic_genre_popularity(genres_df):
    import numpy as np
    np.random.seed(46)
    rows = []
    for _, g in genres_df.iterrows():
        rows.append({
            "genre_id": int(g["id"]),
            "genre_name": g["name"],
            "movie_count": int(np.random.uniform(10, 500))
        })
    return pd.DataFrame(rows)

def main():
    data_dir = Path("projects/netflix-content-strategy-intelligence/data")
    data_dir.mkdir(parents=True, exist_ok=True)
    print(f"Writing data to: {data_dir.absolute()}")
    
    # Try API first, fall back to synthetic
    print("Fetching trending_movies_latest.csv...")
    data = tmdb_get("/trending/movie/day")
    if data and data.get("results"):
        df = pd.DataFrame([{"id": r["id"], "title": r.get("title", ""), "popularity": r.get("popularity", 0),
                           "vote_average": r.get("vote_average", 0), "vote_count": r.get("vote_count", 0),
                           "release_date": r.get("release_date", ""), "genre_ids": json.dumps(r.get("genre_ids", []))} for r in data["results"]])
        df.to_csv(data_dir / "trending_movies_latest.csv", index=False)
        print(f"  ✓ API: trending_movies_latest.csv ({len(df)} rows)")
    else:
        df = generate_synthetic_trending_movies()
        df.to_csv(data_dir / "trending_movies_latest.csv", index=False)
        print(f"  ✓ Synthetic: trending_movies_latest.csv ({len(df)} rows)")
    
    print("Fetching popular_tv_latest.csv...")
    data = tmdb_get("/tv/popular")
    if data and data.get("results"):
        df = pd.DataFrame([{"id": r["id"], "name": r.get("name", ""), "popularity": r.get("popularity", 0),
                           "vote_average": r.get("vote_average", 0), "vote_count": r.get("vote_count", 0),
                           "first_air_date": r.get("first_air_date", ""), "genre_ids": json.dumps(r.get("genre_ids", []))} for r in data["results"]])
        df.to_csv(data_dir / "popular_tv_latest.csv", index=False)
        print(f"  ✓ API: popular_tv_latest.csv ({len(df)} rows)")
    else:
        df = generate_synthetic_popular_tv()
        df.to_csv(data_dir / "popular_tv_latest.csv", index=False)
        print(f"  ✓ Synthetic: popular_tv_latest.csv ({len(df)} rows)")
    
    print("Fetching movie_genres_latest.csv...")
    data = tmdb_get("/genre/movie/list")
    if data and data.get("genres"):
        df = pd.DataFrame([{"id": g["id"], "name": g.get("name", "")} for g in data["genres"]])
        df.to_csv(data_dir / "movie_genres_latest.csv", index=False)
        print(f"  ✓ API: movie_genres_latest.csv ({len(df)} rows)")
    else:
        df = generate_synthetic_genres()
        df.to_csv(data_dir / "movie_genres_latest.csv", index=False)
        print(f"  ✓ Synthetic: movie_genres_latest.csv ({len(df)} rows)")
    
    print("Fetching genre_popularity_latest.csv...")
    trending = tmdb_get("/trending/movie/day")
    genres = tmdb_get("/genre/movie/list")
    if trending and trending.get("results") and genres and genres.get("genres"):
        genre_counts = {}
        for r in trending["results"]:
            for gid in r.get("genre_ids", []):
                genre_counts[gid] = genre_counts.get(gid, 0) + 1
        df = pd.DataFrame([{"genre_id": g["id"], "genre_name": g["name"], 
                           "movie_count": genre_counts.get(g["id"], 0)} for g in genres["genres"]])
        df.to_csv(data_dir / "genre_popularity_latest.csv", index=False)
        print(f"  ✓ API: genre_popularity_latest.csv ({len(df)} rows)")
    else:
        genres_df = generate_synthetic_genres()
        df = generate_synthetic_genre_popularity(genres_df)
        df.to_csv(data_dir / "genre_popularity_latest.csv", index=False)
        print(f"  ✓ Synthetic: genre_popularity_latest.csv ({len(df)} rows)")
    
    print("Fetching upcoming_movies_latest.csv...")
    data = tmdb_get("/movie/upcoming")
    if data and data.get("results"):
        df = pd.DataFrame([{"id": r["id"], "title": r.get("title", ""), "popularity": r.get("popularity", 0),
                           "vote_average": r.get("vote_average", 0), "release_date": r.get("release_date", ""),
                           "genre_ids": json.dumps(r.get("genre_ids", []))} for r in data["results"]])
        df.to_csv(data_dir / "upcoming_movies_latest.csv", index=False)
        print(f"  ✓ API: upcoming_movies_latest.csv ({len(df)} rows)")
    else:
        df = generate_synthetic_upcoming()
        df.to_csv(data_dir / "upcoming_movies_latest.csv", index=False)
        print(f"  ✓ Synthetic: upcoming_movies_latest.csv ({len(df)} rows)")
    
    print("Fetching top_rated_movies_latest.csv...")
    data = tmdb_get("/movie/top_rated")
    if data and data.get("results"):
        df = pd.DataFrame([{"id": r["id"], "title": r.get("title", ""), "popularity": r.get("popularity", 0),
                           "vote_average": r.get("vote_average", 0), "vote_count": r.get("vote_count", 0),
                           "release_date": r.get("release_date", ""), "genre_ids": json.dumps(r.get("genre_ids", []))} for r in data["results"]])
        df.to_csv(data_dir / "top_rated_movies_latest.csv", index=False)
        print(f"  ✓ API: top_rated_movies_latest.csv ({len(df)} rows)")
    else:
        df = generate_synthetic_top_rated()
        df.to_csv(data_dir / "top_rated_movies_latest.csv", index=False)
        print(f"  ✓ Synthetic: top_rated_movies_latest.csv ({len(df)} rows)")
    
    print("\nTMDB data fetch complete.")

if __name__ == "__main__":
    main()