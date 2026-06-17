#!/usr/bin/env python3
"""
Netflix Catalog Analysis — figures from the self-extracted TMDB catalog.

Reads the first-party catalog produced by fetch_netflix_catalog.py and renders
the catalog-layer figures (genre structure, content mix, release-era trends,
real TMDB score distributions). STRICT SOURCE SEPARATION: every figure here is
built ONLY from the catalog CSV — never mixed with the live trending/top-rated
snapshot. Each figure is stamped with its source + extraction date so a reviewer
can trace any number back to a reproducible pull.

Usage:
    python catalog_analysis.py
    python catalog_analysis.py --catalog data/netflix_catalog_latest.csv --out ../../docs/figures

Outputs nflx_01..nflx_09 PNGs (the catalog figures) + prints a stats summary
used for the page copy. nflx_10 (upcoming) stays a live-layer figure.
"""

import argparse
import json
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Brand accents (match the SnapAIArchitect.BI house style)
GOLD = "#f59e0b"
CYAN = "#06b6d4"
INK = "#0f1115"
GRID = "#d9dee8"
PALETTE = [GOLD, CYAN, "#22c55e", "#e11d48", "#8b5cf6", "#f97316", "#14b8a6", "#eab308"]

plt.rcParams.update({
    "figure.figsize": (10, 6), "figure.dpi": 120, "savefig.dpi": 120,
    "axes.facecolor": "white", "figure.facecolor": "white",
    "axes.edgecolor": GRID, "axes.grid": True, "grid.color": GRID, "grid.alpha": 0.5,
    "axes.titlesize": 15, "axes.titleweight": "bold", "font.size": 11,
})


def _stamp(fig, src):
    fig.text(0.99, 0.01, src, ha="right", va="bottom", fontsize=7,
             color="#6b7280", style="italic")


def _save(fig, out, name, src):
    _stamp(fig, src)
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    path = Path(out) / name
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {name}")


def explode_genres(df):
    """One row per (title, genre) from the pipe-joined genres column."""
    s = df["genres"].fillna("").str.split("|")
    ex = df.assign(genre=s).explode("genre")
    ex["genre"] = ex["genre"].str.strip()
    return ex[ex["genre"] != ""]


def fig_genre_distribution(df, out, src):
    g = explode_genres(df)["genre"].value_counts()
    fig, ax = plt.subplots()
    g.sort_values().plot.barh(ax=ax, color=CYAN)
    ax.set_title("Genre Distribution — Full Netflix Catalog")
    ax.set_xlabel("Titles"); ax.set_ylabel("")
    _save(fig, out, "nflx_01_genre_distribution.png", src)


def fig_popularity_vs_rating(df, out, src):
    d = df.dropna(subset=["popularity", "vote_average"])
    d = d[d["vote_count"].fillna(0) >= 10]  # avoid noise from unrated titles
    fig, ax = plt.subplots()
    ax.scatter(d["vote_average"], d["popularity"], s=12, alpha=0.4, color=GOLD)
    ax.set_title("Popularity vs Rating (real TMDB scores)")
    ax.set_xlabel("Vote average"); ax.set_ylabel("Popularity")
    _save(fig, out, "nflx_02_popularity_vs_rating.png", src)


def fig_rating_distribution(df, out, src):
    d = df[df["vote_count"].fillna(0) >= 10]["vote_average"].dropna()
    fig, ax = plt.subplots()
    ax.hist(d, bins=20, color=CYAN, edgecolor="white")
    ax.axvline(d.mean(), color=GOLD, lw=2, label=f"mean {d.mean():.2f}")
    ax.set_title("Rating Distribution (titles with ≥10 votes)")
    ax.set_xlabel("Vote average"); ax.set_ylabel("Titles"); ax.legend()
    _save(fig, out, "nflx_03_rating_distribution.png", src)


def fig_release_trends(df, out, src):
    d = df.dropna(subset=["release_year"])
    d = d[(d["release_year"] >= 1950) & (d["release_year"] <= 2026)]
    by_year = d["release_year"].astype(int).value_counts().sort_index()
    fig, ax = plt.subplots()
    ax.plot(by_year.index, by_year.values, color=GOLD, lw=2)
    ax.fill_between(by_year.index, by_year.values, color=GOLD, alpha=0.15)
    ax.set_title("Catalog by Release Year")
    ax.set_xlabel("Release year"); ax.set_ylabel("Titles")
    _save(fig, out, "nflx_04_release_trends.png", src)


def fig_top_genres(df, out, src):
    g = explode_genres(df)["genre"].value_counts().head(15)
    fig, ax = plt.subplots()
    g.sort_values().plot.barh(ax=ax, color=GOLD)
    ax.set_title("Top 15 Genres by Title Count")
    ax.set_xlabel("Titles"); ax.set_ylabel("")
    _save(fig, out, "nflx_05_top_genres.png", src)


def fig_content_growth(df, out, src):
    d = df.dropna(subset=["release_year"])
    d = d[(d["release_year"] >= 1990) & (d["release_year"] <= 2026)]
    piv = (d.assign(year=d["release_year"].astype(int))
             .groupby(["year", "media_type"]).size().unstack(fill_value=0))
    fig, ax = plt.subplots()
    bottom = None
    for i, col in enumerate(piv.columns):
        ax.bar(piv.index, piv[col], bottom=bottom, label=col, color=PALETTE[i % len(PALETTE)])
        bottom = piv[col] if bottom is None else bottom + piv[col]
    ax.set_title("Content Growth by Type (release year)")
    ax.set_xlabel("Release year"); ax.set_ylabel("Titles"); ax.legend()
    _save(fig, out, "nflx_06_content_growth.png", src)


def fig_content_mix(df, out, src):
    counts = df["media_type"].value_counts()
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%",
           colors=[GOLD, CYAN, PALETTE[2]][:len(counts)],
           wedgeprops={"edgecolor": "white", "linewidth": 2})
    ax.set_title("Content Mix — Movies vs TV")
    _save(fig, out, "nflx_07_content_mix.png", src)


def _squarify(sizes, x, y, w, h):
    """Minimal treemap layout (slice-and-dice). Returns list of (x,y,w,h)."""
    rects, total = [], float(sum(sizes))
    for s in sizes:
        frac = s / total if total else 0
        if w >= h:
            rw = w * frac
            rects.append((x, y, rw, h)); x += rw
        else:
            rh = h * frac
            rects.append((x, y, w, rh)); y += rh
    return rects


def fig_genre_treemap(df, out, src):
    g = explode_genres(df)["genre"].value_counts().head(10)
    fig, ax = plt.subplots()
    rects = _squarify(list(g.values), 0, 0, 100, 100)
    for i, ((name, val), (x, y, w, h)) in enumerate(zip(g.items(), rects)):
        ax.add_patch(plt.Rectangle((x, y), w, h, facecolor=PALETTE[i % len(PALETTE)],
                                    edgecolor="white", linewidth=2))
        if w * h > 60:
            ax.text(x + w / 2, y + h / 2, f"{name}\n{val}", ha="center", va="center",
                    fontsize=9, color="white", fontweight="bold")
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
    ax.set_title("Genre Share (top 10)")
    _save(fig, out, "nflx_08_genre_treemap.png", src)


def fig_quality_tiers(df, out, src):
    d = df[df["vote_count"].fillna(0) >= 10].dropna(subset=["vote_average"]).copy()
    bins = [0, 5, 6, 7, 8, 10]
    labels = ["<5", "5–6", "6–7", "7–8", "8+"]
    d["tier"] = pd.cut(d["vote_average"], bins=bins, labels=labels, include_lowest=True)
    counts = d["tier"].value_counts().reindex(labels, fill_value=0)
    fig, ax = plt.subplots()
    ax.bar(counts.index.astype(str), counts.values, color=PALETTE[:len(counts)])
    ax.set_title("Quality Tiers (vote average)")
    ax.set_xlabel("Rating tier"); ax.set_ylabel("Titles")
    _save(fig, out, "nflx_09_quality_tiers.png", src)


def summarize(df):
    nonen = (df["original_language"].fillna("") != "en").mean() * 100
    rated = df[df["vote_count"].fillna(0) >= 10]
    yrs = df["release_year"].dropna()
    return {
        "total_titles": int(len(df)),
        "movies": int((df["media_type"] == "movie").sum()),
        "tv": int((df["media_type"] == "tv").sum()),
        "pct_non_english": round(float(nonen), 1),
        "mean_vote_average": round(float(rated["vote_average"].mean()), 2) if len(rated) else None,
        "year_min": int(yrs.min()) if len(yrs) else None,
        "year_max": int(yrs.max()) if len(yrs) else None,
        "top_genres": explode_genres(df)["genre"].value_counts().head(5).to_dict(),
    }


def main():
    ap = argparse.ArgumentParser(description="Render Netflix catalog figures from the self-extracted CSV.")
    ap.add_argument("--catalog", default="data/netflix_catalog_latest.csv")
    ap.add_argument("--out", default="../../docs/figures")
    args = ap.parse_args()

    df = pd.read_csv(args.catalog)
    extracted = str(df["extracted_at"].iloc[0])[:10] if "extracted_at" in df and len(df) else "?"
    src = f"Source: TMDB self-extracted Netflix catalog · {len(df):,} titles · {extracted}"
    Path(args.out).mkdir(parents=True, exist_ok=True)
    print(f"Catalog: {len(df):,} titles  →  {args.out}")

    fig_genre_distribution(df, args.out, src)
    fig_popularity_vs_rating(df, args.out, src)
    fig_rating_distribution(df, args.out, src)
    fig_release_trends(df, args.out, src)
    fig_top_genres(df, args.out, src)
    fig_content_growth(df, args.out, src)
    fig_content_mix(df, args.out, src)
    fig_genre_treemap(df, args.out, src)
    fig_quality_tiers(df, args.out, src)

    stats = summarize(df)
    Path(args.out).parent.joinpath("catalog_stats.json").write_text(json.dumps(stats, indent=2))
    print("\nSTATS (for page copy):")
    print(json.dumps(stats, indent=2))
    print("\nAll catalog figures sourced ONLY from the catalog CSV. nflx_10 stays the live layer.")


if __name__ == "__main__":
    main()
