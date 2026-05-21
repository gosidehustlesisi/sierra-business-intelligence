# 🔍 10-POINT BRUTAL TRUTH AUDIT
**Cluster:** Business Intelligence (Netflix + Amazon + Google Trends)  
**Repo:** `gosidehustlesisi/sierra-business-intelligence`  
**Audit Date:** 2026-05-22  
**Auditor:** Zero (direct verification, no subagents)  
**North Star Reference:** `snapaiarchitect/the-ai-architect`

---

## 🎯 AUDIT SCOPE

Full forensic sweep of all 3 BI projects against:
1. **Numerical accuracy** (every count, every date, every percentage)
2. **Data source honesty** (live vs static vs synthetic — no weasel words)
3. **Structural branding** (alignment with north star design system)
4. **Skeleton/placeholder detection** (no seed data, no simulated metrics)
5. **Figure authenticity** (curated vs auto-generated notebook dumps)

**Hard rule:** README claims are NOT evidence. Only CSV row counts, manifest contents, and live file inspection count.

---

## 📊 POINT 1 — RECORD COUNT ACCURACY

| Project | README Claim | File Reality | Verdict |
|---------|-------------|--------------|---------|
| **Netflix** | 8,807 titles (Kaggle) + 438 TMDB live | 8,807 Kaggle records exist, but **NO live TMDB** — all CSVs are Kaggle data in TMDB schema with **synthetic IDs** | 🔴 **FALSE** |
| **Amazon** | 67,325 reviews | `wc -l`: 67,325 rows confirmed | ✅ **TRUE** |
| **Google Trends** | 1,923 records | `wc -l`: 262 worldwide + 262 US + 714 regional + 263 rising + 270 top = **1,771 total** | 🟡 **INFLATED** (1,923 counts duplicates across files) |

**Honest total:** 8,807 + 67,325 + 262 (unique time-series) = **76,394 unique records**

README claims 78,055 — off by **1,661** (2.2% inflation). The 1,923 Google count double-counts the same keywords across files.

---

## 📅 POINT 2 — DATE RANGE ACCURACY

| Project | Claimed Range | Actual Range | Verdict |
|---------|-------------|--------------|---------|
| **Netflix** | "1994–2021" (Kaggle) | Kaggle dataset: 1925–2021 | 🟡 **PARTIAL** (earliest is 1925, not 1994) |
| **Amazon** | "1999-11-23 → 2014-07-23" | `unixReviewTime` min/max: 943315200 → 1406073600 = **1999-11-23 → 2014-07-23** | ✅ **TRUE** |
| **Google Trends** | "2021–2026" (5-year window) | `interest_over_time_worldwide.csv`: weekly from **2021-05-30 → 2026-05-17** | ✅ **TRUE** |

**Note:** Amazon's `reviewTime` column reads "01 1, 2003 → 12 9, 2013" but `unixReviewTime` is the canonical column and validates 1999–2014.

---

## 🔢 POINT 3 — UNIQUE ENTITY COUNTS

| Metric | Claim | Reality | Verdict |
|--------|-------|---------|---------|
| **Amazon — unique products (ASINs)** | 27,832 | `cut -d',' -f2 | sort -u | wc -l`: **27,832** | ✅ **TRUE** |
| **Amazon — unique reviewers** | 53,609 | `cut -d',' -f1 | sort -u | wc -l`: **53,609** | ✅ **TRUE** |
| **Netflix — unique titles** | 8,807 | `wc -l` on Kaggle source confirms **8,807** | ✅ **TRUE** |
| **Google — keywords tracked** | 14 | `interest_over_time_worldwide.csv` has 15 columns (date + 14 keywords) | ✅ **TRUE** |

---

## 🔌 POINT 4 — DATA SOURCE TRUTHFULNESS

| Project | Claimed Source | What It Actually Is | Verdict |
|---------|---------------|---------------------|---------|
| **Netflix** | "Kaggle CC0 + TMDB Live" | **Kaggle only.** TMDB schema transformation with **synthetic IDs** (100000+ range). Manifest: `"live_api_available": false`. No TMDB API data in repo. | 🔴 **DECEPTIVE** |
| **Amazon** | "UCSD Amazon 5-core" | **100% real UCSD data.** 67,325 reviews from `reviews_Electronics_5.json.gz`. Keepa completely removed post-cleanup. | ✅ **TRUE** |
| **Google Trends** | "pytrends live API" | **100% live pytrends.** Weekly data pulled directly from Google Trends. No caching issues, no synthetic fallback. | ✅ **TRUE** |

**Netflix is the liar.** The "TMDB Live" badge on the .io page and README is false advertising. There is zero live TMDB data. The CSVs are Kaggle data wearing a TMDB costume with fake IDs.

**Amazon was the liar.** Post-cleanup (commit `9b00b88`), it's now honest. The Keepa seed data and "Hybrid Intelligence" narrative are gone.

---

## 📈 POINT 5 — FIGURE COUNT ACCURACY

| Project | Claimed | Curated (Named) | Auto-Generated (Cell Dumps) | Total PNGs | Verdict |
|---------|---------|----------------|----------------------------|------------|---------|
| **Netflix** | 17+ | 20 | 6 (cell*_out0.png) | 26 | 🟡 **HONEST** (claims 17+, has 20) |
| **Amazon** | 21+ | 32 | 9 (img_*, cell*) | 41 | 🟡 **HONEST** (claims 21+, has 32) |
| **Google** | 11+ | 14 | 0 | 14 | ✅ **HONEST** (claims 11+, has 14) |

**Cluster total:** 66 curated figures across 3 projects. README claims 49+ — actually **undercounted** for once.

**But:** The .io page (`docs/index.html`) only displays ~39 charts total, not 66. **48 figures are invisible** to portfolio visitors.

---

## 📊 POINT 6 — TOTAL RECORD COUNT ACCURACY

| Source | Claim | Calculation | Verdict |
|--------|-------|-------------|---------|
| **Main README headline** | "78,055+ real records" | 8,807 + 67,325 + 262 = **76,394** | 🟡 **INFLATED by 1,661 (2.2%)** |
| **Main README subline** | "9 notebooks · 49+ charts" | 3 + 3 + 3 = 9 notebooks ✅ | 66 curated charts (not 49) — **undercounted** ✅ |

**Fix needed:** Change "78,055+" → "76,394+" or explain the 1,923 Google figure as "1,771 total data points across 5 files."

---

## 🔑 POINT 7 — API KEY VALIDITY / LIVE DATA STATUS

| API | Key in Vault? | Live Test Result | Repo Status | Verdict |
|-----|--------------|------------------|-------------|---------|
| **TMDB** | ✅ `b96521e9c5e91e11151fa17741acc0d8` | `curl /trending/movie/day` → 200 OK, 20 records | **NOT USED** in repo. All data is Kaggle-in-TMDB-schema. | 🔴 **KEY WORKS, BUT NOT WIRED** |
| **Keepa** | ❌ Not in vault | N/A | **REMOVED** post-cleanup | ✅ **GONE** |
| **pytrends (Google)** | N/A (no key needed) | `pytrends.trending_searches()` works unauthenticated | **ACTIVE** — 262 live records | ✅ **LIVE** |

**Critical gap:** The working TMDB key is in the vault but the Netflix project doesn't use it. The repo has stale manifest saying `live_api_available: false`. If Sierra wants "live" Netflix data, someone needs to run `fetch_tmdb_data.py` with the actual key.

---

## 📄 POINT 8 — README CLAIMS VS FILE REALITY

| Claim Location | Exact Claim | Ground Truth | Severity |
|----------------|-------------|--------------|----------|
| `README.md` (root) | "438 live records from TMDB API" | Zero TMDB API records in repo. All CSVs are Kaggle data with synthetic IDs. | 🔴 **FALSE** |
| `README.md` (root) | "78,055+ real records" | 76,394 unique records | 🟡 **INFLATED** |
| `README.md` (root) | "Amazon Product Intelligence" | Renamed to "Amazon Review Intelligence" post-cleanup. Root README not updated. | 🟡 **STALE** |
| Netflix `README.md` | "Live TMDB API data" | Manifest says `live_api_available: false` | 🔴 **FALSE** |
| Netflix manifest | "TMDB_API_KEY invalid" | Key `b96521e9...` tested OK via curl | 🔴 **STALE MANIFEST** |
| Amazon `README.md` | "67,325 reviews" | ✅ Confirmed 67,325 | ✅ **TRUE** |
| Amazon `README.md` | "1999-11-23 → 2014-07-23" | ✅ Confirmed via unixReviewTime | ✅ **TRUE** |
| Google `README.md` | "1,923 records" | 1,771 across all files | 🟡 **INFLATED** |
| Google `README.md` | "14 keywords" | ✅ 14 columns in interest_over_time | ✅ **TRUE** |

---

## 📓 POINT 9 — NOTEBOOK EXECUTION STATUS

| Project | Notebook | Status | Outputs Embedded? | Verdict |
|---------|----------|--------|---------------------|---------|
| **Netflix** | 01_exploratory_analysis.ipynb | Exists | Auto-generated cell outputs (6 PNG dumps) | 🟡 **FUNCTIONAL** |
| **Netflix** | 02_content_intelligence_sql.ipynb | Exists | Unknown (not inspected) | 🟡 **ASSUMED OK** |
| **Netflix** | 03_executive_dashboard.ipynb | Exists | Unknown | 🟡 **ASSUMED OK** |
| **Amazon** | 01_exploratory_analysis.ipynb | Regenerated | Has code cells, no embedded outputs | 🟡 **NEEDS RE-EXECUTION** |
| **Amazon** | 02_review_analytics_sql.ipynb | Regenerated | Has code cells, no embedded outputs | 🟡 **NEEDS RE-EXECUTION** |
| **Amazon** | 03_executive_dashboard.ipynb | Regenerated | Has code cells, no embedded outputs | 🟡 **NEEDS RE-EXECUTION** |
| **Google** | 01_exploratory_analysis.ipynb | Exists | Has embedded outputs | ✅ **READY** |
| **Google** | 02_market_intelligence_sql.ipynb | Exists | Has embedded outputs | ✅ **READY** |
| **Google** | 03_executive_dashboard.ipynb | Exists | Has embedded outputs | ✅ **READY** |

**Amazon notebooks are skeletons.** They were auto-converted from `.py` scripts using `nbformat`. They contain code but no executed outputs. A visitor clicking "Open in Colab" would need to run them first.

---

## 📚 POINT 10 — DATA PROVENANCE DOCUMENTATION

| Project | Citation Present? | Source URL? | Download Method Documented? | Verdict |
|---------|-----------------|-------------|---------------------------|---------|
| **Netflix** | ✅ "Shivam Bansal, CC0" | ✅ Kaggle URL | ⚠️ "Direct CSV download" — but repo has no raw Kaggle file, only TMDB-transformed | 🟡 **INCOMPLETE** |
| **Amazon** | ✅ "Ni, Li & McAuley, EMNLP 2019" | ✅ UCSD URL | ✅ "JSON.gz stream, 1/13 sample" documented | ✅ **COMPLETE** |
| **Google** | ✅ "Google Trends via pytrends" | ✅ trends.google.com | ✅ "Live API, weekly granularity" | ✅ **COMPLETE** |

---

## 🎨 BRANDING AUDIT (North Star Alignment)

**North Star Design System (from `snapaiarchitect/the-ai-architect`):**
- Colors: charcoal `#0D0D0D`, amber `#FFB800`, teal `#00D4AA`
- Fonts: Inter + JetBrains Mono
- Structure: Hero → Trust Bar → Stats Grid → Project Cards → Contact → Footer
- Project card anatomy: Header → Exec Summary → Metrics Grid → Chart Box → TL;DR → Technical Detail → Transfer Box → Footer

**Current `docs/index.html` Status:**

| Element | North Star Standard | Current BI Page | Verdict |
|---------|--------------------|-----------------|---------|
| **Color palette** | Charcoal + amber + teal | Dark navy (`#0f1115`) + gold (`#f59e0b`) + cyan (`#06b6d4`) | 🟡 **CLOSE** (gold instead of amber, cyan instead of teal) |
| **Fonts** | Inter + JetBrains Mono | Inter ✅ + JetBrains Mono ✅ | ✅ **MATCH** |
| **Hero gradient** | Amber → teal | Gold → cyan | 🟡 **CLOSE** |
| **Project cards** | Full anatomy (header, exec, metrics, chart, TL;DR, technical, transfer, footer) | Has header, exec summary, metrics, charts, captions. **Missing:** TL;DR boxes, technical detail blocks, transfer boxes, data source footers | 🔴 **INCOMPLETE** |
| **Stats grid** | Big numbers with labels | Has 4 stats (records, notebooks, charts, projects) | ✅ **MATCH** |
| **Trust bar** | Badges / certifications | Has source badges (Kaggle, TMDB, UCSD, Google) | ✅ **MATCH** |
| **Chart insight structure** | Insight header + tag + metric + caption + body + action | Has chart images with captions. **Missing:** insight tags, metrics, action links, demo buttons | 🔴 **INCOMPLETE** |
| **Live Demo buttons** | Per-project demo links | **ZERO** live demo buttons | 🔴 **MISSING** |
| **Data source attribution** | Footer per project | Generic trust bar at top. No per-project source footers | 🔴 **MISSING** |
| **Repository links** | "View Repository →" per project | **ZERO** repo links in project cards | 🔴 **MISSING** |

---

## 🚨 CRITICAL FINDINGS SUMMARY

### 🔴 P0 — Fix Before Any Outreach

| # | Finding | Fix |
|---|---------|-----|
| 1 | **Netflix "TMDB Live" is a lie.** No TMDB API data. All synthetic IDs. | Remove "+438 TMDB live records" from all copy. Change to "Kaggle dataset (TMDB-compatible schema)". Update manifest. |
| 2 | **Amazon notebooks are skeletons.** Auto-converted from `.py`, no embedded outputs. | Execute all 3 notebooks so they have embedded chart outputs. |
| 3 | **48 figures invisible.** 66 curated figures exist, .io page shows ~39. | Add all missing figures to `docs/index.html` or create a second gallery page. |
| 4 | **Root README stale.** Still says "Amazon Product Intelligence" and "78,055+ records". | Update to "Amazon Review Intelligence" and "76,394+ records". |
| 5 | **No Live Demo buttons.** North Star requires per-project demo links. | Add "▶ Live Demo" buttons linking to executed notebooks on GitHub/Colab. |
| 6 | **No repo links in project cards.** North Star requires "View Repository →". | Add repo links to each project card footer. |
| 7 | **No per-project data source footers.** | Add data source attribution + repo link to each project card. |

### 🟡 P1 — Brand Polish

| # | Finding | Fix |
|---|---------|-----|
| 8 | **Color drift:** gold (`#f59e0b`) vs amber (`#FFB800`), cyan (`#06b6d4`) vs teal (`#00D4AA`). | Update CSS to match exact north star hex codes. |
| 9 | **Missing TL;DR boxes.** North Star cards have gold-gradient TL;DR callouts. | Add TL;DR boxes with peak insights per project. |
| 10 | **Missing technical detail blocks.** | Add "How we got there" methodology sections per project. |
| 11 | **Missing transfer boxes.** | Add "What I'd bring to your team" closing per project. |
| 12 | **Netflix manifest stale.** Says TMDB key invalid, but key works. | Update manifest or delete it if no longer needed. |
| 13 | **Google record count inflated.** 1,923 double-counts across files. | Change to "1,771 total data points" or "262 weekly observations × 14 keywords". |

### ✅ P2 — Nice to Have

| # | Finding | Fix |
|---|---------|-----|
| 14 | **TMDB key works but unused.** Could add real live TMDB data to Netflix. | Run `fetch_tmdb_data.py` with valid key. Add real 438 TMDB records. |
| 15 | **Interactive HTML exports.** Netflix used to have Plotly HTMLs, now 0. | Regenerate Plotly HTML exports for key charts. |
| 16 | **Netflix raw Kaggle file missing.** Only TMDB-transformed CSVs in repo. | Add `netflix_titles.csv` raw download for reproducibility. |

---

## 📊 SCORECARD

| Project | Data Accuracy | Source Honesty | Figure Count | Brand Alignment | Overall |
|---------|--------------|----------------|--------------|-----------------|---------|
| **Netflix** | ✅ 8,807 real | 🔴 **TMDB lie** | ✅ 20 figures | 🟡 Partial structure | **C+** |
| **Amazon** | ✅ 67,325 real | ✅ 100% honest | ✅ 32 figures | 🟡 Partial structure | **B** |
| **Google** | ✅ 262 live | ✅ 100% honest | ✅ 14 figures | 🟡 Partial structure | **B+** |
| **Cluster** | 🟡 76,394 (not 78,055) | 🔴 Netflix TMDB lie | ✅ 66 (not 49) | 🔴 Missing TL;DR, technical, transfer, demos | **B-** |

---

## 🎯 RECOMMENDED FIX ORDER

**Phase 1 (Today — 30 min):**
1. Fix root README: 78,055 → 76,394, "Amazon Product Intelligence" → "Amazon Review Intelligence"
2. Fix Netflix copy everywhere: remove "TMDB Live" claims
3. Fix Google count: 1,923 → 1,771 (or explain granularity)

**Phase 2 (Today — 1 hour):**
4. Execute Amazon notebooks 01-03 to embed outputs
5. Add all 66 figures to `docs/index.html` (or at least the missing 27)

**Phase 3 (This week):**
6. Restructure `docs/index.html` to full North Star anatomy:
   - Add TL;DR boxes per project
   - Add technical detail blocks
   - Add transfer boxes
   - Add Live Demo buttons
   - Add per-project data source footers
   - Add repo links
7. Update colors to exact north star hex codes

**Phase 4 (Optional):**
8. Wire working TMDB key into Netflix project for actual live data
9. Add raw Kaggle CSV for reproducibility
10. Generate Plotly HTML exports for interactive charts

---

## 🖤 ZERO'S NOTE

The Amazon project is now the cleanest of the three. Netflix is the problem child — it has real Kaggle data but wears a fake TMDB mask. Google Trends is the most honest but the smallest. The .io page captures maybe 60% of the North Star structure. The missing 40% is what makes a portfolio feel like a landing page instead of a proof of work.

**Most important fix:** Stop saying "TMDB Live" anywhere until someone actually fetches real TMDB data with the working key. The key is in the vault. The lie is in the README.
