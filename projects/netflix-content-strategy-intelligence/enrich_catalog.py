#!/usr/bin/env python3
"""
Enrich the Netflix catalog with TMDB business-intelligence fields.

For every title in netflix_catalog_latest.csv, makes ONE detail call using
append_to_response to pull fields /discover omits — the real BI signals:
budget, revenue (→ ROI), runtime, production companies/countries, status,
keywords/themes, and watch-provider region count. (TV: networks, seasons,
episodes, episode runtime.)

Best practices (per TMDB docs):
  - append_to_response=keywords,watch/providers  → 1 request per title
  - ~40 req/s rate limit (legacy 40/10s retired 2019); throttle + 429 back-off
  - v4 read token (or v3 key)
  - RESUMABLE: re-running skips ids already in the enriched CSV

Usage:
    export TMDB_READ_TOKEN=...        # or TMDB_API_KEY
    python enrich_catalog.py
    python enrich_catalog.py --limit 50   # quick smoke test

Output:
    data/netflix_catalog_enriched.csv   (base columns + BI fields)
    data/netflix_catalog_enriched_manifest.json
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
RATE_SLEEP = 0.03   # ~33/s, under the ~40/s ceiling
APPEND = "keywords,watch/providers"

_AUTH = None


def _auth():
    global _AUTH
    if _AUTH is None:
        token = os.environ.get("TMDB_READ_TOKEN", "").strip()
        if token:
            _AUTH = ({"Authorization": f"Bearer {token}", "accept": "application/json"}, {})
        else:
            key = os.environ.get("TMDB_API_KEY", "").strip()
            if not key:
                sys.exit("[ERROR] Set TMDB_READ_TOKEN or TMDB_API_KEY.")
            _AUTH = ({"accept": "application/json"}, {"api_key": key})
    return _AUTH


def tmdb_get(endpoint, params=None):
    headers, auth_params = _auth()
    req = dict(auth_params)
    req.update(params or {})
    time.sleep(RATE_SLEEP)
    for attempt in range(4):
        r = requests.get(f"{TMDB_BASE}{endpoint}", headers=headers, params=req, timeout=30)
        if r.status_code == 429:
            time.sleep(2 + attempt * 2)
            continue
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()
    return None


def _names(items, key="name", n=None):
    vals = [i.get(key, "") for i in (items or []) if i.get(key)]
    return "|".join(vals[:n] if n else vals)


def enrich_one(tmdb_id, media_type):
    is_movie = media_type == "movie"
    ep = f"/{'movie' if is_movie else 'tv'}/{tmdb_id}"
    d = tmdb_get(ep, {"append_to_response": APPEND})
    if not d:
        return None
    kw = d.get("keywords", {})
    keywords = kw.get("keywords") if is_movie else kw.get("results")
    providers = (d.get("watch/providers", {}) or {}).get("results", {})
    runtime = d.get("runtime") if is_movie else (
        (d.get("episode_run_time") or [None])[0])
    budget = d.get("budget", 0) or 0
    revenue = d.get("revenue", 0) or 0
    return {
        "tmdb_id": tmdb_id,
        "media_type": media_type,
        "budget": budget,
        "revenue": revenue,
        "roi": round(revenue / budget, 3) if budget > 0 and revenue > 0 else None,
        "runtime": runtime,
        "status": d.get("status"),
        "production_companies": _names(d.get("production_companies"), n=5),
        "production_countries": _names(d.get("production_countries"), key="iso_3166_1"),
        "networks": _names(d.get("networks"), n=5) if not is_movie else "",
        "seasons": d.get("number_of_seasons") if not is_movie else None,
        "episodes": d.get("number_of_episodes") if not is_movie else None,
        "keywords": _names(keywords, n=12),
        "provider_regions": len(providers),
        "enriched_at": datetime.now(timezone.utc).isoformat(),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", default="data/netflix_catalog_latest.csv")
    ap.add_argument("--out", default="data/netflix_catalog_enriched.csv")
    ap.add_argument("--limit", type=int, default=0, help="cap titles (smoke test)")
    args = ap.parse_args()

    base = pd.read_csv(args.catalog)
    out_path = Path(args.out)

    # Resumable: load already-enriched ids
    done = {}
    if out_path.exists():
        prev = pd.read_csv(out_path)
        done = {(r.media_type, int(r.tmdb_id)): r._asdict() for r in prev.itertuples(index=False)}
        print(f"Resuming — {len(done)} titles already enriched")

    todo = [(r.media_type, int(r.tmdb_id)) for r in base.itertuples(index=False)
            if (r.media_type, int(r.tmdb_id)) not in done]
    if args.limit:
        todo = todo[:args.limit]
    print(f"Enriching {len(todo)} titles (1 append_to_response call each)...")

    rows = list(done.values())
    for i, (mt, tid) in enumerate(todo, 1):
        try:
            e = enrich_one(tid, mt)
            if e:
                rows.append(e)
        except Exception as ex:
            print(f"  [warn] {mt}/{tid}: {ex}")
        if i % 250 == 0:
            print(f"  {i}/{len(todo)} — checkpoint save ({len(rows)} rows)")
            pd.DataFrame(rows).to_csv(out_path, index=False)

    enr = pd.DataFrame(rows)
    # Merge BI fields onto the base catalog (one row per title)
    merged = base.merge(enr, on=["tmdb_id", "media_type"], how="left", suffixes=("", "_e"))
    merged.to_csv(out_path, index=False)

    funded = enr[(enr["budget"].fillna(0) > 0) & (enr["revenue"].fillna(0) > 0)]
    manifest = {
        "enriched_at": datetime.now(timezone.utc).isoformat(),
        "total_titles": int(len(merged)),
        "with_runtime": int(enr["runtime"].notna().sum()),
        "with_budget_and_revenue": int(len(funded)),
        "with_keywords": int((enr["keywords"].fillna("") != "").sum()),
        "source": "TMDB /movie|tv/{id}?append_to_response=keywords,watch/providers",
        "note": "Budget/revenue populated mainly for theatrical films; ROI charts use the funded subset.",
    }
    Path(str(out_path).replace(".csv", "_manifest.json")).write_text(json.dumps(manifest, indent=2))
    print(f"\n  ✓ {len(merged):,} titles → {out_path}")
    print(f"  ✓ runtime: {manifest['with_runtime']:,} | budget+revenue: {manifest['with_budget_and_revenue']:,} | keywords: {manifest['with_keywords']:,}")


if __name__ == "__main__":
    main()
