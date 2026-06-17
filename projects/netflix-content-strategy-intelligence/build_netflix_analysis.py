#!/usr/bin/env python3
"""
Build the interactive Netflix catalog analysis page (Plotly).

Reads the self-extracted catalog CSV and renders docs/netflix-analysis.html:
a single brand-styled page with interactive Plotly charts, data-driven analysis
narrative, and a methodology section. Every figure is built ONLY from the
catalog layer; numbers in the prose are computed here, not hard-coded.

Usage:
    python build_netflix_analysis.py
    python build_netflix_analysis.py --catalog data/netflix_catalog_latest.csv --out ../../docs/netflix-analysis.html
"""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

GOLD, CYAN, GREEN, INK, SURFACE, TEXT, MUTED = (
    "#f59e0b", "#06b6d4", "#22c55e", "#0f1115", "#111827", "#f0f0f0", "#94a3b8")

LANG = {"en": "English", "es": "Spanish", "ja": "Japanese", "ko": "Korean",
        "hi": "Hindi", "fr": "French", "de": "German", "it": "Italian",
        "pt": "Portuguese", "zh": "Chinese", "ta": "Tamil", "tr": "Turkish",
        "th": "Thai", "ar": "Arabic", "id": "Indonesian", "pl": "Polish",
        "te": "Telugu", "nl": "Dutch", "sv": "Swedish", "ru": "Russian"}


def _style(fig, height=460):
    fig.update_layout(
        template="plotly_dark", paper_bgcolor=SURFACE, plot_bgcolor=SURFACE,
        font=dict(family="Inter, sans-serif", color=TEXT, size=13),
        title_font=dict(size=18, color=TEXT),
        margin=dict(l=60, r=30, t=60, b=50), height=height,
        colorway=[GOLD, CYAN, GREEN, "#e11d48", "#8b5cf6", "#f97316"],
        xaxis=dict(gridcolor="#1f2d44"), yaxis=dict(gridcolor="#1f2d44"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    return fig


def explode_genres(df):
    s = df["genres"].fillna("").str.split("|")
    ex = df.assign(genre=s).explode("genre")
    ex["genre"] = ex["genre"].str.strip()
    return ex[ex["genre"] != ""]


def build(df):
    """Return list of (chart_html, title, analysis_html)."""
    blocks = []
    rated = df[df["vote_count"].fillna(0) >= 10]
    div = dict(full_html=False, include_plotlyjs=False,
               config={"displayModeBar": True, "responsive": True,
                       "displaylogo": False})

    # 1 — Genre distribution
    g = explode_genres(df)["genre"].value_counts().head(15).sort_values()
    fig = _style(go.Figure(go.Bar(x=g.values, y=g.index, orientation="h",
                 marker_color=CYAN, hovertemplate="%{y}: %{x} titles<extra></extra>")))
    fig.update_layout(title="Genre Distribution — Full Catalog", xaxis_title="Titles")
    top3 = explode_genres(df)["genre"].value_counts().head(3)
    blocks.append((fig.to_html(**div), "Genre mix",
        f"<b>{top3.index[0]} ({top3.iloc[0]:,})</b> and <b>{top3.index[1]} ({top3.iloc[1]:,})</b> "
        f"anchor the library, with <b>{top3.index[2]} ({top3.iloc[2]:,})</b> a strong third — a "
        f"signature of Netflix's originals-era investment in unscripted and prestige nonfiction. "
        f"Genres are multi-label (a title can count in several), so totals exceed the title count."))

    # 2 — Content mix
    mix = df["media_type"].value_counts()
    fig = _style(go.Figure(go.Pie(labels=[m.upper() for m in mix.index], values=mix.values,
                 hole=0.55, marker=dict(colors=[GOLD, CYAN]),
                 hovertemplate="%{label}: %{value} (%{percent})<extra></extra>")), height=420)
    fig.update_layout(title="Content Mix — Movies vs Series")
    mv, tv = int((df.media_type=="movie").sum()), int((df.media_type=="tv").sum())
    blocks.append((fig.to_html(**div), "Supply shape",
        f"The catalog is <b>{mv:,} films</b> and <b>{tv:,} series</b> "
        f"({100*mv/len(df):.0f}% / {100*tv/len(df):.0f}%) — film-tilted in raw count, but the "
        f"series half carries the quality edge (see ratings below)."))

    # 3 — Release-year trend
    yr = df.dropna(subset=["release_year"])
    yr = yr[(yr.release_year >= 1960) & (yr.release_year <= 2026)]
    by = yr["release_year"].astype(int).value_counts().sort_index()
    fig = _style(go.Figure(go.Scatter(x=by.index, y=by.values, fill="tozeroy",
                 line=dict(color=GOLD, width=2), hovertemplate="%{x}: %{y} titles<extra></extra>")))
    fig.update_layout(title="Catalog by Release Year", xaxis_title="Release year", yaxis_title="Titles")
    recent = int(yr[yr.release_year >= 2015].shape[0])
    blocks.append((fig.to_html(**div), "When the catalog was made",
        f"<b>{100*recent/len(yr):.0f}% of dated titles are from 2015 or later</b> — the catalog is "
        f"overwhelmingly a product of the streaming-originals era, with a long tail back to "
        f"{int(yr.release_year.min())}."))

    # 4 — Rating distribution
    fig = _style(go.Figure(go.Histogram(x=rated["vote_average"], nbinsx=22, marker_color=CYAN,
                 hovertemplate="rating %{x}: %{y} titles<extra></extra>")))
    fig.add_vline(x=rated["vote_average"].mean(), line=dict(color=GOLD, width=2, dash="dash"),
                  annotation_text=f"mean {rated['vote_average'].mean():.2f}", annotation_font_color=GOLD)
    fig.update_layout(title="Rating Distribution (titles with ≥10 votes)",
                      xaxis_title="TMDB vote average", yaxis_title="Titles")
    blocks.append((fig.to_html(**div), "How good is it",
        f"Ratings cluster between 6 and 8 with a mean of <b>{rated['vote_average'].mean():.2f}/10</b> "
        f"across {len(rated):,} rated titles — a solidly-curated library, not a volume dump. "
        f"<b>{100*(rated.vote_average>=7).mean():.0f}%</b> sit at 7.0 or higher."))

    # 5 — Popularity vs rating
    d = rated.dropna(subset=["popularity"])
    fig = _style(go.Figure(go.Scattergl(x=d["vote_average"], y=d["popularity"], mode="markers",
                 marker=dict(color=GOLD, size=5, opacity=0.35),
                 text=d["title"], hovertemplate="%{text}<br>rating %{x}, popularity %{y:.0f}<extra></extra>")))
    fig.update_layout(title="Popularity vs Rating", xaxis_title="Vote average",
                      yaxis_title="Popularity", yaxis_type="log")
    corr = d["vote_average"].corr(d["popularity"])
    blocks.append((fig.to_html(**div), "Popular ≠ acclaimed",
        f"Rating and popularity correlate only weakly (r = {corr:.2f}) — what's <i>watched</i> isn't "
        f"what's <i>rated highest</i>. The high-rating / high-popularity quadrant (upper right) is the "
        f"natural shortlist for promotion and acquisition lookalikes."))

    # 6 — Series vs film ratings
    fig = _style(go.Figure())
    for mt, c in [("movie", GOLD), ("tv", CYAN)]:
        fig.add_trace(go.Box(y=rated[rated.media_type==mt]["vote_average"],
                      name=("Movies" if mt=="movie" else "Series"), marker_color=c, boxmean=True))
    fig.update_layout(title="Ratings: Series vs Film", yaxis_title="Vote average", showlegend=False)
    mvr = rated[rated.media_type=="movie"]["vote_average"].mean()
    tvr = rated[rated.media_type=="tv"]["vote_average"].mean()
    blocks.append((fig.to_html(**div), "Series out-rate film",
        f"Series average <b>{tvr:.1f}</b> vs <b>{mvr:.1f}</b> for films — a {tvr-mvr:.1f}-point edge. "
        f"Netflix's heavy series investment shows up as measurably higher audience scores."))

    # 7 — Language breakdown
    lng = df["original_language"].fillna("?").map(lambda x: LANG.get(x, x.upper())).value_counts().head(10).sort_values()
    fig = _style(go.Figure(go.Bar(x=lng.values, y=lng.index, orientation="h", marker_color=GREEN,
                 hovertemplate="%{y}: %{x} titles<extra></extra>")))
    fig.update_layout(title="Top Original Languages", xaxis_title="Titles")
    nonen = 100*(df.original_language.fillna("")!="en").mean()
    blocks.append((fig.to_html(**div), "A global library",
        f"<b>{nonen:.0f}% of the catalog is non-English</b> by original language — Netflix-US is a "
        f"genuinely international service, not a domestic one with subtitles bolted on."))

    # ── BI ENRICHMENT charts (only render if enriched columns are present) ──
    if "budget" in df.columns and df["budget"].fillna(0).gt(0).any():
        funded = df[(df["budget"].fillna(0) > 0) & (df["revenue"].fillna(0) > 0)].copy()
        funded["roi"] = funded["revenue"] / funded["budget"]
        mx = float(max(funded["budget"].max(), funded["revenue"].max()))
        fig = _style(go.Figure(go.Scattergl(
            x=funded["budget"], y=funded["revenue"], mode="markers",
            marker=dict(size=(funded["popularity"].clip(upper=300) / 18 + 4),
                        color=funded["roi"].clip(upper=10), colorscale="Plasma",
                        showscale=True, colorbar=dict(title="ROI×"), opacity=0.6),
            text=funded["title"],
            hovertemplate="%{text}<br>budget $%{x:,.0f}<br>revenue $%{y:,.0f}<extra></extra>")))
        fig.add_trace(go.Scatter(x=[1, mx], y=[1, mx], mode="lines",
                      line=dict(color=MUTED, dash="dash"), name="break-even", hoverinfo="skip"))
        fig.update_layout(title="Revenue vs Budget — Return on Investment",
                          xaxis_title="Budget ($)", yaxis_title="Revenue ($)",
                          xaxis_type="log", yaxis_type="log", showlegend=False)
        profit = (funded["roi"] > 1).mean() * 100
        blocks.append((fig.to_html(**div), "Return on investment",
            f"Across <b>{len(funded):,} funded films</b> with disclosed budget and revenue, "
            f"<b>{profit:.0f}% cleared a gross profit</b> (above the break-even line); median return "
            f"<b>{funded['roi'].median():.1f}×</b>. Budget/revenue are reported mainly for theatrical "
            f"releases — this is the funded subset, not the full catalog."))

        fr = funded[funded["vote_count"].fillna(0) >= 10]
        fig = _style(go.Figure(go.Scattergl(x=fr["budget"], y=fr["vote_average"], mode="markers",
            marker=dict(color=GOLD, size=6, opacity=0.4), text=fr["title"],
            hovertemplate="%{text}<br>budget $%{x:,.0f}<br>rating %{y}<extra></extra>")))
        fig.update_layout(title="Does Spend Buy Ratings?", xaxis_title="Budget ($)",
                          yaxis_title="Vote average", xaxis_type="log")
        c = np.log(fr["budget"]).corr(fr["vote_average"]) if len(fr) > 2 else 0
        blocks.append((fig.to_html(**div), "Spend vs quality",
            f"Budget and audience rating barely move together (r ≈ {c:.2f}) — bigger budgets buy "
            f"spectacle, not scores. Well-rated mid-budget titles are the efficiency play."))

    if "runtime" in df.columns and df["runtime"].notna().any():
        rt = df[(df["runtime"].fillna(0) > 0) & (df["media_type"] == "movie")]
        if len(rt):
            fig = _style(go.Figure(go.Histogram(x=rt["runtime"], nbinsx=30, marker_color=CYAN,
                hovertemplate="%{x} min: %{y} films<extra></extra>")))
            fig.add_vline(x=rt["runtime"].median(), line=dict(color=GOLD, dash="dash"),
                          annotation_text=f"median {rt['runtime'].median():.0f}m", annotation_font_color=GOLD)
            fig.update_layout(title="Film Runtime Distribution", xaxis_title="Runtime (min)", yaxis_title="Films")
            blocks.append((fig.to_html(**div), "Runtime intelligence",
                f"Median film runs <b>{rt['runtime'].median():.0f} minutes</b> across {len(rt):,} titles."))

    if "production_companies" in df.columns and (df["production_companies"].fillna("") != "").any():
        comp = df["production_companies"].fillna("").str.split("|").explode().str.strip()
        comp = comp[comp != ""].value_counts().head(15).sort_values()
        fig = _style(go.Figure(go.Bar(x=comp.values, y=comp.index, orientation="h", marker_color=GREEN,
            hovertemplate="%{y}: %{x} titles<extra></extra>")))
        fig.update_layout(title="Top Production Companies", xaxis_title="Titles")
        blocks.append((fig.to_html(**div), "Who supplies the catalog",
            f"<b>{comp.index[-1]}</b> leads the supplier mix — the production houses behind Netflix-US "
            f"content, a window into the licensing-vs-originals balance."))

    if "keywords" in df.columns and (df["keywords"].fillna("") != "").any():
        kw = df["keywords"].fillna("").str.split("|").explode().str.strip()
        kw = kw[kw != ""].value_counts().head(20).sort_values()
        fig = _style(go.Figure(go.Bar(x=kw.values, y=kw.index, orientation="h", marker_color=GOLD,
            hovertemplate="%{y}: %{x} titles<extra></extra>")), height=560)
        fig.update_layout(title="Top Themes (TMDB keywords)", xaxis_title="Titles")
        blocks.append((fig.to_html(**div), "Theme mining",
            f"Beyond genre, the recurring themes — <b>{kw.index[-1]}</b> tops the keyword index. "
            f"Keywords surface positioning that genre labels miss."))

    return blocks


PAGE = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Netflix Catalog Intelligence — Sierra Napier</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js" charset="utf-8"></script>
<style>
:root{{--ink:#0f1115;--surface:#111827;--border:#1f2d44;--gold:#f59e0b;--cyan:#06b6d4;--text:#f0f0f0;--muted:#94a3b8;}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--ink);color:var(--text);font-family:Inter,sans-serif;line-height:1.6}}
.wrap{{max-width:1000px;margin:0 auto;padding:3rem 1.5rem}}
a{{color:var(--gold);text-decoration:none}}
h1{{font-size:clamp(2rem,5vw,3rem);font-weight:800;background:linear-gradient(135deg,var(--gold),var(--cyan));-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.sub{{color:var(--muted);font-size:1.1rem;margin:.75rem 0 0}}
.stats{{display:flex;gap:2rem;flex-wrap:wrap;margin:2rem 0}}
.stat .v{{font-size:1.8rem;font-weight:800;color:var(--gold);font-family:'JetBrains Mono',monospace}}
.stat .l{{font-size:.8rem;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}}
.method{{background:var(--surface);border:1px solid var(--border);border-left:3px solid var(--cyan);border-radius:10px;padding:1.25rem 1.5rem;margin:2rem 0}}
.method h2{{font-size:1rem;color:var(--cyan);text-transform:uppercase;letter-spacing:.05em;margin-bottom:.75rem}}
.method li{{color:var(--muted);margin:.3rem 0 .3rem 1.2rem;font-size:.95rem}}
.method b{{color:var(--text)}}
.chartcard{{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:1.25rem;margin:1.75rem 0}}
.chartcard h3{{font-size:.8rem;color:var(--gold);text-transform:uppercase;letter-spacing:.06em;margin-bottom:.4rem;font-family:'JetBrains Mono',monospace}}
.analysis{{color:var(--muted);font-size:1rem;margin-top:.9rem;padding-top:.9rem;border-top:1px solid var(--border)}}
.analysis b{{color:var(--text)}}
footer{{color:var(--muted);font-size:.85rem;text-align:center;margin-top:3rem;border-top:1px solid var(--border);padding-top:1.5rem}}
</style></head><body><div class="wrap">
<a href="index.html">← back to portfolio</a>
<h1>Netflix Catalog Intelligence</h1>
<p class="sub">A supply-side analysis of the Netflix-US catalog — self-extracted from TMDB, every figure reproducible. {n:,} titles · extracted {date}.</p>
<div class="stats">{statboxes}</div>
<div class="method"><h2>Methodology</h2><ul>
<li><b>Source:</b> TMDB <code>/discover</code>, filtered to Netflix (<code>with_watch_providers=8</code>, <code>watch_region=US</code>, flatrate). First-party API, not a third-party CSV.</li>
<li><b>Method:</b> paginated discover across movies + series, deduplicated by TMDB id → <b>{n:,} unique titles</b>.</li>
<li><b>Reproducible:</b> re-run <code>fetch_netflix_catalog.py</code> with any TMDB key and you get this dataset. Refreshed weekly via GitHub Actions.</li>
<li><b>Source separation:</b> these charts use the <b>catalog</b> layer only (what Netflix carries). A separate live "trending/top-rated" layer measures demand — the two are never joined.</li>
<li><b>Ratings:</b> TMDB community vote averages; rating charts filter to titles with ≥10 votes to cut noise.</li>
<li><b>Limitation:</b> reflects TMDB's view of Netflix-US availability (sourced via JustWatch), at a point in time — not Netflix's internal catalog.</li>
<li><b>Tools:</b> Python · pandas · Plotly. Zero synthetic records.</li>
</ul></div>
{charts}
<footer>Built by Sierra Napier · data self-extracted from TMDB · <a href="https://github.com/gosidehustlesisi/sierra-business-intelligence">source on GitHub</a><br><span style="font-size:.8rem">This product uses the TMDB API but is not endorsed or certified by TMDB.</span></footer>
</div></body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", default=None,
                    help="defaults to enriched CSV if present, else the base catalog")
    ap.add_argument("--out", default="../../docs/netflix-analysis.html")
    args = ap.parse_args()

    catalog = args.catalog
    if catalog is None:
        enriched = "data/netflix_catalog_enriched.csv"
        catalog = enriched if Path(enriched).exists() else "data/netflix_catalog_latest.csv"
    print(f"  source: {catalog}")
    df = pd.read_csv(catalog)
    date = str(df["extracted_at"].iloc[0])[:10] if "extracted_at" in df else "?"
    rated = df[df["vote_count"].fillna(0) >= 10]
    statdefs = [
        (f"{len(df):,}", "Titles"),
        (f"{100*(df.original_language.fillna('')!='en').mean():.0f}%", "Non-English"),
        (f"{rated['vote_average'].mean():.1f}", "Mean rating"),
        (f"{int(df.dropna(subset=['release_year']).release_year.min())}–{int(df.dropna(subset=['release_year']).release_year.max())}", "Year range"),
    ]
    statboxes = "".join(f'<div class="stat"><div class="v">{v}</div><div class="l">{l}</div></div>' for v, l in statdefs)

    charts = ""
    for chart_html, title, analysis in build(df):
        charts += f'<div class="chartcard"><h3>{title}</h3>{chart_html}<p class="analysis">{analysis}</p></div>\n'

    html = PAGE.format(n=len(df), date=date, statboxes=statboxes, charts=charts)
    Path(args.out).write_text(html)
    print(f"  wrote {args.out} ({len(html)//1024} KB, {len(build(df))} interactive charts)")


if __name__ == "__main__":
    main()
